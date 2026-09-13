"""
NETRYX EVIDENCE — IOC & Entity Worker (Celery)
Extracts Indicators of Compromise (IPs, Domains, Hashes, Emails) and
Entities (Persons, Orgs, Locations) from raw text/metadata using Regex and NLP.
Enriches IOCs via external Threat Intel (simulated VirusTotal, MISP, Shodan).
"""

import re
import asyncio
from celery import shared_task
from datetime import datetime, timezone

from app.core.database import async_session
from app.models.evidence import Evidence
from app.models.ioc import IOC
from app.models.entity import Entity
from app.models.timeline_event import TimelineEvent
from app.core.events import event_bus


# ── Regex Patterns ─────────────────────────────────────────────
IOC_PATTERNS = {
    "ipv4": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "domain": r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]\b",
    "md5": r"\b[a-fA-F0-9]{32}\b",
    "sha256": r"\b[a-fA-F0-9]{64}\b",
}


# ── Threat Intel Simulator ─────────────────────────────────────
async def enrich_ioc(ioc_type: str, value: str) -> dict:
    """Simulate VirusTotal / Shodan lookup."""
    await asyncio.sleep(0.5)
    
    # Fake threat intel logic based on value to create deterministic mock data
    is_malicious = "urgent" in value.lower() or "192.168" not in value
    
    if ioc_type == "ipv4":
        return {
            "vt_score": "5/94" if is_malicious else "0/94",
            "shodan_ports": [80, 443, 22] if not is_malicious else [3389, 4444],
            "asn": "AS12345 Suspicious Hosting",
            "country": "RU" if is_malicious else "US",
        }
    elif ioc_type == "domain":
        return {
            "vt_score": "12/94" if is_malicious else "0/94",
            "creation_date": "2025-05-01",
            "registrar": "Namecheap",
        }
    
    return {"vt_score": "0/94"}


# ── Core Worker Logic ──────────────────────────────────────────
async def extract_and_enrich_async(payload: dict):
    evidence_id = payload.get("evidence_id")
    case_id = payload.get("case_id")
    results = payload.get("analysis_results", {})
    
    print(f"🔍 Starting IOC & Entity extraction for {evidence_id}")

    async with async_session() as session:
        # Extract text to search
        text_to_search = ""
        
        # Pull from OCR
        if "ocr_text" in results:
            text_to_search += " " + results["ocr_text"]
            
        # Pull from Doc summary/text
        if "summary" in results:
            text_to_search += " " + results["summary"]
            
        # Pull from email headers
        if "headers" in results:
            headers = results["headers"]
            text_to_search += f" {headers.get('From', '')} {headers.get('To', '')} {headers.get('Subject', '')}"
            
            # Create Timeline Event for email sent/received
            if "Date" in headers:
                try:
                    dt = datetime.strptime(headers["Date"], "%Y-%m-%dT%H:%M:%S%z")
                    session.add(TimelineEvent(
                        case_id=case_id,
                        evidence_id=evidence_id,
                        event_type="email.sent",
                        timestamp=dt,
                        description=f"Email sent from {headers.get('From')} to {headers.get('To')}"
                    ))
                except Exception:
                    pass

        # 1. Regex Extraction (IOCs)
        found_iocs = []
        for ioc_type, pattern in IOC_PATTERNS.items():
            matches = set(re.findall(pattern, text_to_search))
            for match in matches:
                if ioc_type == "ipv4" and match.startswith(("10.", "192.168.", "172.16.", "127.")):
                    continue # Skip private IPs
                
                enrichment = await enrich_ioc(ioc_type, match)
                risk = "high" if int(enrichment.get("vt_score", "0").split("/")[0]) > 0 else "info"
                
                ioc = IOC(
                    case_id=case_id,
                    evidence_id=evidence_id,
                    type=ioc_type,
                    value=match,
                    normalized_value=match.lower(),
                    risk=risk,
                    enrichment=enrichment,
                    source="netryx_regex_engine"
                )
                session.add(ioc)
                found_iocs.append(ioc)

        # 2. NLP Entity Extraction (from doc intelligence)
        if "entities_found" in results:
            for ent in results["entities_found"]:
                entity = Entity(
                    case_id=case_id,
                    evidence_id=evidence_id,
                    type=ent["type"],
                    name=ent["value"],
                    normalized_name=ent["value"].lower(),
                    confidence=ent["confidence"],
                    source="netryx_ner_engine"
                )
                session.add(entity)

        await session.commit()
        
        print(f"✅ Extracted {len(found_iocs)} IOCs and saved to database.")

        # Trigger Graph Correlation
        await event_bus.emit("correlation.requested", {
            "case_id": case_id,
            "evidence_id": evidence_id
        })


@shared_task(name="analysis.ioc_extraction")
def ioc_extraction_task(payload: dict):
    asyncio.run(extract_and_enrich_async(payload))
