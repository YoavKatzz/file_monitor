import os
import time
import requests


DIR = r"/file_storage"
FILER_URL = "http://filer:8888"
MASTER_URL = "http://master:9333"


def upload_file(file):
    print("[#] New file detected, attempting upload to SeaweedFS server")
    try:
        filepath = os.path.join(DIR, file)
        
        upload_url = f"{FILER_URL}/Uploads/{file}"
        
        with open(filepath, 'rb') as f:
            response = requests.post(upload_url, files={"file": f})
        
        if response.status_code == 201 or response.status_code == 200:
            print(f"[#] Upload successful!")
        else:
            print(f"[!] Upload Failed due to {response.text}")

    except FileNotFoundError:
        print(f"[!] Error: Local file not found at {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to Filer: {e}")
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")


def get_volume_servers():
    """
    Query the SeaweedFS Master for cluster status.
    Return list of volume server URLs.
    """
    response = requests.get(f"{MASTER_URL}/dir/status", params={"json": "true"})
    response.raise_for_status()
    topology = response.json().get("Topology", {})

    servers = []
    for dc in topology.get("DataCenters", []):
        for rack in dc.get("Racks", []):
            for node in rack.get("DataNodes", []):
                servers.append(node["Url"])

    return servers


def get_used_storage_from_volume(url):
    """
    Query a volume server and read disk usage (filesystem-level).
    """
    response = requests.get(f"http://{url}/status", params={"format": "json"})
    response.raise_for_status()
    data = response.json()

    return data["DiskStatuses"][0]["used"]


def get_total_used_storage():
    """
    Query master, then all volume servers, and sum their used disk space.
    """
    volume_servers = get_volume_servers()

    total_used = 0
    for server in volume_servers:
        used = get_used_storage_from_volume(server)
        total_used += used

    return total_used


def log_storage_state():
    total_used_bytes = get_total_used_storage()
    print(f"[#] SeaweedFS total used storage: {total_used_bytes} ({total_used_bytes / 1024**3:.2f} GB)")


def main():
    stored_files = set(os.listdir(DIR))
    
    while True:
        current_files = set(os.listdir(DIR))
        new_files = current_files - stored_files
        for new_file in new_files:
            upload_file(new_file)
            log_storage_state()
        stored_files = current_files
        time.sleep(1)


if __name__ == "__main__":
    print("[#] Starting file monitor...")
    main()