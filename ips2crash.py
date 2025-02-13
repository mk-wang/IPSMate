import json
import os
import sys
from datetime import datetime


def convert_ips_to_crash(ips_file_path, output_filename=None):
    # Read the IPS file
    with open(ips_file_path, 'r') as f:
        content = f.readlines()

    # Extract header JSON
    header = json.loads(content[0])

    # Create crash file name
    if output_filename is None:
        timestamp = datetime.strptime(header['timestamp'].split(
        )[0] + ' ' + header['timestamp'].split()[1], '%Y-%m-%d %H:%M:%S.%f')
        crash_filename = header['app_name'] + '_' + \
            timestamp.strftime('%Y-%m-%d_%H-%M-%S') + '.crash'
    else:
        crash_filename = output_filename

    # Convert content to crash format
    crash_content = []
    crash_content.append("Incident Identifier: " + header['slice_uuid'] + "\n")
    crash_content.append("CrashReporter Key: " +
                         header.get('crashreporter_key', 'unknown') + "\n")
    crash_content.append("Hardware Model: " +
                         header.get('hardware_model', 'unknown') + "\n")
    crash_content.append(
        "Process: " + header['app_name'] +
        " [" + header.get('pid', '0')
        + "]\n")
    crash_content.append("Path: " + header.get('path', 'unknown') + "\n")
    crash_content.append("Identifier: "
                         + header['bundleID'] +
                         "\n")
    crash_content.append(
        "Version: " + header['build_version']
        + " (" + header['app_version']
        + ")\n")
    crash_content.append("Code Type: ARM-64\n")
    crash_content.append("Role: " + header.get('role', 'Foreground') + "\n")
    crash_content.append("Date/Time: " + header['timestamp'] + "\n")
    crash_content.append("OS Version: " + header['os_version'] + "\n")
    crash_content.append(
        "Launch Time: " + header.get('launch_time', 'unknown') + "\n")
    crash_content.append("\n")

    # Add the rest of the content
    is_header = True
    for line in content[1:]:
        if line.strip() == "":
            is_header = False
            crash_content.append(line)
            continue

        if not is_header:
            crash_content.append(line)

    # Write crash file
    output_path = os.path.join(os.path.dirname(ips_file_path), crash_filename)
    with open(output_path, 'w') as f:
        f.writelines(crash_content)

    return output_path


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python ips2crash.py <ips_file> [output_crash_file]")
        sys.exit(1)

    ips_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else None

    if not os.path.exists(ips_file):
        print("Error: File not found: " + ips_file)
        sys.exit(1)

    try:
        output_path = convert_ips_to_crash(ips_file, output_file)
        print("Successfully converted to: " + output_path)
    except Exception as e:
        print("Error converting file: " + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
