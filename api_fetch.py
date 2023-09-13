from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
app = FastAPI(title="SMART Data API")

@app.post("/getInformation")
async def getInformation(info: Request):
    req_info = await info.json()

    # Save JSON data to "new.json" file
    with open("new.json", "w") as json_file:
        json.dump(req_info, json_file)

    return {
        "status": "SUCCESS",
        "data": req_info
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main1:app", host="127.0.0.1", port=8000, reload=True)

