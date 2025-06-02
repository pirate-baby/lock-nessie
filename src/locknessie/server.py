import datetime
import pytz
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from locknessie.settings import safely_get_settings
import locknessie.main as main

settings = safely_get_settings()

app = FastAPI()

@app.get("/v1/secret/data/{secret_name}")
async def get_secret(secret_name: str):
    try:
        assert secret_name == settings.secret_name
    except AssertionError:
        raise HTTPException(status_code=400, detail="Invalid secret name")
    token = main.LockNessie().get_token()
    now = datetime.datetime.now(pytz.utc).isoformat() + "Z"
    response = {
        "data": {
            "data": {
                secret_name: token
            },
            "metadata": {
                "created_time": now,
                "custom_metadata": None,
                "deletion_time": "",
                "destroyed": False,
                "version": 1
            }
        }
    }
    return JSONResponse(content=response)

