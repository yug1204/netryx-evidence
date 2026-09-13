"""
NETRYX EVIDENCE — Graph API Endpoints
Endpoints for querying the Neo4j Investigation Graph.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from neo4j import AsyncGraphDatabase

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.user import User

router = APIRouter(prefix="/graph", tags=["Investigation Graph"])
settings = get_settings()

@router.get("/case/{case_id}", response_model=Dict[str, Any])
async def get_case_graph(
    case_id: int,
    limit: int = Query(100, ge=10, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the investigation graph for a specific case.
    Returns nodes and edges formatted for Cytoscape.js.
    """
    # Verify access to case
    from app.api.v1.cases import _get_case_or_404
    await _get_case_or_404(db, case_id, current_user)

    # In production, this connects to Neo4j.
    # For now, we'll return a rich mock dataset simulating a phishing investigation.
    
    nodes = [
        {"data": {"id": "ev1", "label": "email_01.eml", "type": "evidence", "risk": 45}},
        {"data": {"id": "ev2", "label": "wire_instructions.pdf", "type": "evidence", "risk": 95}},
        {"data": {"id": "ent1", "label": "John Doe", "type": "person", "risk": 10}},
        {"data": {"id": "ent2", "label": "Shell Corp LLC", "type": "organization", "risk": 80}},
        {"data": {"id": "ioc1", "label": "192.168.100.45", "type": "ipv4", "risk": 100}},
        {"data": {"id": "ioc2", "label": "ceo-urgent@company-portal-update.com", "type": "email", "risk": 98}},
        {"data": {"id": "ioc3", "label": "company-portal-update.com", "type": "domain", "risk": 85}},
        {"data": {"id": "ioc4", "label": "45.33.22.11", "type": "ipv4", "risk": 95}},
    ]
    
    edges = [
        {"data": {"source": "ev1", "target": "ioc2", "label": "CONTAINS"}},
        {"data": {"source": "ev1", "target": "ev2", "label": "ATTACHED_TO"}},
        {"data": {"source": "ev2", "target": "ent2", "label": "MENTIONS"}},
        {"data": {"source": "ev2", "target": "ent1", "label": "MENTIONS"}},
        {"data": {"source": "ioc2", "target": "ioc3", "label": "PART_OF"}},
        {"data": {"source": "ioc3", "target": "ioc4", "label": "RESOLVES_TO"}},
        {"data": {"source": "ioc4", "target": "ioc1", "label": "COMMUNICATES_WITH"}},
    ]
    
    return {
        "nodes": nodes,
        "edges": edges
    }
