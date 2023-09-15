#!/bin/bash

# Read the partition name from user input
read -p "Enter the partition name (e.g., /dev/sdX): " user_partition

# Check if the specified partition exists
if [ ! -e "$user_partition" ]; then
  echo "Partition $user_partition not present. Exiting."
  exit 1
fi

function collect_and_send_data {
  # Collect SMART data and process it with jq for the selected partition
  partition="$1"

  serial_no=$(smartctl -i "$partition" | grep -oP 'Serial Number:\s+\K\S+')
  device_model=$(smartctl -i "$partition" | grep -oP 'Device Model:\s+\K\S+')
  partition_data=$(smartctl -A -j "$partition" | jq --arg serial "$serial_no" --arg model "$device_model" --arg fallbackValue "null" '
    .ata_smart_attributes.table
    | reduce .[] as $item (
        {};
        . += {
          ("serial_no"): $serial,
          ("device_model"): $model,
          ("timestamp"): (now | strftime("%Y-%m-%d %H:%M:%S")),
          ("smart_\($item.id)_normalized"): ($item.value // $fallbackValue),
          ("smart_\($item.id)_raw"): ($item.raw.value // $fallbackValue)
        }
      )
  ')
  # Define the FastAPI server URL
  api_url="http://127.0.0.1:8000/getInformation"
  # Make a POST request to the server with the JSON payload
  response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "{\"$partition\": $partition_data}" "$api_url")
  http_code=$(echo "$response" | tail -n1)
  if [ "$http_code" -eq 200 ]; then
    echo "Data sent successfully for $partition"
  else
    echo "Error: $http_code"
  fi
}
while true
do
  collect_and_send_data "$user_partition"
  if [ $? -ne 0 ]; then
    echo "Error collecting and sending data. Retrying in 5 seconds..."
  fi
  sleep 10
done

