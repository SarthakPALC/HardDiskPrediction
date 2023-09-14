from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from prediction import predict_failure
import json
app = FastAPI(title="SMART Data API")
import pandas as pd
import joblib

import pandas as pd
import joblib

def predict_failure(data):
    # Reorder the columns to match the training order
    data = {
        "smart_198_raw": data.get("smart_198_raw", -1),
        "smart_197_raw": data.get("smart_197_raw", -1),
        "smart_187_raw": data.get("smart_187_raw", -1),
        "smart_5_raw": data.get("smart_5_raw", -1),
    }

    series_data = pd.Series(data)

    one_class_svm_model = joblib.load('trained model/one_class_svm_model.pkl')
    x_year = series_data.to_frame().T  # Convert the Series to a DataFrame with one row
    anomaly_predictions_year = one_class_svm_model.predict(x_year)
    result_df = pd.DataFrame({'predicted_failure': anomaly_predictions_year})
    result_df['predicted_failure'] = result_df['predicted_failure'].apply(lambda x: 'critical' if x == 1 else 'not critical')
    return result_df

@app.post("/getInformation")
async def getInformation(info: Request):
    req_info = await info.json()
    for key, value in req_info.items():
        smart_5_raw = value.get("smart_5_raw", -1)
        smart_187_raw = value.get("smart_187_raw", -1)
        smart_197_raw = value.get("smart_197_raw", -1)
        smart_198_raw = value.get("smart_198_raw", -1)
        data = {
                "smart_5_raw" :  smart_5_raw,
                "smart_187_raw" :  smart_187_raw,
                "smart_197_raw" :  smart_197_raw,
                "smart_198_raw" :  smart_198_raw
            }
        print(data)
        result_df = predict_failure(data)

        # You can return the result or do further processing here
        print(result_df)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_fetch:app", host="127.0.0.1", port=8000, reload=True)
