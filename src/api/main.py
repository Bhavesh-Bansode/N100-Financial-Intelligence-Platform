from fastapi import FastAPI

app = FastAPI(title="Nifty100 API")


@app.get("/health")
def health():
    return {"status": "ok"}