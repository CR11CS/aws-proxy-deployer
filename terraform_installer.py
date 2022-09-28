#!/usr/bin/env python3
import os
import platform
import re
import requests
import wget
import zipfile

OPERATING_SYSTEM = os.name
MACHINE_IS_64BIT = '64' in platform.architecture()[0]
TERRAFORM_BASE_URL = 'https://releases.hashicorp.com/terraform/'


def get_latest_version_url_prefix():
    """Grabs and returns the latest version of Terraform that is not alpha, beta, or rc."""
    page_content_text = requests.get(TERRAFORM_BASE_URL).text
    terraform_page_content_html_stripped = (re.sub('<[^<]+?>', '', page_content_text))
    terraform_version_regex = re.compile('(\d+)\.(\d+)\.(\d+)[^-alpha|beta|rc]')
    latest_stable_version = (terraform_version_regex.search(terraform_page_content_html_stripped))[0].strip()
    return TERRAFORM_BASE_URL + latest_stable_version + '/'


def get_os_version_url_suffix():
    """Grabs and returns the correct version of Terraform for your operating system."""
    page_content_text = requests.get(get_latest_version_url_prefix()).text
    terraform_subpage_content_html_stripped = (re.sub('<[^<]+?>', '', page_content_text))

    if MACHINE_IS_64BIT:
        if OPERATING_SYSTEM == 'nt':
            terraform_os_version = re.compile('.*windows_amd64\.zip').search(terraform_subpage_content_html_stripped)
        elif OPERATING_SYSTEM == 'posix':
            terraform_os_version = re.compile('.*linux_amd64\.zip').search(terraform_subpage_content_html_stripped)

    if not MACHINE_IS_64BIT:
        if OPERATING_SYSTEM == 'nt':
            terraform_os_version = re.compile('.*windows_386\.zip').search(terraform_subpage_content_html_stripped)
        elif OPERATING_SYSTEM == 'posix':
            terraform_os_version = re.compile('.*linux_386\.zip').search(terraform_subpage_content_html_stripped)
    return terraform_os_version[0].strip()


def download_terraform_latest():
    """Downloads your Terraform .exe or .bin to the current working directory."""
    prefix = get_latest_version_url_prefix()
    suffix = get_os_version_url_suffix()
    download_url = prefix + suffix
    wget.download(download_url, 'terraform.zip')


def unzip_terraform_and_clean():
    """Unzips Terraform .zip file and removes it, keeping the contents."""
    with zipfile.ZipFile('terraform.zip', 'r') as zip_ref:
        zip_ref.extractall(os.getcwd())
    os.remove('terraform.zip')


def install_terraform():
    """Downloads Terraform then unzips and removes zip file."""
    download_terraform_latest()
    unzip_terraform_and_clean()


if __name__ == "__main__":
    install_terraform()
    print("Terraform installer executed independently.")
