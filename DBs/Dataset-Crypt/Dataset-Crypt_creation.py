import json
import pandas as pd
from tqdm import tqdm

flowchart = pd.read_csv("features/flowchart_Dataset-Crypt.csv")

# To filter out short functions(if needed)
flowchart = flowchart[flowchart["bb_num"] >= 0]

source_x86_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/x86/")]["idb_path"].unique().tolist()
)
source_arm32_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/arm32/")]["idb_path"]
    .unique()
    .tolist()
)
source_arm64_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/arm64/")]["idb_path"]
    .unique()
    .tolist()
)
source_mips32_idb_path_list = (
    flowchart[flowchart["idb_path"].str.contains("/mips32/")]["idb_path"]
    .unique()
    .tolist()
)
target_x86_idb_path_list = (
    flowchart[
        flowchart["idb_path"].str.contains("/vul/")
        & flowchart["idb_path"].str.contains("x86")
    ]["idb_path"]
    .unique()
    .tolist()
)
target_arm32_idb_path_list = (
    flowchart[
        flowchart["idb_path"].str.contains("/vul/")
        & flowchart["idb_path"].str.contains("arm32")
    ]["idb_path"]
    .unique()
    .tolist()
)
target_arm64_idb_path_list = (
    flowchart[
        flowchart["idb_path"].str.contains("/vul/")
        & flowchart["idb_path"].str.contains("arm64")
    ]["idb_path"]
    .unique()
    .tolist()
)
target_mips32_idb_path_list = (
    flowchart[
        flowchart["idb_path"].str.contains("/vul/")
        & flowchart["idb_path"].str.contains("mips32")
    ]["idb_path"]
    .unique()
    .tolist()
)

architecture_map = {
    "x86": {
        "source": source_x86_idb_path_list,
        "target": target_x86_idb_path_list,
    },
    "arm32": {
        "source": source_arm32_idb_path_list,
        "target": target_arm32_idb_path_list,
    },
    "arm64": {
        "source": source_arm64_idb_path_list,
        "target": target_arm64_idb_path_list,
    },
    "mips32": {
        "source": source_mips32_idb_path_list,
        "target": target_mips32_idb_path_list,
    },
}

crypto_keywords = [
    "aes",
    "des",
    "rc4",
    "rc5",
    "rc6",
    "sha",
    "md5",
    "hmac",
    "hash",
    "cbc",
    "ecb",
    "crypt",
    "rsa",
    "dsa",
    "ecdsa",
    "curve",
    "poly1305",
    "chacha",
    "cipher",
    "sign",
    "verify",
    "digest",
    "tls",
    "ssl",
]

flowchart_with_func_name = flowchart[
    (~flowchart["func_name"].str.contains("sub_"))
    & flowchart["idb_path"].str.contains("/x86/|/arm32/|/arm64/|/mips32/")
].copy()
flowchart_with_func_name["func_name_lower"] = flowchart_with_func_name[
    "func_name"
].str.lower()

crypt_funcs = flowchart_with_func_name[
    flowchart_with_func_name["func_name_lower"].apply(
        lambda x: any(k in x for k in crypto_keywords)
    )
]
crypt_funcs_list = crypt_funcs["func_name"].unique().tolist()

selected_columns = ["idb_path", "fva", "func_name", "hashopcodes"]

# Store the new function pairs
comparison_list = list()

# Iterate over each architecture of the vul test
for arch, data in architecture_map.items():
    print(f"Processing {arch} architecture.")
    # Iterate over each function in the list
    for source_func in tqdm(crypt_funcs_list):
        # Iterate over the selected binaries
        for source_path in data["source"]:
            # Select the source function
            left_row = flowchart[
                (flowchart["idb_path"] == source_path)
                & (flowchart["func_name"] == source_func)
            ]
            if left_row.empty:
                continue
            left = list(left_row[selected_columns].values[0])

            # Iterate over the target functions
            right_indexes = flowchart[flowchart["idb_path"].isin(data["target"])].index
            for index in right_indexes:
                right = list(flowchart.loc[index, selected_columns].values)
                comparison_list.append(left + right)

print("All done!!")

# Create a new DataFrame
columns = [x + "_1" for x in selected_columns] + [x + "_2" for x in selected_columns]
testing = pd.DataFrame(comparison_list, columns=columns)

# Add the db_type column
testing["db_type"] = ["XM"] * testing.shape[0]

# Sort the rows
testing.sort_values(by=["idb_path_1", "fva_1", "idb_path_2", "fva_2"], inplace=True)
testing.reset_index(inplace=True, drop=True)

# Check that the hashopcodes of the functions to compare are different
for i, row in testing.iterrows():
    if row["hashopcodes_1"] == row["hashopcodes_2"]:
        print("MATCH!")
        print(row)

# Paranoid check
testing.drop_duplicates(inplace=True)
testing.reset_index(inplace=True, drop=True)

# Remove hashopcodes columns
del testing["hashopcodes_1"]
del testing["hashopcodes_2"]

# Save the DataFrame to file
testing.to_csv("pairs/pairs_testing_Dataset-Crypt.csv")

# Save the "selected functions" to a JSON.
# This is useful to limit the IDA analysis to some functions only.

testing_functions = set([tuple(x) for x in testing[["idb_path_1", "fva_1"]].values])
testing_functions |= set([tuple(x) for x in testing[["idb_path_2", "fva_2"]].values])
print("Found {} unique functions".format(len(testing_functions)))

from collections import defaultdict

selected_functions = defaultdict(list)
for t in testing_functions:
    selected_functions[t[0]].append(int(t[1], 16))

# Test
assert sum([len(v) for v in selected_functions.values()]) == len(testing_functions)

# Save to file
with open("features/selected_Dataset-Crypt.json", "w") as f_out:
    json.dump(selected_functions, f_out)

# Save the "selected functions" to a CSV.
# This will be useful to post-process the results.

# Remove from flowchart the functions that are not used for the testing
dataset = flowchart.copy()
del dataset["bb_list"]
del_list = list()
for i, row in dataset.iterrows():
    if not tuple([row["idb_path"], row["fva"]]) in testing_functions:
        del_list.append(i)
dataset.drop(del_list, inplace=True)
dataset.reset_index(inplace=True, drop=True)
print(dataset.shape)

# Save to file
dataset.to_csv("testing_Dataset-Crypt.csv")
