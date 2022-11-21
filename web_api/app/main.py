from fastapi import FastAPI, Request
from datetime import datetime
from utils import (
    get_exchangerate,
    get_all_coin_exchangerate_from_cache,
    services_healthy,
)

app = FastAPI()


@app.get("/api/exchangerate")
async def pair_exchangerate(request: Request):
    queryparam = request.query_params
    rate = get_exchangerate(queryparam["pairs"])
    return {"exchangerate": rate}


@app.get("/api/all_exchangerates")
async def get_all_exchangerate():
    response = get_all_coin_exchangerate_from_cache()
    return response


@app.get("/api/services/")
async def get_services_healthy():
    status, updated_time = services_healthy()
    updated_time = datetime.fromtimestamp(updated_time).strftime(
        "/%Y/%m/%d, %H:%M:%S"
    )
    return {"healthy": status, "last update": updated_time}

