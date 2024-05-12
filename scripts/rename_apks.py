import subprocess
import os
import re
import argparse
from shutil import copyfile

def get_apk_info(apk_path):
    """Extract package name, version name, and ABIs from the APK using aapt."""
    result = subprocess.run(['aapt', 'dump', 'badging', apk_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    
    package_name_match = re.search(r"package: name='(\S+)'", output)
    version_name_match = re.search(r"versionName='([\S]+)'", output)
    abis_match = re.search(r"native-code: '([\S\s]+)'", output)

    if not package_name_match or not version_name_match:
        raise ValueError(f"Failed to extract info from {apk_path}")

    package_name = package_name_match.group(1)
    version_name = version_name_match.group(1)
    abis = abis_match.group(1).replace("'", "").replace(" ", "_") if abis_match else 'noabi'  # Combine ABIs into a single string without quotes

    return package_name, version_name, abis

def rename_apk(apk_path, output_dir):
    """Rename the APK file with the format <package_name>_<version_name>_<abis>.apk."""
    package_name, version_name, abis = get_apk_info(apk_path)
    
    new_file_name = f"{package_name}_{version_name}_{abis}.apk"
    new_file_path = os.path.join(output_dir, new_file_name)
    copyfile(apk_path, new_file_path)
    print(f"Renamed {apk_path} to {new_file_path}")

def find_apk_files(search_dir):
    """Find all APK files in the specified directory."""
    result = subprocess.run(['find', search_dir, '-name', '*.apk'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    apk_files = result.stdout.decode('utf-8').strip().split('\n')
    return apk_files

def main():
    parser = argparse.ArgumentParser(description="Rename APKs with package name, version name, and ABI information")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--directory", help="Directory to search for APK files")
    group.add_argument("-f", "--file", help="Path to a single APK file")
    parser.add_argument("-o", "--output_dir", default=".", help="Directory to store the renamed APK files")
    args = parser.parse_args()

    if args.directory and not args.output_dir:
        parser.error("-o/--output_dir is required when using -d/--directory option")

    os.makedirs(args.output_dir, exist_ok=True)

    apk_files = []
    
    if args.directory:
        apk_files = find_apk_files(args.directory)
    elif args.file:
        apk_files = [args.file]
    else:
        # If neither directory nor file is provided, use the current directory
        apk_files = [os.path.join(os.getcwd(), f) for f in os.listdir() if f.endswith('.apk')]

    for apk_path in apk_files:
        if apk_path:  # Ensure the path is not empty
            try:
                rename_apk(apk_path, args.output_dir)
            except Exception as e:
                print(f"Error processing {apk_path}: {e}")

if __name__ == "__main__":
    main()

