import subprocess
import json
import argparse

def get_installed_packages(serial_number=None):
    adb_command = ['adb']
    
    if serial_number:
        adb_command.extend(['-s', serial_number])
        
    adb_command.extend(['shell', 'pm', 'list', 'packages', '-3'])
    
    result = subprocess.run(adb_command, stdout=subprocess.PIPE)
    package_lines = result.stdout.decode('utf-8').splitlines()
    
    packages = []
    
    for line in package_lines:
        parts = line.split(":")
        if len(parts) == 2:
            package_name = parts[1]
                
            # Get package info using dumpsys package
            adb_info_command = ['adb']
            if serial_number:
                adb_info_command.extend(['-s', serial_number])
            
            adb_info_command.extend(['shell', 'dumpsys', 'package', package_name])
            package_info_result = subprocess.run(adb_info_command, stdout=subprocess.PIPE)
            package_info_output = package_info_result.stdout.decode('utf-8')
            
            # Extracting relevant details from the package info
            version_name = ''
            primary_abi = ''
            
            for info_line in package_info_output.splitlines():
                if 'versionName' in info_line:
                    version_name = info_line.split('=')[1]
                elif 'primaryCpuAbi' in info_line:
                    primary_abi = info_line.split('=')[1]
            
            packages.append({
                'package_name': package_name,
                'version_name': version_name,
                'primary_abi': primary_abi
            })
    
    return packages

def print_packages(packages, single_line):
    if single_line:
        print(f"{'Package Name':<40} {'Version':<20} {'Primary ABI'}")
        print("=" * 80)
        for pkg in packages:
            print(f"{pkg['package_name']:<40} {pkg['version_name']:<20} {pkg['primary_abi']}")
    else:
        print(json.dumps(packages, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get details of installed packages on an Android device.')
    parser.add_argument('-s', '--serial', type=str, help='Serial number of the target device')
    parser.add_argument('-p', '--plain', action='store_true', help='Output each package on a single line')
    
    args = parser.parse_args()
    serial_number = args.serial
    single_line = args.plain
    
    packages = get_installed_packages(serial_number)
    
    # Print or save the package details
    print_packages(packages, single_line)

