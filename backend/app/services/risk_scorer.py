"""
NETRYX EVIDENCE — Bayesian Risk Scorer
Calculates dynamic risk scores for cases based on aggregate evidence, IOCs, and graph correlations.
Uses a simplified Bayesian updating model.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.case import Case
from app.models.evidence import Evidence
from app.models.ioc import IOC

class RiskScorer:
    
    @staticmethod
    async def recalculate_case_risk(session: AsyncSession, case_id: int):
        """
        Recalculates the overall risk score (0-100) for a case using Bayesian updates.
        Prior probability is assumed 10% (0.1).
        Evidence and IOCs act as evidence events adjusting the probability.
        """
        case = await session.get(Case, case_id)
        if not case:
            return

        # Fetch evidence risk scores
        ev_result = await session.execute(select(Evidence.risk_score).where(Evidence.case_id == case_id))
        evidence_scores = ev_result.scalars().all()
        
        # Fetch IOC risks
        ioc_result = await session.execute(select(IOC.risk).where(IOC.case_id == case_id))
        ioc_risks = ioc_result.scalars().all()
        
        # Base prior probability of a severe incident (10%)
        prior_prob = 0.1
        
        # For each piece of evidence, update the probability
        # Likelihood modifiers:
        # Score > 90: True Positive Rate 0.9, False Positive Rate 0.1
        # Score > 50: TPR 0.6, FPR 0.3
        
        posterior = prior_prob
        
        for score in evidence_scores:
            s = score or 0
            if s >= 90:
                tpr, fpr = 0.9, 0.1
            elif s >= 50:
                tpr, fpr = 0.6, 0.3
            else:
                tpr, fpr = 0.2, 0.8
                
            # Bayes Theorem: P(A|B) = P(B|A)*P(A) / [P(B|A)*P(A) + P(B|~A)*P(~A)]
            numerator = tpr * posterior
            denominator = numerator + (fpr * (1 - posterior))
            posterior = numerator / denominator if denominator > 0 else posterior

        # Factor in IOCs
        for risk in ioc_risks:
            if risk == "high":
                tpr, fpr = 0.95, 0.05
            elif risk == "medium":
                tpr, fpr = 0.7, 0.3
            else:
                continue
                
            numerator = tpr * posterior
            denominator = numerator + (fpr * (1 - posterior))
            posterior = numerator / denominator if denominator > 0 else posterior

        # Convert back to 0-100 scale
        final_score = int(posterior * 100)
        
        # Assign Priority based on score
        if final_score >= 85:
            case.priority = "critical"
        elif final_score >= 60:
            case.priority = "high"
        elif final_score >= 30:
            case.priority = "medium"
        else:
            case.priority = "low"
            
        # Update case metadata
        meta = case.metadata or {}
        meta["bayesian_risk_score"] = final_score
        case.metadata = meta
        
        await session.commit()
        print(f"📊 Recalculated Case {case_id} Risk: {final_score}/100 ({case.priority})")
        return final_score

risk_scorer = RiskScorer()
