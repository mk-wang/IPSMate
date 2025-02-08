import os
import sys
import subprocess

def symbolicate_crash(crash_file, dsym_file):
    # symbolicatecrash tool path
    symbolicatecrash = "./symbolicatecrash"
    
    try:
        # Execute symbolication command
        result = subprocess.run([
            symbolicatecrash,
            crash_file,
            dsym_file
        ], capture_output=True, text=True)
        
        # Generate output filename
        output_file = os.path.splitext(crash_file)[0] + "_symbolicated.crash"
        
        # Save symbolication result
        with open(output_file, 'w') as f:
            f.write(result.stdout)
            
        print("Symbolication successful, output file: " + output_file)
        
    except Exception as e:
        print("Symbolication failed: " + str(e))

def main():
    if len(sys.argv) != 4:
        print("Usage: python symbolicate.py <ips_file> <dsym_file> <output_file>")
        sys.exit(1)

    ips_file = sys.argv[1]
    dsym_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Ensure files exist
    if not os.path.exists(ips_file):
        print("Error: IPS file not found")
        return
    if not os.path.exists(dsym_file):
        print("Error: dSYM file not found")
        return
    
    # Convert IPS to crash file and symbolicate
    try:
        # Use temporary crash file
        temp_crash = "temp_crash.crash"
        subprocess.run(['python', 'ips2crash.py', ips_file, temp_crash], check=True)
        
        # Symbolicate and save directly to output file
        result = subprocess.run([
            './symbolicatecrash',
            temp_crash,
            dsym_file
        ], capture_output=True, text=True)
        
        with open(output_file, 'w') as f:
            f.write(result.stdout)
            
        # Clean up temp file
        os.remove(temp_crash)
        print("Symbolication successful, output file: " + output_file)
        
    except Exception as e:
        print("Error processing file: " + str(e))
        if os.path.exists(temp_crash):
            os.remove(temp_crash)

if __name__ == "__main__":
    main()