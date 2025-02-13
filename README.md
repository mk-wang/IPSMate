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
# Basic usage
python symbolicate.py crash.ips

# With explicit dSYM file
python symbolicate.py crash.ips --dsym /path/to/app.dSYM

# With custom output file
python symbolicate.py crash.ips --output symbolicated.crash

# With both dSYM and output file
python symbolicate.py crash.ips --dsym /path/to/app.dSYM --output symbolicated.crash

# Using short options
python symbolicate.py crash.ips -d /path/to/app.dSYM -o symbolicated.crash
```

### Arguments

- `ips_file`: Required. Path to the input IPS crash report file
- `--dsym, -d`: Optional. Path to dSYM file. If not provided, will search in Xcode Archives
- `--output, -o`: Optional. Path for output file. If not provided, will use input filename with "\_symbolicated.crash" suffix
