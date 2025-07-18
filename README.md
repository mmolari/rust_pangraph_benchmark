# benchmark for new pangraph rust implementation

## setup

**binaries:**
Location of the binaries is encoded in the `binaries` entry of the [config file](config.yaml). Currently:
- the `pangraph` binary should be available in the path. This corresponds to the old julia version.
- the `pangraph_rust_release` binary should be available in the root folder of the repository. This corresponds to the new rust implementation in the `release` profile.
- the `pangraph_rust_profiling` binary should be available in the root folder of the repository. This corresponds to the new rust implementation in the `profiling` profile, containing additional debug checks.
- the `pangraph_rust_debug` binary should be available in the root folder of the repository. This corresponds to the new rust implementation in the `debug` profile, containing additional debug checks.

Any alternative location can be simply encoded by changing the config file.

**datasets:**
- data will be downloaded from NCBI using [ncbi-acc-download](https://github.com/kblin/ncbi-acc-download).
- to facilitate the download, you can save your NCBI api key in a `ncbi_api_key.txt` file in the root folder of the repository.

## running the pipeline

Running the pipeline requires [snakemake](https://snakemake.readthedocs.io/en/stable/) v8+ and a working installation of conda/mamba.

The pipeline is designed to run on a slurm cluster (see the [profile file](profiles/cluster/config.v8+.yaml)). It can be run with:

```sh
snakemake --profile profiles/cluster all
```

To run the verification / debugging steps, use:

```sh
snakemake --profile profiles/cluster verify
snakemake --profile profiles/cluster debug
```

## results

The pipeline produces the two benchmark summary images below, together with [a summary table](results/summary.csv).

![stats](results/stats.png)

![log_stats](results/stats_log.png)