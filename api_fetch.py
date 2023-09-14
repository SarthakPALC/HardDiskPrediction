from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pymongo
import json
app = FastAPI(title="SMART Data API")

@app.post("/getInformation")
async def getInformation(info: Request):
    req_info = await info.json()
    for key, value in req_info.items():
        smart_5_norm = value.get("smart_5_normalized", -1)
        smart_5_raw = value.get("smart_5_raw", -1)
        smart_187_norm = value.get("smart_187_normalized", -1)
        smart_187_raw = value.get("smart_187_raw", -1)
        smart_197_norm = value.get("smart_197_normalized", -1)
        smart_197_raw = value.get("smart_197_raw", -1)
        smart_198_norm = value.get("smart_198_normalized", -1)
        smart_198_raw = value.get("smart_198_raw", -1)
        """data = {
                "smart_5_normalized" : smart_5_norm,
                "smart_5_raw" :  smart_5_raw,
                "smart_187_normalized" : smart_187_norm,
                "smart_187_raw" :  smart_187_raw,
                "smart_197_normalized" :  smart_197_norm,
                "smart_197_raw" :  smart_197_raw,
                "smart_198_normalized" :  smart_198_norm,
                "smart_198_raw" :  smart_198_raw
            }"""
        data = {
                "smart_5_raw" :  smart_5_raw,
                "smart_187_raw" :  smart_187_raw,
                "smart_197_raw" :  smart_197_raw,
                "smart_198_raw" :  smart_198_raw
            }
        
        print(data)
        df_year_failure = pd.DataFrame(data)
        one_class_svm_model = joblib.load('trained model/one_class_svm_model.pkl')
        x_year = df_year_failure
        anomaly_predictions_year = one_class_svm_model.predict(x_year)
        result_df = pd.DataFrame({'predicted_failure': anomaly_predictions_year})
        result_df['predicted_failure'] = result_df['predicted_failure'].apply(lambda x: 'not critical' if x == 1 else 'critical')
        print(result_df)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main1:app", host="127.0.0.1", port=8000, reload=True)

