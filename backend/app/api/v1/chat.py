"""
NETRYX EVIDENCE — Chat API Endpoints (RAG)
Handles chat interactions with the AI Assistant using pgvector similarity search.
"""

import asyncio
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.embedding import EvidenceEmbedding
from app.models.evidence import Evidence

router = APIRouter(prefix="/chat", tags=["AI Assistant"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    case_id: int
    messages: List[ChatMessage]

async def mock_stream_response(query: str, context: str):
    """Simulates an LLM streaming response for UI testing."""
    await asyncio.sleep(0.5)
    
    prompt = f"Based on the query '{query}' and context: {context[:100]}...\n"
    words = [
        "Based", "on", "the", "evidence", "found", "in", "this", "case,", "it", 
        "appears", "that", "the", "IP", "address", "192.168.100.45", "communicated", 
        "with", "a", "known", "malicious", "domain.", "The", "email", "header", 
        "analysis", "also", "shows", "a", "failed", "DMARC", "check,", "indicating", 
        "a", "highly", "probable", "spear-phishing", "attack."
    ]
    
    for word in words:
        yield f"data: {word} \n\n"
        await asyncio.sleep(0.05)
        
    yield "data: [DONE]\n\n"


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    RAG Chat endpoint.
    1. Embeds the user query.
    2. Searches pgvector for the top 3 most relevant evidence chunks.
    3. Streams the response back from the LLM.
    """
    query = req.messages[-1].content
    
    # In production: embed the query using OpenAI
    # For simulation, we create a dummy query vector
    import hashlib
    h = hashlib.md5(query.encode()).digest()
    query_vector = [(float(b) / 255.0) - 0.5 for b in h] * 96 

    # Perform Vector Similarity Search in pgvector using L2 distance (<->)
    # Get top 3 closest chunks in this case
    results = await db.execute(
        select(EvidenceEmbedding, Evidence)
        .join(Evidence, Evidence.id == EvidenceEmbedding.evidence_id)
        .where(EvidenceEmbedding.case_id == req.case_id)
        .order_by(EvidenceEmbedding.embedding.l2_distance(query_vector))
        .limit(3)
    )
    
    rows = results.all()
    
    context = ""
    citations = []
    
    for emb, ev in rows:
        context += f"\n--- Evidence ID {ev.id} ({ev.original_filename}) ---\n"
        context += emb.chunk_text
        citations.append({
            "id": str(ev.id),
            "filename": ev.original_filename
        })

    # Return a streaming response (Server-Sent Events)
    return StreamingResponse(
        mock_stream_response(query, context), 
        media_type="text/event-stream"
    )
