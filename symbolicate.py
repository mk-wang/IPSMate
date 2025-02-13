import os
import subprocess
import re
import argparse
from pathlib import Path


def find_dsym_in_archives(crash_uuid):
    """Search for matching dSYM file in Xcode Archives based on UUID"""
    archives_path = os.path.expanduser("~/Library/Developer/Xcode/Archives")

    # Find all .xcarchive directories
    for archive in Path(archives_path).rglob("*.xcarchive"):
        dsyms_path = archive / "dSYMs"
        if not dsyms_path.exists():
            continue

        # Search through all dSYM files in the archive
        for dsym in dsyms_path.rglob("*.dSYM"):
            print(f"Checking dSYM: {dsym}")
            try:
                # Run dwarfdump to get UUID
                result = subprocess.run(
                    ["dwarfdump", "--uuid", str(dsym)],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Extract UUID from dwarfdump output
                uuid_match = re.search(
                    r'UUID: ([0-9A-F-]+)', result.stdout, re.IGNORECASE)
                if uuid_match:
                    dsym_uuid = uuid_match.group(1)
                    if dsym_uuid.upper() == crash_uuid.upper():
                        return str(dsym)

            except subprocess.CalledProcessError:
                continue

    return None


def get_crash_uuid(crash_file):
    """Extract UUID from crash file"""
    try:
        with open(crash_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Look for Incident Identifier
            incident_pattern = r'Incident Identifier:\s*([0-9a-fA-F-]{36})'
            match = re.search(incident_pattern, content)
            if match:
                return match.group(1)

            # Fallback to UUID pattern in binary images section
            uuid_pattern = r'UUID: ([0-9A-F-]{36})'
            match = re.search(uuid_pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)

            # Fallback to looking for binary UUID
            binary_uuid_pattern = r'Binary Images:.*?UUID: ([0-9A-F-]{36})'
            match = re.search(binary_uuid_pattern, content,
                              re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)

    except Exception as e:
        print(f"Error reading crash file: {e}")
    return None


def symbolicate_crash(crash_file, dsym_file):
    # Get script directory and symbolicatecrash path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    symbolicatecrash = os.path.join(script_dir, 'symbolicatecrash')

    # Verify symbolicatecrash exists
    if not os.path.exists(symbolicatecrash):
        raise FileNotFoundError(
            f"symbolicatecrash not found at {symbolicatecrash}")

    try:
        # Execute symbolication command with absolute path
        result = subprocess.run(
            args=[symbolicatecrash, crash_file, dsym_file],
            capture_output=True,
            text=True,
            check=True
        )

        # Generate output filename
        output_file = os.path.splitext(crash_file)[0] + "_symbolicated.crash"

        # Save symbolication result
        with open(output_file, 'w') as f:
            f.write(result.stdout)

        print("Symbolication successful, output file: " + output_file)

    except Exception as e:
        print("Symbolication failed: " + str(e))


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

    if not os.path.exists(args.ips_file):
        print("Error: IPS file not found")
        return

    # Get directory of input IPS file
    ips_dir = os.path.dirname(os.path.abspath(args.ips_file))
    ips_name = os.path.splitext(os.path.basename(args.ips_file))[0]

    # Create temporary file in the same directory as IPS file
    temp_crash = os.path.join(ips_dir, f"{ips_name}_temp.crash")
    print(f"Using temporary crash file: {temp_crash}")

    # Get script directory for ips2crash.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ips2crash_path = os.path.join(script_dir, 'ips2crash.py')

    if not os.path.exists(ips2crash_path):
        print(f"Error: ips2crash.py not found at {ips2crash_path}")
        return

    try:
        # Convert IPS to crash using absolute path
        result = subprocess.run(
            args=['python', ips2crash_path, args.ips_file, temp_crash],
            check=True,
            capture_output=True,
            text=True
        )

        # Check if conversion was successful
        if result.returncode != 0:
            print(f"Error converting IPS file:\n{result.stderr}")
            return

        if not os.path.exists(temp_crash):
            print(
                f"Error: create crash file: {temp_crash}")
            return

        print(f"Successfully converted to: {temp_crash}")
        with open(temp_crash, 'r') as f:
            first_line = f.readline().strip()
            if not first_line:
                print("Error: Generated crash file appears invalid")
                return

        print("Crash file validation successful")

        # If dsym_file not provided, try to find it automatically
        if not args.dsym_file:
            crash_uuid = get_crash_uuid(temp_crash)
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

        # Generate default output filename if not specified
        output_file = args.output_file or os.path.splitext(
            args.ips_file)[0] + "_symbolicated.crash"

        # Symbolicate and save to output file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        symbolicatecrash = os.path.join(script_dir, 'symbolicatecrash')

        if not os.path.exists(symbolicatecrash):
            print(f"Error: symbolicatecrash not found at {symbolicatecrash}")
            return

        result = subprocess.run(
            args=[symbolicatecrash, temp_crash, dsym_file],
            capture_output=True,
            text=True,
            check=True
        )

        with open(output_file, 'w') as f:
            f.write(result.stdout)

        print("Symbolication successful, output file: " + output_file)

    except Exception as e:
        print("Error processing file: " + str(e))


if __name__ == "__main__":
    main()
