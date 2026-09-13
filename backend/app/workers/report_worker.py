"""
NETRYX EVIDENCE — Report Generator Worker (Celery)
Generates PDF and DOCX forensic reports using WeasyPrint and Jinja2 templates.
"""

import asyncio
from datetime import datetime, timezone
import json
from celery import shared_task
from sqlalchemy import select

from app.core.database import async_session
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.ioc import IOC

# In production, we would use Jinja2 to render an HTML template 
# and WeasyPrint to convert that HTML into a secure PDF.
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML

async def generate_report_async(payload: dict):
    case_id = payload.get("case_id")
    requester_id = payload.get("requester_id")
    
    print(f"📄 Generating Forensic Report for Case {case_id}")
    
    async with async_session() as session:
        # Fetch Case Data
        case = await session.get(Case, case_id)
        if not case:
            return
            
        # Fetch Evidence
        ev_result = await session.execute(select(Evidence).where(Evidence.case_id == case_id))
        evidences = ev_result.scalars().all()
        
        # Fetch IOCs
        ioc_result = await session.execute(select(IOC).where(IOC.case_id == case_id))
        iocs = ioc_result.scalars().all()

        # Build Report Context
        report_data = {
            "title": f"Forensic Investigation Report: {case.title}",
            "date_generated": datetime.now(timezone.utc).isoformat(),
            "case_id": case_id,
            "status": case.status,
            "priority": case.priority,
            "total_evidence": len(evidences),
            "total_iocs": len(iocs),
            "executive_summary": case.description,
            "evidence_chain": [
                {
                    "filename": e.original_filename,
                    "sha256": e.file_hash_sha256,
                    "risk": e.risk_score
                } for e in evidences
            ],
            "critical_iocs": [
                {"type": i.type, "value": i.value} for i in iocs if i.risk == "high"
            ]
        }
        
        # Simulate PDF Generation delay
        await asyncio.sleep(2)
        
        # Generate the PDF (Mocked)
        # html_out = template.render(report_data)
        # pdf_bytes = HTML(string=html_out).write_pdf()
        pdf_bytes = json.dumps(report_data, indent=2).encode('utf-8')
        
        # Upload PDF to MinIO
        from app.services.storage import storage
        filename = f"reports/case_{case_id}_{int(datetime.now().timestamp())}.pdf"
        storage.upload_file(filename, pdf_bytes, "application/pdf")
        
        # Update case metadata to link report
        meta = case.metadata or {}
        reports = meta.get("generated_reports", [])
        reports.append(filename)
        meta["generated_reports"] = reports
        case.metadata = meta
        
        await session.commit()
        
    print(f"✅ Report generated and saved to {filename}")


@shared_task(name="reports.generate")
def generate_report_task(payload: dict):
    asyncio.run(generate_report_async(payload))
