#!/usr/bin/python3

import json
import os
import subprocess
import re
import argparse
from loacate_dsym import find_dsym_in_archives


def get_file_info(crash_file):
    """
    Extract UUID and OS version from crash file
    Returns: tuple of (uuid, os_version)
    """
    try:
        with open(crash_file, 'r', encoding='utf-8') as f:
            # Read first line as JSON
            first_line = f.readline().strip()
            crash_info = json.loads(first_line)

            # Extract uuid and os_version from JSON
            uuid = crash_info.get('slice_uuid')
            os_version = crash_info.get('os_version')

            return uuid, os_version

    except Exception as e:
        print(f"Error reading crash file: {e}")
    return None, None


def symbolicate_crash15(crash_file, dsym_file, output_file):
    """Symbolicate crash using Xcode 15's CrashSymbolicator"""
    crash_symbolizer = ("/Applications/Xcode.app/Contents/SharedFrameworks/"
                        "CoreSymbolicationDT.framework/Versions/A/Resources/"
                        "CrashSymbolicator.py")

    if not os.path.exists(crash_symbolizer):
        print("Error: Xcode 15 crash symbolizer not found")
        return False

    try:
        result = subprocess.run(
            args=[
                'python3',
                crash_symbolizer,
                crash_file,
                '-d', dsym_file,
                '-o', output_file
            ],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stderr:
            print(f"Warnings during symbolication: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Xcode 15 symbolication: {e}")
        print(f"Stderr: {e.stderr}")
        return False


def symbolicate_crash(crash_file, dsym_file, output_file):
    """Symbolicate crash using legacy symbolicatecrash tool"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    symbolicatecrash = os.path.join(script_dir, 'symbolicatecrash')

    if not os.path.exists(symbolicatecrash):
        print(f"Error: symbolicatecrash not found at {symbolicatecrash}")
        return False
    try:
        result = subprocess.run(
            args=[symbolicatecrash, crash_file, dsym_file],
            capture_output=True,
            text=True,
            check=True
        )

        with open(output_file, 'w') as f:
            f.write(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running symbolication: {e}")
        print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error during symbolication: {e}")
        return False


def get_os_version_number(os_version_string):
    """Extract major version number from OS version string"""
    if not os_version_string:
        return None
    # Match pattern like "iPhone OS 13.0 (17A577)" or "iOS 15.0 (19A346)"
    match = re.search(r'(?:iPhone OS|iOS)\s+(\d+)', os_version_string)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Symbolicate iOS crash reports')
    parser.add_argument('ips_file',
                        help='Input IPS crash report file')
    parser.add_argument('--dsym', '-d',
                        dest='dsym_file',
                        help='Path to dSYM file '
                             '(optional, will search in Archives)')
    parser.add_argument('--output', '-o',
                        dest='output_file',
                        help='Output file path (optional)')

    args = parser.parse_args()
    ips_file = args.ips_file
    if not os.path.exists(ips_file):
        print("Error: IPS file not found")
        return

    dsym_file = args.dsym_file
    is_new_version = False
    try:
        # If dsym_file not provided, try to find it automatically
        if not dsym_file:
            crash_uuid, os_version = get_file_info(ips_file)
            os_version_num = get_os_version_number(os_version)
            is_new_version = os_version_num and os_version_num >= 15

            if crash_uuid:
                print(f"Found UUID in crash file: {crash_uuid}")
                dsym_file = find_dsym_in_archives(crash_uuid)
                if dsym_file:
                    print(f"Found matching dSYM file: {dsym_file}")
                else:
                    print("Error: Could not find matching dSYM file")
                    return
            else:
                print("Error: Could not extract UUID from crash file")
                return
        elif not os.path.exists(args.dsym_file):
            print("Error: Specified dSYM file not found")
            return
    except Exception as e:
        print("Error finding dSYM file: " + str(e))

    try:
        # Generate default output filename if not specified
        output_file = args.output_file or os.path.splitext(
            args.ips_file)[0] + "_symbolicated.crash"
        result = False
        print(
            f"Symbolicating : {ips_file}, new version: {is_new_version}")
        if is_new_version:
            result = symbolicate_crash15(ips_file, dsym_file, output_file)
        else:
            result = symbolicate_crash(ips_file, dsym_file, output_file)

        if result:
            print(f"Symbolication successful, output file: {output_file}")

    except Exception as e:
        print("Error processing file: " + str(e))


if __name__ == "__main__":
    main()
