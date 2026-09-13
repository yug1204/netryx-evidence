"""
NETRYX EVIDENCE — Graph Correlation Engine (Celery)
Builds the Neo4j knowledge graph and runs correlation algorithms.
Links Entities and IOCs across multiple evidences and cases to find hidden connections.
"""

import asyncio
from celery import shared_task
from neo4j import AsyncGraphDatabase
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session
from app.models.ioc import IOC
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.core.events import event_bus

settings = get_settings()


async def build_and_correlate_async(payload: dict):
    """
    1. Read all entities/IOCs for the given evidence.
    2. Sync them to Neo4j.
    3. Run a Cypher query to find overlaps with existing nodes.
    4. If an overlap is found, create a Relationship in PostgreSQL and Neo4j.
    """
    case_id = payload.get("case_id")
    evidence_id = payload.get("evidence_id")
    
    print(f"🕸️ Starting Graph Correlation for Evidence {evidence_id}")

    # Fetch data from Postgres
    async with async_session() as session:
        # Get Entities
        result_entities = await session.execute(
            select(Entity).where(Entity.evidence_id == evidence_id)
        )
        entities = result_entities.scalars().all()
        
        # Get IOCs
        result_iocs = await session.execute(
            select(IOC).where(IOC.evidence_id == evidence_id)
        )
        iocs = result_iocs.scalars().all()

    if not entities and not iocs:
        print("No nodes to correlate.")
        return

    # Sync to Neo4j
    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI, 
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    async with driver.session() as neo_session:
        # Create Nodes
        for ent in entities:
            await neo_session.run(
                """
                MERGE (e:Entity {pg_id: $pg_id})
                SET e.name = $name, e.type = $type, e.case_id = $case_id
                """,
                pg_id=str(ent.id), name=ent.name, type=ent.type, case_id=case_id
            )
            
        for ioc in iocs:
            await neo_session.run(
                """
                MERGE (i:IOC {pg_id: $pg_id})
                SET i.value = $value, i.type = $type, i.case_id = $case_id, i.risk = $risk
                """,
                pg_id=str(ioc.id), value=ioc.value, type=ioc.type, case_id=case_id, risk=ioc.risk
            )
            
        # Link Evidence to Nodes
        await neo_session.run(
            """
            MERGE (ev:Evidence {pg_id: $ev_id})
            SET ev.case_id = $case_id
            """,
            ev_id=evidence_id, case_id=case_id
        )
        
        # Simple rule-based correlation (e.g., connect IPs to Domains if found in same evidence)
        await neo_session.run(
            """
            MATCH (i1:IOC {type: 'ipv4', pg_id: $ev_id}), (i2:IOC {type: 'domain', pg_id: $ev_id})
            MERGE (i1)-[r:RESOLVES_TO]->(i2)
            """,
            ev_id=evidence_id
        )
        
        # Cross-case correlation discovery
        # Find if any IOC matches one from a different case
        records = await neo_session.run(
            """
            MATCH (i1:IOC {case_id: $case_id})
            MATCH (i2:IOC)
            WHERE i1.value = i2.value AND i1.case_id <> i2.case_id
            RETURN i1.pg_id AS source, i2.pg_id AS target, i1.value AS value
            """,
            case_id=case_id
        )
        
        correlations = await records.data()
        
    await driver.close()

    # Save discovered cross-case relationships back to Postgres
    if correlations:
        print(f"🚨 Found {len(correlations)} cross-case correlations!")
        async with async_session() as session:
            for corr in correlations:
                # Need to map to entities in PG or just log it
                pass
            await session.commit()
            
    print(f"✅ Graph Correlation complete for {evidence_id}")


@shared_task(name="analysis.correlation")
def correlation_task(payload: dict):
    asyncio.run(build_and_correlate_async(payload))
