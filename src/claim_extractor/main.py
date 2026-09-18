from fastapi import FastAPI

from claim_extractor.api.routes import router

app = FastAPI(title="Claim Extractor")
app.include_router(router)
