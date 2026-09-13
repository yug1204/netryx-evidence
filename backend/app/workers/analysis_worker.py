"""
NETRYX EVIDENCE — Analysis Worker (Celery)
Dedicated workers for Image, Document, and Email intelligence.
Integrates with AI models (CLIP, YOLO, Tesseract) and NLP engines.
"""

import asyncio
from typing import Dict, Any
from celery import shared_task
from datetime import datetime, timezone

from app.core.database import async_session
from app.models.evidence import Evidence
from app.models.entity import Entity
from app.models.audit_log import AuditLog
from app.core.events import event_bus


# ── AI Engine Simulators (In Production, use actual ML inference) ──

async def extract_image_intelligence(file_bytes: bytes, metadata: dict) -> Dict[str, Any]:
    """
    Simulate Image Intelligence Pipeline:
    1. EXIF Extraction (GPS, Camera, Dates)
    2. OCR (Tesseract) for text in image
    3. YOLO Object Detection
    4. CLIP Embeddings (handled in embedding_worker)
    """
    await asyncio.sleep(2)  # Simulate GPU processing time
    
    return {
        "engine": "netryx_vision_v2",
        "objects_detected": ["laptop", "smartphone", "document"],
        "ocr_text": "CONFIDENTIAL: Project Phoenix timeline...",
        "nsfw_score": 0.01,
        "exif": {
            "Make": "Apple",
            "Model": "iPhone 15 Pro",
            "DateTimeOriginal": "2025-05-09 14:22:01",
            "GPS": {"lat": 28.6139, "lon": 77.2090}  # New Delhi
        }
    }


async def extract_document_intelligence(file_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    """
    Simulate Document Intelligence Pipeline (PDF, DOCX):
    1. Text extraction (PyMuPDF, python-docx)
    2. NER (Named Entity Recognition via SpaCy)
    3. Macro/Malware detection for Office docs
    """
    await asyncio.sleep(2)
    
    return {
        "engine": "netryx_doc_intel_v1",
        "word_count": 4512,
        "language": "en",
        "has_macros": False,
        "summary": "Financial report detailing unauthorized offshore transfers.",
        "entities_found": [
            {"type": "person", "value": "John Doe", "confidence": 0.98},
            {"type": "organization", "value": "Shell Corp LLC", "confidence": 0.95},
            {"type": "money", "value": "$1,450,000", "confidence": 0.99}
        ]
    }


async def extract_email_intelligence(file_bytes: bytes) -> Dict[str, Any]:
    """
    Simulate Email Intelligence Pipeline (EML, MSG):
    1. Header parsing (SPF, DKIM, DMARC)
    2. Routing path analysis
    3. Phishing classifier (LLM/ML based)
    """
    await asyncio.sleep(1)
    
    return {
        "engine": "netryx_mail_intel_v1",
        "headers": {
            "From": "ceo-urgent@company-portal-update.com",
            "To": "finance@target-company.com",
            "Subject": "URGENT: Wire Transfer Required",
            "Date": "2025-05-10T09:14:00Z"
        },
        "authentication": {
            "SPF": "fail",
            "DKIM": "none",
            "DMARC": "fail"
        },
        "phishing_score": 98,
        "attachments": ["wire_instructions.pdf"]
    }


# ── Core Worker Logic ──────────────────────────────────────────

async def run_analysis_pipeline(payload: dict, analysis_type: str):
    """Generic orchestrator for running specific analysis pipelines."""
    evidence_id = payload.get("evidence_id")
    
    print(f"🧠 Running {analysis_type} intelligence on {evidence_id}")

    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(Evidence).where(Evidence.id == evidence_id))
        evidence = result.scalar_one_or_none()
        
        if not evidence:
            return

        # Fetch bytes from MinIO
        from app.services.storage import storage
        try:
            file_bytes = storage.download_file(evidence.storage_path)
        except Exception as e:
            print(f"Failed to download {evidence_id} for analysis: {e}")
            return

        # Run appropriate AI engine
        results = {}
        if analysis_type == "image":
            results = await extract_image_intelligence(file_bytes, evidence.metadata)
        elif analysis_type == "document":
            results = await extract_document_intelligence(file_bytes, evidence.mime_type)
        elif analysis_type == "email":
            results = await extract_email_intelligence(file_bytes)
            
            # If high phishing score, adjust evidence risk
            if results.get("phishing_score", 0) > 80:
                evidence.risk_score = max(evidence.risk_score or 0, 95)
                evidence.is_malicious = True
        
        # Save results to JSONB
        existing_results = evidence.analysis_results or {}
        existing_results[f"{analysis_type}_intelligence"] = results
        evidence.analysis_results = existing_results
        
        await session.commit()
        
        print(f"✅ Completed {analysis_type} intelligence for {evidence_id}")

        # Trigger downstream entity extraction
        # Pass the extracted text/results for IOC/Entity extraction
        extraction_payload = payload.copy()
        extraction_payload["analysis_results"] = results
        
        await event_bus.emit("analysis.ioc_extraction.requested", extraction_payload)


# ── Celery Task Entrypoints ────────────────────────────────────

@shared_task(name="analysis.image")
def process_image_task(payload: dict):
    asyncio.run(run_analysis_pipeline(payload, "image"))


@shared_task(name="analysis.document")
def process_document_task(payload: dict):
    asyncio.run(run_analysis_pipeline(payload, "document"))


@shared_task(name="analysis.email")
def process_email_task(payload: dict):
    asyncio.run(run_analysis_pipeline(payload, "email"))
