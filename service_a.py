from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
RESULTS_DB = []  

class ResultData(BaseModel):
    url: str
    count: int

@app.post("/results")
def save_result(data: ResultData):
    RESULTS_DB.append(data.dict())
    print(f" [A] Zapisano wynik: {data.count} osób dla {data.url}")
    return {"status": "saved", "total_records": len(RESULTS_DB)}

@app.get("/results")
def get_results():
    return RESULTS_DB