from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import pandas as pd
import joblib
from pymongo import MongoClient
from json.decoder import JSONDecodeError
import json
from bson import ObjectId
import re
from datetime import datetime
from datetime import timedelta


latest_data = {}

app = FastAPI(title="SMART Data API")

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unexpected error: {str(exc)}"},
    )

# Define the correct feature order
feature_order = [
    "smart_198_raw",
    "smart_197_raw",
    "smart_187_raw",
    "smart_5_raw"
]

# Load the one-class SVM model
one_class_svm_model = joblib.load('trained_model/one_class_svm_model.pkl')

# MongoDB configuration
mongo_username = "mongoadmin"
mongo_password = "bdung"
database_name = "SMART"

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

try:
    mongo_client = MongoClient(
        f"mongodb://{mongo_username}:{mongo_password}@172.27.1.162:27017/"
    )
    db = mongo_client[database_name]
    print("MongoDB connection established.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error connecting to MongoDB: {str(e)}")

def clean_collection_name(name):
    # Remove any non-alphanumeric characters from the name
    return re.sub(r'[^a-zA-Z0-9]', '_', name)

def predict_failure(data, feature_order):
    # Create a DataFrame with the input data in the correct order
    df_year_failure = pd.DataFrame({feature: [data[feature]] for feature in feature_order})

    # Make predictions
    anomaly_predictions_year = one_class_svm_model.predict(df_year_failure)

    # Assign binary labels based on anomaly predictions
    predicted_failure = [1 if pred == -1 else 0 for pred in anomaly_predictions_year]

    # Map binary labels to 'critical' and 'not critical'
    result_df = pd.DataFrame({'predicted_failure': predicted_failure})
    result_df['predicted_failure'] = result_df['predicted_failure'].apply(lambda x: 'critical' if x == 1 else 'not critical')

    return result_df

def remove_outdated_entries():
    global latest_data
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    threshold_time = datetime.now() - timedelta(minutes=1)  # Remove entries older than 5 minutes
    keys_to_remove = []
    for serial_no, data in latest_data.items():
        if datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S") < threshold_time:
            keys_to_remove.append(serial_no)
    for key in keys_to_remove:
        del latest_data[key]
    # Ensure that the data is in the correct format for MongoDB
    latest_data = {str(k): v for k, v in latest_data.items()}

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

@app.post("/getInformation")
async def get_information(info: Request):
    global latest_data
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB connection is not established.")
    try:
        req_info = await info.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data in the request body")

    if not req_info:
        raise HTTPException(status_code=400, detail="Request body is empty")
    
    # Create an empty dictionary to store the results
    result_dict = {}

    # Create a list to store filtered SMART attributes for storage drives
    storage_drives_attributes = []

    for key, value in req_info.items():
        for drive_data in value["storage_drive"]:
            #drive_attributes = {}
            for drive_serial, drive_info in drive_data.items():
                # Filter and include only the desired SMART attributes
                filtered_attributes = {
                    "smart_5_raw": drive_info.get("smart_5_raw",-1),
                    "smart_187_raw": drive_info.get("smart_187_raw",-1),
                    "smart_197_raw": drive_info.get("smart_197_raw",-1),
                    "smart_198_raw": drive_info.get("smart_198_raw",-1)
                }

                #prediction
                result_df = predict_failure(filtered_attributes, feature_order)

                # Add 'prediction' field to result_df
                result_dict[drive_serial] = {
                    "prediction": result_df["predicted_failure"].values[0],  # Get the prediction value
                }

            # You can add other fields from value to result_dict if needed
                result_dict[drive_serial].update(drive_info)

        result_list = []
        result_json = json.dumps(result_dict)

        try:
            # Use the serial_no as the sub-collection name after cleaning it
            '''serial_no = clean_collection_name(key)
            collection = db[serial_no]

            # Create a "storage_drives" sub-collection within the "serial_no" collection
            storage_drives_collection = collection["storage_drives"]

            result_list = json.loads(result_json)
            #print(result_list)
            collection.insert_one(result_list)  # Insert the result data into MongoDB'''
            # Use the serial_no as the collection name after cleaning it
            #serial_no = clean_collection_name(key)
            # Get the IP address of the device
            ip_address = info.client.host

            # Modify the serial_no with the IP address
            serial_no = clean_collection_name(key) + "_" + ip_address

            #collection = db[serial_no]
            collection = db["Device"]

            # Convert result_dict to a list of storage drives
            storage_drives = list(result_dict.values())

            '''# Insert the result data into MongoDB
            collection.insert_one({"serial_no": serial_no,"storage_drives": storage_drives})'''

            # Get the current date and time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert the result data into MongoDB
            #collection.insert_one({"serial_no": serial_no, "storage_drives": storage_drives, "timestamp": current_time})

            #latest_data = [d for d in latest_data if d['serial_no'] != serial_no]  # Remove the old data for this serial_no
            #latest_data.append({"serial_no": serial_no, "storage_drives": storage_drives, "timestamp": current_time})  # Add the new data

            latest_data[serial_no] = {"storage_drives": storage_drives, "timestamp": current_time}

            #print(f"latest_data\n{latest_data}\n")
            # Assuming `data` is your dictionary
            latest_data = {k: v for k, v in latest_data.items() if k != '_id'}
            remove_outdated_entries()
            #data = list(latest_data)
            print(f"latest_data\n{latest_data}\n")
            collection.insert_one(latest_data,bypass_document_validation=True)
            #collection.insert_one(list(latest_data.values()), bypass_document_validation=True)

            print("Data inserted into MongoDB.")

            # You can return the result or do further processing here
            print("\nProcessed data: ", result_list)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error inserting data into MongoDB: {str(e)}")

        return JSONResponse(content=result_json)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_fetch:app", host="0.0.0.0", port=8000, reload=True)
