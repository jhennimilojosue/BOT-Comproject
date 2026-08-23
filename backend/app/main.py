from fastapi import FastAPI

from app.api.routes import cases, processing, responsibles, uploads

app = FastAPI(
    title="BOT-COMProject API",
    description="API for processing Aranda cases and generating time estimations",
    version="0.1.0"
)

app.include_router(responsibles.router)
app.include_router(uploads.router)
app.include_router(cases.router)
app.include_router(processing.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
