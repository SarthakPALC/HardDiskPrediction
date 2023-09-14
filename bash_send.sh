#!/bin/bash

function collect_and_send_data {
  # Collect SMART data and process it with jq for /dev/sdc
  partition="/dev/sdc"

  if [ -e "$partition" ]; then
    serial_no=$(smartctl -i "$partition" | grep -oP 'Serial Number:\s+\K\S+')
    device_model=$(smartctl -i "$partition" | grep -oP 'Device Model:\s+\K\S+')
    sdc_data=$(smartctl -A -j "$partition" | jq --arg serial "$serial_no" --arg model "$device_model" --arg fallbackValue "null" '
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
    response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "{\"sdc\": $sdc_data}" "$api_url")
    http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" -eq 200 ]; then
      echo "Data sent successfully"
    else
      echo "Error: $http_code"
    fi
  else
    echo "Partition $partition not present. Exiting."
    exit 1
  fi
}

read -p "Continue with collecting data for /dev/sdc? (yes/no): " user_input

if [ "$user_input" = "yes" ]; then
  while true
  do
    collect_and_send_data
    sleep 300
  done
else
  echo "Data collection aborted."
fi

