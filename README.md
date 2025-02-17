# IPSMate：iOS Crash Log Symbolication Tools

A set of tools to convert and symbolicate iOS crash logs from IPS format. Supports both legacy and iOS 15+ crash formats.

## Requirements

- Python 3.x
- Xcode installed (for symbolication tools)
- dwarfdump (included with Xcode)

## Features

- Automatic detection of iOS crash log format (legacy/new)
- Automatic dSYM file discovery in Xcode Archives
- Support for both legacy and iOS 15+ symbolication
- Flexible output file naming
- UUID-based dSYM matching

## Files

- `symbolicate.py`: Main script to process and symbolicate crash logs
- `symbolicatecrash`: Legacy symbolication tool
- `loacate_dsym.py`: Utility to find dSYM files by UUID in Xcode Archives

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/IPSMate.git
cd IPSMate
```

2. Make sure symbolicatecrash is executable:

```bash
chmod +x symbolicatecrash
```

## Usage

### Basic Usage

```bash
python symbolicate.py crash.ips
```

```bash
python symbolicate.py crash.ips --dsym /path/to/app.dSYM
```

### Specify dSYM File

```bash
# Search in default Xcode Archives location
python loacate_dsym.py 12345678-1234-1234-1234-1234567890AB

# Search in multiple custom locations
python loacate_dsym.py 12345678-1234-1234-1234-1234567890AB --archives ~/Archives1 ~/Archives2
```
