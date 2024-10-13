import argparse
from pip._vendor.distlib.wheel import ABI, ARCH, IMPVER
import sys

def parse_args(argv):
    description = "Main interface to training a BrainNet model. For convenience, a few parameters are exposed on the command line. Values provided here will overwrite those set in the configuration file."
    parser = argparse.ArgumentParser(
        prog="blabla",
        description=description,
    )
    parser.add_argument(
        "package-name", help="Configuration file defining the parameters for training."
    )
    parser.add_argument(
        "package-version",
        help="Resume training from this checkpoint.",
    )
    parser.add_argument(
        "--python-tag",
        help="Python tag (e.g., cp311).",
    )
    parser.add_argument(
        "--abi-tag",
        help="ABI tag (e.g., cp311).",
    )
    parser.add_argument(
        "--platform-tag",
        help="Platform tag (e.g., linux_x86_64).",
    )

    return parser.parse_args(argv[1:])


def build_wheel_name(args):

    python_tag = args.python_tag or IMPVER
    abi_tag = args.abi_tag or ABI
    platform_tag = args.platform_tag or ARCH

    stem = "-".join([getattr(args, "package-name"), getattr(args, "package-version"), python_tag, abi_tag, platform_tag])
    name = ".".join([stem, "whl"])
    return name

if __name__ == "__main__":
    args = parse_args(sys.argv)
    name = build_wheel_name(args)
    print(name)