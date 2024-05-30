import os
import subprocess
import shutil
import datetime
import argparse
import getpass
import pandas as pd
from tabulate import tabulate
from colorama import init, Fore, Back, Style
import sys
import textwrap
import logging

# Initialize colorama
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Application:
    def __init__(self, name, size, installed_from, path, installed_date):
        self.name = name
        self.size = size
        self.installed_from = installed_from
        self.path = path
        self.installed_date = installed_date

def format_size(size):
    if size >= 2**30:
        return f"{size / 2**30:.2f} GB"
    elif size >= 2**20:
        return f"{size / 2**20:.2f} MB"
    elif size >= 2**10:
        return f"{size / 2**10:.2f} KB"
    else:
        return f"{size} B"

def get_mod_time(path):
    try:
        mod_time = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d")
    except FileNotFoundError:
        return ""

def calculate_total_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                continue
    return total_size

def get_temporary_file_size(app_path):
    temporary_size = 0
    temp_dirs = [
        "/private/var/folders",
        "/var/folders",
        "/private/tmp",
        "/tmp"
    ]
    for temp_dir in temp_dirs:
        temp_path = os.path.join(temp_dir, "com.apple.appsandbox.containerd")
        if os.path.exists(temp_path):
            temporary_size += calculate_total_size(temp_path)
    return temporary_size

def find_brew_path():
    try:
        brew_path = subprocess.check_output(["which", "brew"]).decode("utf-8").strip()
        return brew_path
    except subprocess.CalledProcessError:
        return None

def get_applications():
    applications = []

    applications_path = "/Applications"
    for item in os.listdir(applications_path):
        if item.endswith(".app"):
            app_path = os.path.join(applications_path, item)
            size = calculate_total_size(app_path) + get_temporary_file_size(app_path)
            installed_from = "Manual"
            installed_date = get_mod_time(app_path)
            applications.append(Application(item, size, installed_from, app_path, installed_date))

    brew_path = find_brew_path()
    if brew_path:
        try:
            brew_apps = subprocess.check_output([brew_path, "list", "--cask"], user=os.getlogin()).decode("utf-8").strip().split("\n")
            for app in brew_apps:
                app_path = os.path.join(applications_path, f"{app}.app")
                size = calculate_total_size(app_path) + get_temporary_file_size(app_path)
                installed_from = "Homebrew"
                installed_date = get_mod_time(app_path)
                applications.append(Application(app, size, installed_from, app_path, installed_date))
        except subprocess.CalledProcessError:
            pass

    try:
        app_store_apps = subprocess.check_output(["mdfind", "kMDItemAppStoreHasReceipt=1"]).decode("utf-8").strip().split("\n")
        for app in app_store_apps:
            if app.endswith(".app"):
                app_name = os.path.basename(app)
                size = calculate_total_size(app) + get_temporary_file_size(app)
                installed_from = "App Store"
                installed_date = get_mod_time(app)
                applications.append(Application(app_name, size, installed_from, app, installed_date))
    except subprocess.CalledProcessError:
        pass

    applications.sort(key=lambda x: x.name.lower())
    return applications

def print_applications(applications):
    data = []
    for idx, app in enumerate(applications, start=1):
        data.append([idx, app.name, format_size(app.size), app.installed_from, app.path, app.installed_date])

    headers = [Fore.WHITE + Back.GREEN + "#", "App Name", "Size", "From", "Path", "Installed" + Style.RESET_ALL]
    table = tabulate(data, headers=headers, tablefmt="plain")
    print(table)

def uninstall_multiple_applications(indexes):
    applications = get_applications()
    uninstall_apps = []
    for idx in indexes:
        try:
            idx = int(idx) - 1
            if 0 <= idx < len(applications):
                uninstall_apps.append(applications[idx])
        except ValueError:
            continue

    for app in uninstall_apps:
        uninstall_application_complete(app.name)

def uninstall_application_complete(app_name):
    applications_path = "/Applications"
    app_path = os.path.join(applications_path, app_name)

    if not os.path.exists(app_path):
        print(f"Application {app_name} not found in {applications_path}")
        return

    initial_size = calculate_total_size(app_path)

    print(f"Uninstalling {app_name}...")

    if is_application_running(app_name):
        response = input(f"{Fore.RED}{app_name} is currently running. Would you like to quit it? (Y/n): {Style.RESET_ALL}")
        if response.lower() != 'y':
            print(f"{Fore.RED}Aborted uninstallation of {app_name}.{Style.RESET_ALL}")
            return
        else:
            kill_application(app_name)
            if is_application_running(app_name):
                print(f"{Fore.RED}Error: Could not quit {app_name}. Please try quitting manually.{Style.RESET_ALL}")
                return

    delete_path(app_path)

    artifacts = find_artifacts(app_name.split(".app")[0])
    artifacts_size = 0

    for artifact in artifacts:
        artifacts_size += calculate_total_size(artifact)
        delete_path(artifact)

    total_size_freed = initial_size + artifacts_size
    print(f"{app_name} uninstalled successfully. Total space freed: {total_size_freed / (1024 * 1024):.2f} MB")
    logging.info(f"Uninstalled {app_name}. Total space freed: {total_size_freed / (1024 * 1024):.2f} MB")

def is_application_running(app_name):
    try:
        output = subprocess.check_output(["pgrep", "-f", app_name])
        if output.strip():
            return True
    except subprocess.CalledProcessError:
        pass
    return False

def kill_application(app_name):
    try:
        subprocess.check_call(["pkill", "-f", app_name])
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error: Failed to kill {app_name}. {e}{Style.RESET_ALL}")

def delete_path(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

def find_artifacts(app_name):
    artifacts = []
    user = getpass.getuser()
    library_paths = [
        f"/Users/{user}/Library/Application Support/{app_name}",
        f"/Users/{user}/Library/Caches/{app_name}",
        f"/Users/{user}/Library/Preferences/{app_name}.plist",
        f"/Users/{user}/Library/Logs/{app_name}"
    ]
    for path in library_paths:
        if os.path.exists(path):
            artifacts.append(path)
    return artifacts

def run_with_sudo():
    if os.geteuid() != 0:
        args = ['sudo', sys.executable] + sys.argv
        os.execlpe('sudo', *args, os.environ)

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='iAppGone',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
-----------------------------------------------------------    
--[ iAppGone - Fully Functional Uninstaller for Mac OS ]---
-----------------------------------------------------------                                 
         _ _____         _____             
        |_|  _  |___ ___|   __|___ ___ ___ 
        | |     | . | . |  |  | . |   | -_|
        |_|__|__|  _|  _|_____|___|_|_|___|
                |_| |_|                    
                         By h4rithd.com

Usage:
    sudo python3 iAppGone.py -l
    sudo python3 iAppGone.py -u AppName
    sudo python3 iAppGone.py -m 1,2,4
        '''))

    parser.add_argument("-l", "--list", action="store_true", help="List all installed applications")
    parser.add_argument("-u", "--app", help="Uninstall a specific application by name")
    parser.add_argument("-m", "--multi", help="Uninstall multiple applications by index numbers (comma-separated)")

    return parser.parse_args()

def main():
    run_with_sudo()
    
    args = parse_arguments()

    if args.list:
        applications = get_applications()
        print_applications(applications)
    elif args.app:
        uninstall_application_complete(args.app)
    elif args.multi:
        indexes = args.multi.split(",")
        uninstall_multiple_applications(indexes)
    else:
        print("Invalid option. Use -h for help.")

if __name__ == "__main__":
    main()
