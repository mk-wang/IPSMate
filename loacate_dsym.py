#!/usr/bin/python3

from pathlib import Path
import subprocess
import re
import os


def find_dsym_in_archives(
    crash_uuid,
    archives_paths=["~/Library/Developer/Xcode/Archives"]
):
    """Search for matching dSYM file in Xcode Archives based on UUID"""
    import os

    for path in archives_paths:
        archives_path = os.path.expanduser(path)
        if not os.path.exists(archives_path):
            print(f"Archives directory not found: {archives_path}")
            continue

        try:
            for archive in Path(archives_path).rglob("*.xcarchive"):
                dsyms_path = archive / "dSYMs"
                if not dsyms_path.exists():
                    continue

                for dsym in dsyms_path.rglob("*.dSYM"):
                    try:
                        result = subprocess.run(
                            ["dwarfdump", "--uuid", str(dsym)],
                            capture_output=True,
                            text=True,
                            check=True
                        )

                        uuid_match = re.search(
                            r'UUID: ([0-9A-F-]+)',
                            result.stdout,
                            re.IGNORECASE
                        )

                        if uuid_match:
                            dsym_uuid = uuid_match.group(1)
                            if dsym_uuid.upper() == crash_uuid.upper():
                                print(f"Found matching dSYM: {dsym}")
                                return str(dsym)

                    except subprocess.CalledProcessError as e:
                        print(f"Error processing dSYM {dsym}: {e}")
                        continue
                    except Exception as e:
                        print(f"Unexpected error for {dsym}: {e}")
                        continue

        except Exception as e:
            print(f"Error during search: {e}")
            return None

    print(f"No dSYM found for UUID: {crash_uuid}")
    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Find dSYM file by UUID in Xcode Archives')
    parser.add_argument('uuid', help='UUID of the dSYM to find')
    parser.add_argument('--archives', help='Path to Xcode archives',
                        default=["~/Library/Developer/Xcode/Archives"],
                        nargs='+')

    args = parser.parse_args()
    result = find_dsym_in_archives(args.uuid, args.archives)

    if result:
        print(f"Found dSYM at: {result}")
        dsym_dir = os.path.dirname(result)
        subprocess.run(['open', dsym_dir])
    else:
        print(f"No dSYM found for UUID: {args.uuid}")
