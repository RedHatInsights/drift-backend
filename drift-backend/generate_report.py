import argparse
import json

import toml

from kerlescan.inventory_service_interface import interleave_systems_and_profiles

from drift import info_parser
from drift.app import create_app


def _read_file(path):
    with open(path, "r") as myfile:
        return json.loads(myfile.read())


def _read_inputs(
    systems_path,
    profiles_path,
    baselines_path,
    tags_path,
    hsps_path,
    expected_output_path,
):
    """
    read from file paths and return either parsed json or text
    """
    systems = _read_file(systems_path)["results"]
    profiles = _read_file(profiles_path)["results"]
    baselines = _read_file(baselines_path)["data"]
    tags = _read_file(tags_path)["results"]
    hsps = _read_file(hsps_path)["data"]

    # combine systems + profiles into an object that can be compared
    systems_with_profiles = interleave_systems_and_profiles(systems, profiles, tags)

    # read as text, not json
    with open(expected_output_path, "r") as myfile:
        expected_output = myfile.read().splitlines()

    return systems_with_profiles, baselines, hsps, expected_output


parser = argparse.ArgumentParser()
parser.add_argument("conf_file")
parser.add_argument(
    "--write",
    action="store_true",
    help="write a new report instead of comparing. This should only be used"
    " when the report format has been updated, and you have manually"
    " verified that the new report is correct!",
)
args = parser.parse_args()

conf = None
with open(args.conf_file, "r") as conf_fh:
    conf = toml.load(conf_fh)

print("Testing report generation...")

# TODO: remove need to initialize flask app
app = create_app()
app.app.app_context().push()

for report in conf:
    systems_with_profiles, baselines, hsps, expected_output = _read_inputs(**conf[report])
    comparisons = info_parser.build_comparisons(
        systems_with_profiles,
        baselines,
        hsps,
        None,
        False,
    )
    if args.write:
        outpath = conf[report]["expected_output_path"]
        with open(outpath, "w") as outfile:
            json.dump(comparisons, outfile, indent=4, sort_keys=True)
        print(f"output written to {outpath}")
    else:
        result = json.dumps(comparisons, indent=4, sort_keys=True).splitlines()
        if result != expected_output:
            raise RuntimeError("expected report differed from generated report")
        else:
            print("OK")
