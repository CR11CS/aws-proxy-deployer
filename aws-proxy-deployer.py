#!/usr/bin/env python3
import argparse
from contextlib import contextmanager
import csv
import ctypes
import ipaddress
import os
import re
import requests
import shutil
import sys
import terraform_installer


class InitializeScript:
    @staticmethod
    def check_process_admin():
        """Check if script is ran as admin, else exit."""
        if os.name == "posix":
            if os.getuid() != 0:
                sys.exit("ERROR: Script must be ran as an admin.")
        elif os.name == "nt":
            if not ctypes.windll.shell32.IsUserAnAdmin():
                sys.exit("ERROR: Script must be ran as an admin.")

    @staticmethod
    def prepare_base_terraform():
        """Detect user OS, and rename Terraform files to avoid overlapping Terraform base configs specific to OS."""
        if os.name == "posix":
            if os.path.exists("base-files/base_key_export_windows.tf"):
                os.rename("base-files/base_key_export_windows.tf", "base-files/base_key_export_windows.tf.alt")
        elif os.name == "nt":
            if os.path.exists("base-files/base_key_export_linux.tf"):
                os.rename("base-files/base_key_export_linux.tf", "base-files/base_key_export_linux.tf.alt")

    @staticmethod
    def check_terraform_present():
        """Checks user's environment to determine if and where Terraform is installed."""
        terraform_present = False
        if shutil.which("terraform"):
            terraform_present = True
        return terraform_present

    @staticmethod
    def check_aws_keys_present():
        """Check if AWS keys are already present in user's environment."""
        access_present = False
        secret_present = False
        if os.environ.get("AWS_ACCESS_KEY_ID"):
            access_present = True
        if os.environ.get("AWS_SECRET_ACCESS_KEY"):
            secret_present = True

        if all([access_present, secret_present]):
            return True
        elif not all([access_present, secret_present]):
            return False

    @staticmethod
    def check_rootkey_present():
        """Checks user's environment for rootkey.csv file."""
        rootkey_present = os.path.exists("rootkey.csv")
        return rootkey_present

    @staticmethod
    def import_aws_keys_csv():
        """Extracts AWS keys from a .csv file as provided by Amazon."""
        with open("rootkey.csv") as key_file:
            aws_variables = csv.reader(key_file)
            csv_header = next(key_file)
            access_key, secret_key = [key.strip() for key in next(key_file).split(",")]
        return access_key, secret_key

    @staticmethod
    def check_proxy_conf_present():
        """Checks user's environment for tinyproxy-install.sh file."""
        proxy_conf_present = os.path.exists("tinyproxy-install.sh")
        return proxy_conf_present

    @staticmethod
    def get_tiny_proxy_config():
        proxy_settings = ["echo "" > /etc/tinyproxy.conf"]
        with open("tinyproxy.conf", "r") as file:
            for line in file:
                proxy_settings.append(f"echo {line} >> /etc/tinyproxy.conf")
        return proxy_settings

    @staticmethod
    def get_public_ip():
        """Gets the user's public IP for use in their AWS security group."""
        try:
            primary = requests.get("https://api.ipify.org/").content.decode("utf-8")
            return primary
        except ConnectionError:
            secondary = requests.get("https://ident.me").content.decode("utf-8")
            return secondary

    @staticmethod
    def check_active_proxy():
        """Determine if a proxy server is active by checking if 'active-proxy' folder exists."""
        return os.path.exists("active-proxy")

    @staticmethod
    def get_active_proxy_filepath():
        if os.name == "posix":
            active_proxy_filepath = os.getcwd() + "/active-proxy"
            return active_proxy_filepath
        elif os.name == "nt":
            active_proxy_filepath = os.getcwd() + "\\active-proxy"
            return active_proxy_filepath

    def initialize_all(self):
        """Initializes environment to have working Terraform executable, AWS keys present, and proxy conf present."""
        # Check for root privileges that are required for functionality
        self.check_process_admin()

        # Detect OS and rename base_key_export_{OS}.tf to avoid usage
        self.prepare_base_terraform()

        # If Terraform isn't installed, download the latest version to your local directory
        if not self.check_terraform_present():
            terraform_installer.install_terraform()
            if os.name == "posix":
                os.system("chmod +x terraform")

        # If no AWS keys are present in environment variables, check for 'rootkey.csv' in local directory
        if not self.check_aws_keys_present():
            if not self.check_rootkey_present():
                sys.exit(
                    "ERROR: Unable to locate environment variables for 'AWS_ACCESS_KEY_ID' and / or 'AWS_SECRET_ACCESS_KEY' and no 'rootkey.csv' was found in the local directory.")
            elif self.check_rootkey_present():
                self.access_key, self.secret_key = self.import_aws_keys_csv()

        # If 'tinyproxy.conf' isn't present in local directory, exit with error
        if not self.check_proxy_conf_present():
            sys.exit("ERROR: Unable to locate 'tinyproxy.conf' in the local directory.")

    def __init__(self):
        self.public_ip = self.get_public_ip()
        self.active_proxy = self.check_active_proxy()
        self.active_proxy_filepath = self.get_active_proxy_filepath()
        self.access_key = None
        self.secret_key = None
        self.initialize_all()


def deploy():
    """Build Terraform folder 'active-proxy', modify 'active_vars.tf' variables, then Terraform init and apply."""
    # Copy base files to active-proxy folder then rename all to "active_".
    shutil.copytree("base-files", "active-proxy")
    for file in os.listdir("active-proxy"):
        if file[-3:] == ".tf":
            os.rename(f"active-proxy/{file}", "active-proxy/" + file.replace("base_", "active_"))

    # Read lines from active_vars.tf, make variable substitutions then write back to file
    base_variables = []
    modified_variables = []
    with open("active-proxy/active_vars.tf") as variables_file:
        base_variables = variables_file.readlines()

    for line in base_variables:
        if "<REGION>" in line:
            line = line.replace("<REGION>", f"\"{region}\"")
        if "<CIDR_BLOCKS>" in line:
            line = line.replace("<CIDR_BLOCKS>", f"{cidr_blocks}")
        if initialize.access_key:
            if "<ACCESS_KEY>" in line:
                line = line.replace("<ACCESS_KEY>", f"{initialize.access_key}")
        if initialize.secret_key:
            if "<SECRET_KEY>" in line:
                line = line.replace("<SECRET_KEY>" f"{initialize.secret_key}")
        modified_variables.append(line)

    with open("active-proxy/active_vars.tf", "w") as variables_file:
        for line in modified_variables:
            variables_file.write(line)

    # Read lines from active_proxy_location.tf, make AWS key substitutions then write back to file
    base_keys = []
    modified_keys = []
    with open("active-proxy/active_proxy_location.tf") as keys_file:
        base_keys = keys_file.readlines()

    for line in base_keys:
        if initialize.access_key:
            if "<ACCESS_KEY>" in line:
                line = line.replace("<ACCESS_KEY>", f"{initialize.access_key}")
        if initialize.secret_key:
            if "<SECRET_KEY>" in line:
                line = line.replace("<SECRET_KEY>", f"{initialize.secret_key}")
        modified_keys.append(line)

    with open("active-proxy/active_proxy_location.tf", "w") as keys_file:
        for line in modified_keys:
            keys_file.write(line)

    if os.name == "posix":
        active_proxy_filepath = os.getcwd() + "/active-proxy"
    elif os.name == "nt":
        active_proxy_filepath = os.getcwd() + "\\active-proxy"

    with suppress_output():
        os.system(f"{terraform_location} -chdir={active_proxy_filepath} init")
        os.system(f"{terraform_location} -chdir={active_proxy_filepath} apply --auto-approve")
    os.system(f"{terraform_location} -chdir={active_proxy_filepath} output")


def destroy():
    """Check for existing TF state and call Terraform destroy to remove all cloud resources"""
    if initialize.active_proxy:
        with suppress_output():
            os.system(f"{terraform_location} -chdir={initialize.active_proxy_filepath} destroy --auto-approve")
    elif not initialize.active_proxy:
        sys.exit("ERROR: No active-proxy found. If this error is incorrect, manually remove all resources via EC2.")


def status():
    """Display current TF state outputs"""
    if initialize.active_proxy:
        with suppress_output():
            os.system(f"{terraform_location} -chdir{initialize.active_proxy_filepath}")
        os.system(f"{terraform_location} -chdir={initialize.active_proxy_filepath} --output")
    elif not initialize.active_proxy:
        sys.exit("ERROR: No active-proxy found. If this error is incorrect, manually remove all resources via EC2.")


def main():
    """Do regular checks to determine if proxy server is active if required for action."""

    if action == "deploy":
        # Ensure no proxy server is active before continuing.
        if initialize.active_proxy:
            sys.exit("ERROR: Active proxy in use. Use 'quick-proxy-deployer destroy' to destroy active proxy before deploying. If this error is incorrect, delete the \"active-proxy\" folder and ensure all resources are removed via EC2 console.")
        if not initialize.active_proxy:
            deploy()

    if action == "destroy":
        if not initialize.active_proxy:
            sys.exit("ERROR: No active proxy detected to destroy. Missing \"active-proxy\" folder from current directory. If this error is incorrect, manually remove all resources via EC2 console.")
        elif initialize.active_proxy:
            destroy()
            shutil.rmtree("active-proxy")

    if action == "status":
        if not initialize.active_proxy:
            sys.exit("STATUS: No active-proxy detected or \"active-proxy\" folder has moved.")


def cli_usage_info():
    return '''quick-proxy-deployer action [flag] <"value">

    ACTIONS:
        [deploy,        Deploy proxy using standard defaults..............................]
        [destroy,       Destroy active proxy resources from AWS...........................]

    FLAGS:
        [-r, --region   Specify AWS region to deploy proxy in.............................]
        [-p, --permit   Permit additional user via comma-separated IPv4 CIDR notation.....]

    REGIONS:
        'us-east-2':'US East (Ohio)'                   |   'ap-northeast-1':'Asia Pacific (Tokyo)'
        'us-east-1':'US East (N. Virginia)'            |   'ca-central-1':'Canada (Central)'
        'us-west-1':'US West (N. California)'          |   'eu-central-1':'Europe (Frankfurt)'
        'us-west-2':'US West (Oregon)'                 |   'eu-west-1':'Europe (Ireland)'
        'ap-south-1':'Asia Pacific (Mumbai)'           |   'eu-west-2':'Europe (London)'
        'ap-northeast-3':'Asia Pacific (Osaka)'        |   'eu-west-3':'Europe (Paris)'
        'ap-northeast-2':'Asia Pacific (Seoul)'        |   'eu-north-1':'Europe (Stockholm)'
        'ap-southeast-1':'Asia Pacific (Singapore)'    |   'sa-east-1':'South America (Sao Paulo)'
        'ap-southeast-2':'Asia Pacific (Sydney)'       |
    '''


@contextmanager
def suppress_output():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def process_cidr_block_argument(raw_cidr_argument):
    """Take cidr_block argument, validate the address(es), and format them for .tf usage."""

    if not raw_cidr_argument:
        return f"\"{initialize.public_ip}/32\""

    cidr_regex = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}")
    cidr_match = cidr_regex.findall(raw_cidr_argument)

    if not cidr_match:
        sys.exit('ERROR: Incorrect input to -p permit flag.\nExample usage: quick-proxy-deployer deploy -p "8.8.8.8/32,1.1.1.1/32"')

    for match in cidr_match:
        try:
            subnet = ipaddress.ip_network(match)
            if not subnet.is_global:
                sys.exit('ERROR: Incorrect input to -p permit flag (private addresses are not allowed).\nExample usage: quick-proxy-deployer deploy -p "8.8.8.8/32,1.1.1.1/32"')
        except Exception:
            sys.exit('ERROR: Incorrect input to -p permit flag.\nExample usage: quick-proxy-deployer deploy -p "8.8.8.8/32,1.1.1.1/32"')

    cidr_string_format_list = []

    for address in cidr_match:
        address = f"\"{address}\""
        cidr_string_format_list.append(address)

    cidr_fully_formatted = "/32,".join(cidr_string_format_list)

    return cidr_fully_formatted


if __name__ == "__main__":
    # Go through all system checks to verify environment is ready and determine if a proxy server is active.
    initialize = InitializeScript()

    if not shutil.which("terraform"):
        terraform_location = f"{os.getcwd()}/terraform"
    elif shutil.which("terraform"):
        terraform_location = shutil.which("terraform")

    # Parse CLI arguments.
    parser = argparse.ArgumentParser(
        description="Quick Proxy Deployer rapidly deploys an AWS EC2 hosted proxy to user specified configuration and allows easy updating of the proxy server without direct interaction.",
        usage=cli_usage_info())
    parser.add_argument("action", type=str, choices=["deploy", "destroy", "status"])
    parser.add_argument("-r", "--region", action="store", dest="region", default="")
    parser.add_argument("-p", "--permit", action="store", dest="cidr_blocks", default="")
    args = vars(parser.parse_args())
    public_ip = initialize.public_ip

    # Establish CLI arguments; use default region and cidr_blocks if not provided; format and validate cidr_blocks input if provided
    action = args["action"]
    region = args["region"]
    cidr_blocks = process_cidr_block_argument(args["cidr_blocks"])

    # Set default region us-east-1
    if not region:
        region = "us-east-1"

    main()
