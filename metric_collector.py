import argparse
import json
import os


def members_from_manifest(path):
    """api >= 0.8.0: the gathered results, read from the `--from-files` manifest.

    One row per gathered file: where it is, and which stage/module chain
    (lineage) produced it."""
    with open(path) as fh:
        manifest = json.load(fh)
    rows = []
    for member in manifest["members"]:
        lineage = "/".join(f"{step['stage']}.{step['module']}" for step in member["lineage"])
        for output_id, file_path in member["files"].items():
            rows.append((lineage, output_id, file_path))
    return rows


def write_tsv(path, rows):
    with open(path, 'w') as file:
        file.write("lineage\toutput\tpath\n")
        for row in rows:
            file.write("\t".join(row) + "\n")


def write_html(path, rows):
    with open(path, 'w') as file:
        file.write("<html><body>\n<h2>Input Files</h2>\n<ul>\n")
        for lineage, _, file_path in rows:
            file.write(f"<li>{lineage}: {file_path}</li>\n")
        file.write("</ul>\n</body></html>\n")


def main():
    parser = argparse.ArgumentParser(description='Collect results into one table and one report.')
    parser.add_argument('--output_dir', type=str, help='output directory where results are stored.')
    # api >= 0.8.0 (gather stage)
    parser.add_argument('--from-files', dest='from_files', type=str, help='manifest (lineage.json) listing the gathered files.')
    parser.add_argument('--output', action='append', default=[], help='id=PATH of an output to write')
    # api < 0.8.0 (metric collector)
    parser.add_argument('--metrics.scores', type=str, nargs='+', help='Metrics scores files.')
    args, _ = parser.parse_known_args()

    if args.from_files:
        rows = members_from_manifest(args.from_files)
    else:
        rows = [("", "metrics.scores", f) for f in getattr(args, 'metrics.scores') or []]

    paths = [o.split("=", 1)[1] for o in args.output] or [
        os.path.join(args.output_dir, 'biometrics.tsv'),
        os.path.join(args.output_dir, 'biometrics_report.html'),
    ]
    for path in paths:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        # The output's file extension picks what is written to it.
        (write_html if path.endswith('.html') else write_tsv)(path, rows)


if __name__ == "__main__":
    main()
