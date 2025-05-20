import pandas as pd
import click
from tqdm import tqdm


@click.command()
@click.option("--ds_info_csv", required=True)
@click.option("--pairs_csv", required=True)
def main(ds_info_csv, pairs_csv):
    output_path = pairs_csv[:-4] + "_with_idx.csv"
    df = pd.read_csv(ds_info_csv)
    pairs = pd.read_csv(pairs_csv, index_col=0)

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        pairs.loc[
            (pairs["idb_path_1"] == row["idb_path"])
            & (pairs["func_name_1"] == row["func_name"]),
            "idx_1",
        ] = idx
        pairs.loc[
            (pairs["idb_path_2"] == row["idb_path"])
            & (pairs["func_name_2"] == row["func_name"]),
            "idx_2",
        ] = idx

    pairs["idx_1"] = pairs["idx_1"].astype(int)
    pairs["idx_2"] = pairs["idx_2"].astype(int)
    pairs.to_csv(output_path)


if __name__ == "__main__":
    main()
