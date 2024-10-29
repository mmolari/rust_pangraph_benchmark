import re
import argparse
import json
import pathlib

# Define the function to parse the log content
def parse_log(log_content):
    # Define regex patterns for each field
    patterns = {
        "Command": r'Command being timed:\s*"(.+)"',
        "User time (seconds)": r"User time \(seconds\):\s+([\d.]+)",
        "System time (seconds)": r"System time \(seconds\):\s+([\d.]+)",
        "Percent of CPU this job got": r"Percent of CPU this job got:\s+([\d]+)%",
        "Elapsed (wall clock) time": r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s+([\d:.]+)",
        "Maximum resident set size (kbytes)": r"Maximum resident set size \(kbytes\):\s+(\d+)",
        "Major (requiring I/O) page faults": r"Major \(requiring I/O\) page faults:\s+(\d+)",
        "Minor (reclaiming a frame) page faults": r"Minor \(reclaiming a frame\) page faults:\s+(\d+)",
        "Voluntary context switches": r"Voluntary context switches:\s+(\d+)",
        "Involuntary context switches": r"Involuntary context switches:\s+(\d+)",
        "Page size (bytes)": r"Page size \(bytes\):\s+(\d+)",
        "Exit status": r"Exit status:\s+(\d+)"
    }

    # Parse the log data
    parsed_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, log_content)
        if match:
            parsed_data[key] = match.group(1)

    # Count FASTA files in the "Command" field
    if "Command" in parsed_data:
        fasta_count = len(re.findall(r'\S+\.fa\b', parsed_data["Command"]))
        parsed_data["fasta file count"] = fasta_count

    return parsed_data

def graph_filesize(fname):
    f = pathlib.Path(fname)
    filesize_bytes = f.stat().st_size
    filesize_mb = filesize_bytes / (1024 ** 2)
    return filesize_mb

# Main function to handle argument parsing and writing to JSON
def main():
    parser = argparse.ArgumentParser(description="Parse /usr/bin/time -v log file and export to JSON.")
    parser.add_argument("--logfile", type=str, help="Path to the log file to parse.")
    parser.add_argument("--graph_file", type=str, help="output graph file")
    parser.add_argument("--output_json", type=str, help="Path to the output JSON file.")
    args = parser.parse_args()

    # Read the log file content
    with open(args.logfile, 'r') as f:
        log_content = f.read()

    # Parse the log content
    parsed_data = parse_log(log_content)
    parsed_data["graph file size (Mb)"] = graph_filesize(args.graph_file)

    with open(args.output_json, "w") as f:
        json.dump(parsed_data, f, indent=4)

    print(f"Log data has been parsed and written to {args.output_json}.")

if __name__ == "__main__":
    main()
