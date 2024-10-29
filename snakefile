configfile: "config.yaml"


accs = config["acc_nums"]


def acc_list(n):
    """return the path of the first n files"""
    return [f"data/{acc}.fa" for acc in accs[: int(n)]]


rule build_rust:
    input:
        fa=lambda w: acc_list(w.n),
    output:
        graph="results/graphs/rust_{n}.json",
        log="results/log/rust_{n}.txt",
    params:
        pg=config["binaries"]["rust"],
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
        fa=lambda w: acc_list(w.n),
    output:
        graph="results/graphs/julia_{n}.json",
        log="results/log/julia_{n}.txt",
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
        fa=lambda w: acc_list(w.n),
    output:
        graph="results/graphs/verify_{n}.json",
        log="results/log/verify_{n}.txt",
    params:
        pg=config["binaries"]["rust"],
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
        log="results/log/{tool}_{n}.txt",
        graph="results/graphs/{tool}_{n}.json",
    output:
        "results/parsed_log/{tool}_{n}.json",
    shell:
        """
        python scripts/parse_log.py \
            --logfile {input.log} \
            --graph_file {input.graph} \
            --output_json {output}
        """


Ns = config["Ns"]


rule stat_figs:
    input:
        expand(rules.parse_log.output, n=Ns, tool=["julia", "rust", "verify"]),
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
        expand(rules.verify_rust.output, n=Ns),
