"""
FastAPI application with SSE streaming for the ASQA pipeline.
"""

import json
import asyncio
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from backend.models import AnalyzeRequest
from backend.pipeline_runner import run_pipeline_streaming

app = FastAPI(title="ASQA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    async def event_generator():
        async for event in run_pipeline_streaming(
            code=request.code,
            language=request.language,
            description=request.description,
        ):
            yield {
                "event": event.agent,
                "data": json.dumps(event.model_dump()),
            }
            # Small delay so frontend can render between events
            await asyncio.sleep(0.05)

    return EventSourceResponse(event_generator())
