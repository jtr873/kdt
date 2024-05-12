import subprocess
import os
import argparse

def get_third_party_packages(serial=None):
    """Get a list of third-party packages installed on the Android device."""
    cmd = ['adb']
    if serial:
        cmd.extend(['-s', serial])
    cmd.extend(['shell', 'pm', 'list', 'packages', '-3'])
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    package_list = result.stdout.decode('utf-8').strip().split('\n')
    packages = [pkg.split(':')[1] for pkg in package_list if pkg.startswith('package:')]
    return packages

def get_apk_paths(serial, package_name):
    """Get the APK paths of a specific package."""
    cmd = ['adb']
    if serial:
        cmd.extend(['-s', serial])
    cmd.extend(['shell', 'pm', 'path', package_name])
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    paths = result.stdout.decode('utf-8').strip().split('\n')
    apk_paths = [path.split(':')[1] for path in paths if path.startswith('package:')]
    return apk_paths

def pull_apk(serial, package_name, apk_path, output_dir):
    """Pull the APK file from the device to the host environment."""
    os.makedirs(output_dir, exist_ok=True)
    apk_file_name = os.path.basename(apk_path)
    output_path = os.path.join(output_dir, apk_file_name)
    cmd = ['adb']
    if serial:
        cmd.extend(['-s', serial])
    cmd.extend(['pull', apk_path, output_path])
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="Pull APKs from an Android device")
    parser.add_argument("-s", "--serial", help="Serial number of the Android device")
    parser.add_argument("-o", "--output_dir", default="apks", help="Output directory for APKs (default: apks)")
    args = parser.parse_args()

    serial = args.serial
    packages = get_third_party_packages(serial)
    output_base_dir = args.output_dir

    for package in packages:
        print(f"Processing package: {package}")
        apk_paths = get_apk_paths(serial, package)
        if apk_paths:
            package_output_dir = os.path.join(output_base_dir, package)
            for apk_path in apk_paths:
                pull_apk(serial, package, apk_path, package_output_dir)
            print(f"APK(s) for {package} pulled to {package_output_dir}")
        else:
            print(f"Failed to get APK paths for {package}")

if __name__ == "__main__":
    main()

