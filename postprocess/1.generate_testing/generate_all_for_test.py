import pandas as pd
import click
import os
from os.path import join, basename
from itertools import combinations
from tqdm import tqdm


@click.command()
@click.option("--out_dir", required=True)
@click.option("--ds_info_csv", required=True)
def main(out_dir, ds_info_csv):
    all_pairs = []
    dataset = basename(ds_info_csv).split(".")[0].split("_")[1].removeprefix("Dataset-")
    df = pd.read_csv(ds_info_csv)
    for (idx1, row1), (idx2, row2) in tqdm(
        combinations(df.iterrows(), 2), total=len(df) * (len(df) - 1) // 2
    ):
        all_pairs.append(
            {
                "idb_path_1": row1["idb_path"],
                "fva_1": row1["fva"],
                "idx_1": idx1,
                "idb_path_2": row2["idb_path"],
                "fva_2": row2["fva"],
                "idx_2": idx2,
                "db_type": "XM",
                "func_name_1": row1["func_name"],
                "func_name_2": row2["func_name"],
            }
        )

    os.makedirs(out_dir, exist_ok=True)
    all_df = pd.DataFrame(all_pairs)
    all_df_path = join(out_dir, f"all-xm_Ds{dataset}.csv")
    all_df.to_csv(all_df_path)
    print(f"Saved {all_df_path}")


if __name__ == "__main__":
    main()
