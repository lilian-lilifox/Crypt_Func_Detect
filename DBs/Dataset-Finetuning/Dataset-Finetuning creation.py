import json
import numpy as np
import os
import pandas as pd
import random
from collections import defaultdict

from tqdm import tqdm

flowchart = pd.read_csv("features/flowchart_Dataset-Finetuning.csv")
del flowchart["bb_list"]
flowchart = flowchart[flowchart["bb_num"] >= 5]
flowchart.drop_duplicates("hashopcodes", keep="first", inplace=True)

x86_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/x86/")]["idb_path"].unique().tolist()
)
arm32_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/arm32/")]["idb_path"]
    .unique()
    .tolist()
)
arm64_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/arm64/")]["idb_path"]
    .unique()
    .tolist()
)
mips32_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/mips32/")]["idb_path"]
    .unique()
    .tolist()
)

architecture_map = {
    "x86": x86_idb_path_list,
    "arm32": arm32_idb_path_list,
    "arm64": arm64_idb_path_list,
    "mips32": mips32_idb_path_list,
}

crypto_keywords = [
    "aes",
    "des",
    "rc4",
    "sha",
    "md5",
    "hmac",
    "hash",
    "cbc",
    "ecb",
    "rsa",
    "dsa",
    "ecdsa",
    "curve",
    "poly1305",
    "chacha",
]
pattern = r"(" + "|".join(crypto_keywords) + r")"

df = flowchart[
    (~flowchart["func_name"].str.contains("sub_"))
    & (flowchart["func_name"].str.contains(pattern, case=False, na=False, regex=True))
].copy()
df = df[
    df["func_name"].isin(
        df["func_name"].value_counts()[df["func_name"].value_counts() > 1].index
    )
]
crypt_funcs_list = df["func_name"].unique().tolist()

keyword_counts = {
    keyword: df["func_name"].str.contains(keyword, case=False).sum()
    for keyword in crypto_keywords
}
counts_df = pd.DataFrame(list(keyword_counts.items()), columns=["Keyword", "Count"])
print(counts_df.sort_values(by="Count", ascending=False))

# Shuffle by function name
unique_func_names = df["func_name"].unique()
shuffled_func_names = (
    pd.Series(unique_func_names)
    .sample(frac=1, random_state=459657)
    .reset_index(drop=True)
)

# Calculate split sizes based on the number of unique function names
n_total_funcs = len(shuffled_func_names)
n_test_funcs = int(n_total_funcs * 0.2)
n_validation_funcs = int(n_total_funcs * 0.2)
n_train_funcs = n_total_funcs - n_validation_funcs - n_test_funcs

# Split function names
train_funcs = shuffled_func_names[:n_train_funcs]
test_funcs = shuffled_func_names[n_train_funcs : n_train_funcs + n_test_funcs]
validation_funcs = shuffled_func_names[n_train_funcs + n_test_funcs :]

# Create dataframes for each set
df_training = df[df["func_name"].isin(train_funcs)].reset_index(drop=True)
df_testing = df[df["func_name"].isin(test_funcs)].reset_index(drop=True)
df_validation = df[df["func_name"].isin(validation_funcs)].reset_index(drop=True)

# Check the result
print(f"Training size: {len(df_training)}")
print(f"Testing size: {len(df_testing)}")
print(f"Validation size: {len(df_validation)}")

selected_columns = ["idb_path", "fva", "func_name"]


def generate_pairs(fl):
    comparison_list = list()

    for arch, data in architecture_map.items():
        print(f"Processing {arch} architecture.")
        for source_func in tqdm(crypt_funcs_list):
            for source_path in data:
                left_row = fl[
                    (fl["idb_path"] == source_path) & (fl["func_name"] == source_func)
                ]
                if left_row.empty:
                    continue
                left = list(left_row[selected_columns].values[0])

                right_index = fl[
                    (fl["idb_path"].str.contains(f"/{arch}/"))
                    & (fl["func_name"].isin(crypt_funcs_list))
                ].index
                for index in right_index:
                    right = list(fl.loc[index, selected_columns].values)
                    comparison_list.append(left + right)

    print("All done!!")
    print(f"Total: {len(comparison_list)}.")

    # Create a new DataFrame
    columns = [x + "_1" for x in selected_columns] + [
        x + "_2" for x in selected_columns
    ]
    df = pd.DataFrame(comparison_list, columns=columns)

    # Add the db_type column
    df["db_type"] = ["XM"] * df.shape[0]

    # Sort the rows
    df.sort_values(by=["idb_path_1", "fva_1", "idb_path_2", "fva_2"], inplace=True)
    df.reset_index(inplace=True, drop=True)

    # Paranoid check
    df.drop_duplicates(inplace=True)
    df.reset_index(inplace=True, drop=True)

    return df


print("Generating Training pairs:")
pairs_training = generate_pairs(df_training)
print("Generating Testing pairs:")
pairs_testing = generate_pairs(df_testing)
print("Generating Validation pairs:")
pairs_validation = generate_pairs(df_validation)


def create_similarity_pairs(df_input, neg_for_pos=100):
    def extract_keywords(func_name):
        func_name = str(func_name).lower()
        return set([kw for kw in crypto_keywords if kw in func_name])

    def has_common_crypto_keyword(row):
        kw1 = extract_keywords(row["func_name_1"])
        kw2 = extract_keywords(row["func_name_2"])
        return len(kw1 & kw2) > 0

    def no_common_crypto_keyword(row):
        kw1 = extract_keywords(row["func_name_1"])
        kw2 = extract_keywords(row["func_name_2"])
        return len(kw1 & kw2) == 0

    df_pos = df_input[df_input.apply(has_common_crypto_keyword, axis=1)].copy()
    df_neg = df_input[df_input.apply(no_common_crypto_keyword, axis=1)].copy()

    if len(df_pos) * neg_for_pos > len(df_neg):
        num_neg = len(df_neg)
        num_pos = len(df_neg) // neg_for_pos
        df_pos = df_pos.sample(frac=1, random_state=837465).reset_index(drop=True)[
            :num_pos
        ]
    else:
        num_pos = len(df_pos)
        num_neg = len(df_pos) * neg_for_pos
        df_neg = df_neg.sample(frac=1, random_state=837465).reset_index(drop=True)[
            :num_neg
        ]

    return df_pos, df_neg


# training: 61467 399628
df_pos_training, df_neg_training = create_similarity_pairs(pairs_training)
# testing: 7139 40696
df_pos_testing, df_neg_testing = create_similarity_pairs(pairs_testing)
# validation: 7006 41444
df_pos_validation, df_neg_validation = create_similarity_pairs(pairs_validation)

print("Counts of pos and neg pairs:")
print("Training", len(df_pos_training), len(df_neg_training))
print("Testing", len(df_pos_testing), len(df_neg_testing))
print("Validation", len(df_pos_validation), len(df_neg_validation))

print("[D] Converting the positive/negative pairs into CSV...", flush=True)

df_pos_training.to_csv("pairs/training/pos-training-Finetuning.csv")
df_pos_testing.to_csv("pairs/testing/pos-testing-Finetuning.csv")
df_pos_validation.to_csv("pairs/validation/pos-validation-Finetuning.csv")
df_neg_training.to_csv("pairs/training/neg-training-Finetuning.csv")
df_neg_testing.to_csv("pairs/testing/neg-testing-Finetuning.csv")
df_neg_validation.to_csv("pairs/validation/neg-validation-Finetuning.csv")

print("Done!!")


def filter_functions_in_pairs(df_input, pairs_df):
    pair_funcs = set(
        list(zip(pairs_df["idb_path_1"], pairs_df["func_name_1"]))
        + list(zip(pairs_df["idb_path_2"], pairs_df["func_name_2"]))
    )

    df_filtered = df_input[
        df_input.apply(
            lambda row: (row["idb_path"], row["func_name"]) in pair_funcs, axis=1
        )
    ].copy()

    return df_filtered


df_training = filter_functions_in_pairs(
    df_training, pd.concat([df_pos_training, df_neg_training], ignore_index=True)
)
df_testing = filter_functions_in_pairs(
    df_testing, pd.concat([df_pos_testing, df_neg_testing], ignore_index=True)
)
df_validation = filter_functions_in_pairs(
    df_validation, pd.concat([df_pos_validation, df_neg_validation], ignore_index=True)
)

# Check the result
print(f"Training size: {len(df_training)}")
print(f"Testing size: {len(df_testing)}")
print(f"Validation size: {len(df_validation)}")

print("[D] Converting Dataset into CSV...", flush=True)

df_training.to_csv("training_Dataset-Finetuning.csv")
df_testing.to_csv("testing_Dataset-Finetuning.csv")
df_validation.to_csv("validation_Dataset-Finetuning.csv")

print("Done!!")

# Save the "selected functions" to a JSON.
# This is useful to limit the IDA analysis to some functions only.
df_list = [df_training, df_validation, df_testing]
split_list = ["training", "validation", "testing"]

for split, df_t in zip(split_list, df_list):
    fset = set([tuple(x) for x in df_t[["idb_path", "fva"]].values])
    print("{}: {} functions".format(split, len(fset)))

    selected_functions = defaultdict(list)
    for t in fset:
        selected_functions[t[0]].append(int(t[1], 16))

    # Test
    assert sum([len(v) for v in selected_functions.values()]) == len(fset)

    # Save to file
    with open(
        os.path.join(
            "features", split, "selected_{}_Dataset-Finetuning.json".format(split)
        ),
        "w",
    ) as f_out:
        json.dump(selected_functions, f_out)

print("All done!!")
