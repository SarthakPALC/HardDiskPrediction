import subprocess
import requests
import json
import time
import os

# Function to list hard drives
def list_hard_drives():
    hard_drives = []

    for root, _, files in os.walk('/dev/'):
        for filename in files:
            if filename.startswith('sd') and len(filename) == 3 and filename[2].isalpha():
                device_path = os.path.join(root, filename)
                hard_drives.append(device_path)

    return hard_drives

# Function to collect SMART data
def collect_data():
    hard_drive_data_list = []
    hard_drive_list = list_hard_drives()
    for device in hard_drive_list:
        try:
            # Collect SMART data for the selected partition
            serial_no = subprocess.check_output(["smartctl", "-i", device]).decode("utf-8")
            serial_no = [line.split(":")[1].strip() for line in serial_no.splitlines() if "Serial Number" in line][0]

            device_model = subprocess.check_output(["smartctl", "-i", device]).decode("utf-8")
            device_model = [line.split(":")[1].strip() for line in device_model.splitlines() if "Device Model" in line][0]

            partition_data = subprocess.check_output(["smartctl", "-A", "-j", device]).decode("utf-8")
            partition_data = json.loads(partition_data)

            # Prepare the data payload
            data = {
                "serial_no": serial_no,
                "storage_drive_model": device_model,
                #"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            for item in partition_data['ata_smart_attributes']['table']:
                data[f"smart_{item['id']}_normalized"] = item['value']
                data[f"smart_{item['id']}_raw"] = item['raw']['value']

            hard_drive_data_list.append({serial_no: data})
        except Exception as e:
            print(f"Error collecting data: {str(e)}")
    return hard_drive_data_list

# Function to post the collected data
def post_data(hard_drive_data_list):
    # Define the FastAPI server URL
    api_url = "http://127.0.0.1:8000/getInformation"

    for hard_drive_data in hard_drive_data_list:
        for serial_no, data in hard_drive_data.items():
            try:
                # Make a POST request to the server with the JSON payload
                response = requests.post(api_url, json={serial_no: data})

                if response.status_code == 200:
                    print(f"Data sent successfully for {serial_no}")
                else:
                    print(f"Error: {response.status_code}")
            except Exception as e:
                print(f"Error posting data: {str(e)}")

if __name__ == "__main__":
    while True:
        hard_drive_data_list = collect_data()
        if not hard_drive_data_list:
            print("No storage drive found")
        else:
            #print("list\n")
            # Get system serial number
            system_serial_number = subprocess.check_output(["sudo", "dmidecode", "-s", "system-serial-number"]).decode("utf-8").strip()
            device_hard_drive_data_list = [{
            system_serial_number:
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "storage_drive": hard_drive_data_list
                }
            }]
            post_data(device_hard_drive_data_list)
        time.sleep(10)

