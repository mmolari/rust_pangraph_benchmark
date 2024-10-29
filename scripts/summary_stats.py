import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser(description="Load multiple JSON summary files and plot summary statistics.")
    parser.add_argument("--logfiles", type=str, nargs='+', required=True, help="Paths to JSON summary files.")
    parser.add_argument("--fig_file", type=str, required=True, help="output figure file")
    parser.add_argument("--fig_file_log", type=str, required=True, help="output figure file (log scale)")
    parser.add_argument("--out_csv", type=str, required=True, help="output csv summary dataframe")
    args = parser.parse_args()
    return args

def assign_type(df):
    df["type"] = "rust"
    mask = df["Command"].str.startswith("pangraph build")
    df.loc[mask, "type"] = "julia"
    mask = df["Command"].str.contains("--verify")
    df.loc[mask, "type"] = "verify"

    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass

    df["User time (minutes)"] = df["User time (seconds)"] / 60
    df["System time (minutes)"] = df["System time (seconds)"] / 60
    df["Maximum resident set size (Gb)"] = df["Maximum resident set size (kbytes)"] / 1024 / 1024
    df["Wall clock time (minutes)"] = pd.to_timedelta("00:" + df["Elapsed (wall clock) time"]).dt.total_seconds() / 60
    return df


def load_json_files(json_files):
    data = []
    for file in json_files:
        with open(file, 'r') as f:
            data.append(json.load(f))
    return pd.DataFrame(data)

def create_plots(df, fig_file, logscale=False):

    def subpanel(y, ax):
        sns.lineplot(data=df, x="fasta file count", hue="type", y=y, ax=ax, marker=".")

    fig, axs = plt.subplots(2,3, figsize=(10, 6), sharex=True)

    subpanel(y="User time (minutes)", ax=axs[0,0])
    subpanel(y="System time (minutes)", ax=axs[0,1])
    subpanel(y="Percent of CPU this job got", ax=axs[0,2])
    subpanel(y="Wall clock time (minutes)", ax=axs[1,0])
    subpanel(y="Maximum resident set size (Gb)", ax=axs[1,1])
    subpanel(y="graph file size (Mb)", ax=axs[1,2])

    if logscale:
        for ax in axs.flatten():
            ax.set_xscale("log")
            ax.set_yscale("log")

    sns.despine()
    plt.tight_layout()
    plt.savefig(fig_file, dpi=200)
    plt.close()

def save_dataframe(df, fname):

    selected_cols = [
        "type",
        "fasta file count",
        "User time (minutes)",
        "System time (minutes)",
        "Percent of CPU this job got",
        "Wall clock time (minutes)",
        "Maximum resident set size (Gb)",
        "graph file size (Mb)",
    ]
    sdf = df[selected_cols].copy()
    sdf.sort_values(selected_cols[:2], inplace=True)
    sdf.to_csv(fname, index=False)



def main():
    args = parse_args()

    # Load JSON files into a DataFrame
    df = load_json_files(args.logfiles)
    assign_type(df)

    print("Data loaded into DataFrame:")
    print(df)

    print(f"creating plots and saving in {args.fig_file}")
    create_plots(df, args.fig_file, logscale=False)
    create_plots(df, args.fig_file_log, logscale=True)

    print(f"save dataframe to {args.out_csv}")
    save_dataframe(df, args.out_csv)

if __name__ == "__main__":
    main()