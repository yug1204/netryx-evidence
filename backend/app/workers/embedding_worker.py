"""
NETRYX EVIDENCE — Vector Embedding Worker (Celery)
Generates vector embeddings for evidence text/metadata using OpenAI.
Stores the embeddings in PostgreSQL using the pgvector extension for Semantic Search (RAG).
"""

import asyncio
from celery import shared_task
from openai import AsyncOpenAI
import json

from app.core.config import get_settings
from app.core.database import async_session
from app.models.evidence import Evidence
from app.models.embedding import EvidenceEmbedding

settings = get_settings()

async def generate_embeddings_async(payload: dict):
    """
    Takes analysis results (OCR text, document summaries) and converts 
    them into dense vector embeddings for RAG search.
    """
    evidence_id = payload.get("evidence_id")
    case_id = payload.get("case_id")
    results = payload.get("analysis_results", {})
    
    print(f"🧠 Generating Vector Embeddings for Evidence {evidence_id}")

    # Build the text chunk to embed
    text_chunks = []
    
    if "ocr_text" in results:
        text_chunks.append(f"[OCR Text] {results['ocr_text']}")
        
    if "summary" in results:
        text_chunks.append(f"[Document Summary] {results['summary']}")
        
    if "headers" in results:
        h = results["headers"]
        text_chunks.append(f"[Email] From: {h.get('From')} To: {h.get('To')} Subject: {h.get('Subject')}")

    if not text_chunks:
        print("No meaningful text to embed.")
        return

    full_text = "\n".join(text_chunks)
    
    # In production, use AsyncOpenAI with the real API key.
    # client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    # response = await client.embeddings.create(input=full_text, model="text-embedding-3-small")
    # embedding = response.data[0].embedding
    
    # For simulation, we create a deterministic dummy vector (1536 dimensions)
    # This prevents requiring a real OpenAI API key just to boot the system
    import hashlib
    h = hashlib.md5(full_text.encode()).digest()
    dummy_vector = [(float(b) / 255.0) - 0.5 for b in h] * 96 # 16 bytes * 96 = 1536 dims

    async with async_session() as session:
        # Check if embedding already exists
        from sqlalchemy import select
        existing = await session.execute(
            select(EvidenceEmbedding).where(EvidenceEmbedding.evidence_id == evidence_id)
        )
        emb = existing.scalar_one_or_none()
        
        if emb:
            emb.embedding = dummy_vector
            emb.chunk_text = full_text
        else:
            new_emb = EvidenceEmbedding(
                evidence_id=evidence_id,
                case_id=case_id,
                chunk_index=0,
                chunk_text=full_text,
                embedding=dummy_vector
            )
            session.add(new_emb)
            
        await session.commit()
        
    print(f"✅ Vector embeddings saved to pgvector for {evidence_id}")


@shared_task(name="analysis.embedding")
def embedding_task(payload: dict):
    asyncio.run(generate_embeddings_async(payload))
