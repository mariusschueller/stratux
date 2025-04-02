import os
import time
import json
import requests

# Define local version file and app directory
LOCAL_VERSION_FILE = "/boot/firmware/skyhound/versions.json"
APP_DIR = "/boot/firmware/skyhound"

# Define the server URL for the version file
SERVER_VERSION_URL = "https://drive.google.com/uc?export=download&id=18zNnCpgUGy0YOnR0JwDqh6c9bl7ZB5MV"

def get_local_versions():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return {}
    with open(LOCAL_VERSION_FILE, "r") as f:
        return json.load(f)

def get_server_versions():
    time.sleep(20)
    response = requests.get(SERVER_VERSION_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch server versions: {response.status_code}")
        return {}

def update_files(server_versions, local_versions):
    for filename, server_info in server_versions.items():
        local_version = local_versions.get(filename, {}).get("version", "0.0.0")
        if server_info["version"] > local_version:
            print(f"Updating {filename} from version {local_version} to {server_info['version']}...")
            download_and_replace(filename, server_info["url"])
            local_versions[filename] = {"version": server_info["version"]}

    # Save updated local versions
    with open(LOCAL_VERSION_FILE, "w") as f:
        json.dump(local_versions, f, indent=4)

def download_and_replace(filename, url):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(APP_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"{filename} updated successfully.")
    else:
        print(f"Failed to download {filename}: {response.status_code}")

if __name__ == "__main__":
    local_versions = get_local_versions()
    server_versions = get_server_versions()
    if server_versions:
        update_files(server_versions, local_versions)

