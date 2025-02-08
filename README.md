# IPSMate：iOS Crash Log Symbolication Tools

A set of tools to convert and symbolicate iOS crash logs from IPS format.

## Requirements

- Python 3.x

## Files

- `ips2crash.py`: Converts IPS format crash logs to standard crash format
- `symbolicate.py`: Main script to process and symbolicate crash logs
- `symbolicatecrash`: Symbolication tool (from Xcode15)

## Usage

```bash
python symbolicate.py <ips_file> <dsym_file> <output_file>