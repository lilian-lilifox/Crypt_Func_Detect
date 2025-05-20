import click
import os
import pickle
import pandas as pd

from recall_mrr import compute_pair_sims


def compute_for_one_task(pair_csv, in_dir, pkl_fp):
    all_testing_fn = os.path.basename(pair_csv)
    assert all_testing_fn.endswith(".csv")
    assert pkl_fp is not None and os.path.exists(pkl_fp), (
        f"Failed to find pkl data: {pkl_fp}"
    )
    df_testing = pd.read_csv(pair_csv, index_col=0)
    with open(pkl_fp, "rb") as f:
        pkl_data = pickle.load(f)
    print(f"Loaded: {pkl_fp}")
    sims = compute_pair_sims(df_testing, pkl_data)
    df_testing["sim"] = sims
    df_testing.to_csv(
        os.path.join(in_dir, all_testing_fn)[:-4] + "_sim.csv", index=False
    )


@click.command()
@click.option(
    "--pair_csv_or_dir",
    required=True,
    help="Path to the CSV or directory containing the pairs.",
)
@click.option(
    "--target_dir", required=True, help="Path to the output target directory."
)
@click.option("--pkl_fp", required=True, help="Path to the pickle file.")
def main(pair_csv_or_dir, target_dir, pkl_fp):
    if os.path.isdir(pair_csv_or_dir):
        print(f"[D]: Collect results of all tasks in {pair_csv_or_dir}. ")
        # TODO
        # collect_for_all_tasks(all_pair_csv_or_dir, target_dir)
    elif os.path.exists(pair_csv_or_dir):
        print(f"[D]: Collect for the task {pair_csv_or_dir}. ")
        compute_for_one_task(pair_csv_or_dir, target_dir, pkl_fp)
    else:
        print(f"Error: {pair_csv_or_dir} does not exists. ")


if __name__ == "__main__":
    main()
