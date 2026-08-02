from fastapi import FastAPI

app = FastAPI(
    title="FinLens Backend",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "FinLens Backend Running"}
