from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import joblib
from pymongo import MongoClient
from json.decoder import JSONDecodeError  # Import JSONDecodeError

app = FastAPI(title="SMART Data API")

# Define the correct feature order
feature_order = [
    "smart_198_raw",
    "smart_197_raw",
    "smart_187_raw",
    "smart_5_raw"
]

# Load the one-class SVM model
one_class_svm_model = joblib.load('trained model/one_class_svm_model.pkl')

# MongoDB configuration
mongo_username = "mongoadmin"
mongo_password = "bdung"
database_name = "SMART"
sub_collection = "serial no"

import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

data = {"_id": ObjectId("613f3d7a0d04b3a8da8e5e4f")}
json_data = json.dumps(data, cls=JSONEncoder)


try:
    mongo_client = MongoClient(
        f"mongodb://{mongo_username}:{mongo_password}@172.27.1.162:27017/"
    )
    db = mongo_client[database_name]
    output_collection = db[sub_collection]
    print("MongoDB connection established.")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error connecting to MongoDB: {str(e)}")

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

@app.post("/getInformation")
async def get_information(info: Request):
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

    for key, value in req_info.items():
        smart_5_raw = value.get("smart_5_raw", -1)
        smart_187_raw = value.get("smart_187_raw", -1)
        smart_197_raw = value.get("smart_197_raw", -1)
        smart_198_raw = value.get("smart_198_raw", -1)
        data = {
            "smart_5_raw": smart_5_raw,
            "smart_187_raw": smart_187_raw,
            "smart_197_raw": smart_197_raw,
            "smart_198_raw": smart_198_raw
        }
        print("Received data:", data)
        result_df = predict_failure(data, feature_order)

        # Add 'prediction' field to result_df
        result_dict[key] = {
            "prediction": result_df["predicted_failure"].values[0],  # Get the prediction value
        }

        # You can add other fields from value to result_dict if needed
        result_dict[key].update(value)

        # Convert result_df to JSON
        json_data = result_df.to_json(orient='records')  # Serialize result_df to JSON

        # Load JSON data into a list of dictionaries
        result_list = json.loads(json_data)

        # Add data from req_info[key] to each item in the result_list
        for item in result_list:
            item.update(req_info[key])

        # Insert data into MongoDB
        try:
            serial_no = value.get("serial_no", -1)
            collection = db[serial_no]  # Replace with your desired collection name
            print(result_list)
            collection.insert_many(result_list)  # Insert the result data into MongoDB
            print("Data inserted into MongoDB.")
        except Exception as e:
            print(f"Error inserting data into MongoDB: {str(e)}")

        # You can return the result or do further processing here
        print("Processed data:", json_data)

    return JSONResponse(content=result_dict)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_fetch1:app", host="127.0.0.1", port=8000, reload=True)

