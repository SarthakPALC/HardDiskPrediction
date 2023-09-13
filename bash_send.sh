# Collect SMART data and process it with jq
sda_data=$(smartctl -A -j /dev/sda | jq --arg fallbackValue "null" '
  .ata_smart_attributes.table
  | reduce .[] as $item (
      {};
      . += {
        ("timestamp"): (now | strftime("%Y-%m-%d %H:%M:%S")),
        ("smart_\($item.id)_normalized"): ($item.value // $fallbackValue),
        ("smart_\($item.id)_raw"): ($item.raw.value // $fallbackValue)
      }
    )
')

# Collect data from /dev/sdc
sdc_data=$(smartctl -A -j /dev/sdc | jq --arg fallbackValue "null" '
  .ata_smart_attributes.table
  | reduce .[] as $item (
      {};
      . += {
        ("timestamp"): (now | strftime("%Y-%m-%d %H:%M:%S")),
        ("smart_\($item.id)_normalized"): ($item.value // $fallbackValue),
        ("smart_\($item.id)_raw"): ($item.raw.value // $fallbackValue)
      }
    )
')

# Combine the data from both partitions into a single array
output=$(jq -n --argjson sda_data "$sda_data" --argjson sdc_data "$sdc_data" '
  { "sda": $sda_data, "sdc": $sdc_data }
')


# Combine the data from both partitions into a single JSON object
combined_data="{\"sda\": $sda_data, \"sdc\": $sdc_data}"

# Save the combined data to smart_data_combined.json
echo "$combined_data" > smart_data_combined.json

# Read the JSON data from the file
json_data=$(cat smart_data_combined.json)

# Define the FastAPI server URL
api_url="http://127.0.0.1:8000/getInformation"

# Make a POST request to the server with the JSON payload
curl -X POST -H "Content-Type: application/json" -d "$json_data" "$api_url"

