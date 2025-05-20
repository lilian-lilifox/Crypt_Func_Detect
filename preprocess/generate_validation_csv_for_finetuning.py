import pandas as pd
from os.path import join

DB_DIR = "DBs"
INPUT = join(DB_DIR, "Dataset-Finetuning/validation_Dataset-Finetuning.csv")
OUTPUT = join(DB_DIR, "Dataset-Finetuning/pairs/validation/validation_functions.csv")

df = pd.read_csv(INPUT, index_col=0)

# This script tried another way for grouping.
# It suggests that the same crypto algorithm should be in the same group.
# Notice: This will lead to bad model performance, as we tested!!!
# See also model/core/graph_factory_training.py _select_random_function_pairs()
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


def get_crypto(str):
    str = str.lower()
    for keyword in crypto_keywords:
        if keyword in str:
            return keyword
    return None


crypto2groupid = {}
counter = 0
groups = []

for idx, r in df.iterrows():
    crypto = get_crypto(r["func_name"])
    if not crypto in crypto2groupid.keys():
        crypto2groupid[crypto] = counter
        counter += 1
    groups.append(crypto2groupid[crypto])

df = df[["idb_path", "fva", "func_name"]]
df.insert(2, "group", groups)
df = df.rename(columns={"idb_path": "idb"})

df.to_csv(OUTPUT)
