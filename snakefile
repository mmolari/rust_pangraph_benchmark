configfile: "config.yaml"


import numpy as np
from functools import cache

accs = config["acc_nums"]
R = int(config["n_replicates"])


@cache
def acc_list(N, r):
    """returns the path of N files, for replicate r"""
    assert isinstance(N, int), f"{N=} should be integer"
    assert isinstance(r, int), f"{r=} should be integer"
    seed = r + 100 * N
    np.random.seed(seed)
    L = len(accs)
    # pick N from L
    nums = np.random.choice(L, N, replace=False)
    return sorted([f"data/{accs[i]}.fa" for i in nums])


rule build_rust:
    input:
        fa=lambda w: acc_list(int(w.n), int(w.r)),
    output:
        graph="results/graphs/rust_{n}_repl{r}.json",
        log="results/log/rust_{n}_repl{r}.txt",
    params:
        pg=config["binaries"]["rust_release"],
    shell:
        """
        /usr/bin/time -v \
            {params.pg} build \
            -c -l 100 -a 10 -b 5 \
            {input.fa} > {output.graph}.tmp 2> {output.log}
        tr -d '[:space:]' < {output.graph}.tmp > {output.graph}
        rm {output.graph}.tmp
        """


rule build_julia:
    input:
        fa=lambda w: acc_list(int(w.n), int(w.r)),
    output:
        graph="results/graphs/julia_{n}_repl{r}.json",
        log="results/log/julia_{n}_repl{r}.txt",
    params:
        pg=config["binaries"]["julia"],
    shell:
        """
        export JULIA_NUM_THREADS=16 && \
            /usr/bin/time -v \
            {params.pg} build \
            -c -l 100 -a 10 -b 5 \
            {input.fa} > {output.graph} 2> {output.log}
        """


rule verify_rust:
    input:
        fa=lambda w: acc_list(int(w.n), int(w.r)),
    output:
        graph="results/graphs/verify_{n}_repl{r}.json",
        log="results/log/verify_{n}_repl{r}.txt",
    params:
        pg=config["binaries"]["rust_profiling"],
    shell:
        """
        /usr/bin/time -v \
            {params.pg} build \
            -c -l 100 -a 10 -b 5 \
            --verify \
            {input.fa} > {output.graph} 2> {output.log}
        """


rule parse_log:
    input:
        log="results/log/{tool}_{n}_repl{r}.txt",
        graph="results/graphs/{tool}_{n}_repl{r}.json",
    output:
        "results/parsed_log/{tool}_{n}_repl{r}.json",
    shell:
        """
        python scripts/parse_log.py \
            --replicate {wildcards.r} \
            --logfile {input.log} \
            --graph_file {input.graph} \
            --output_json {output}
        """


Ns = config["Ns"]


rule stat_figs:
    input:
        expand(
            rules.parse_log.output, n=Ns, r=range(R), tool=["julia", "rust", "verify"]
        ),
    output:
        fig="results/stats.png",
        fig_log="results/stats_log.png",
        csv="results/summary.csv",
    conda:
        "envs/general.yaml"
    shell:
        """
        python scripts/summary_stats.py \
            --fig_file {output.fig} \
            --fig_file_log {output.fig_log} \
            --out_csv {output.csv} \
            --logfiles {input}
        """


rule all:
    input:
        rules.stat_figs.output,
