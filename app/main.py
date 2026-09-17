from fastapi import FastAPI

app = FastAPI(title="Dispute Triage Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
