"""
Database models and schema definitions for TrueMark using SQLAlchemy 2.x.

Defines:
- Base: Shared DeclarativeBase for TrueMark ORM models.
- Claim: Statement or claim submitted for verification.
- EvidenceItem: External evidence retrieved from authoritative sources.
- VerificationResult: Verdict, confidence score, and explanation produced by AI analysis.

Note:
- Table creation is NOT performed on module import.
- Table schemas and migrations are managed via Alembic / migration tools.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared DeclarativeBase for all TrueMark ORM models."""
    pass


class Claim(Base):
    """
    Represents a factual statement or claim submitted for verification.
    """
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        server_default="PENDING",
        nullable=False,
    )

    # Relationships
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="claim",
        cascade="all, delete-orphan",
    )
    verification_results: Mapped[list["VerificationResult"]] = relationship(
        "VerificationResult",
        back_populates="claim",
        cascade="all, delete-orphan",
    )

    @property
    def verification_result(self) -> Optional["VerificationResult"]:
        """Return the most recent verification result, if any."""
        return self.verification_results[-1] if self.verification_results else None

    @verification_result.setter
    def verification_result(self, value: Optional["VerificationResult"]) -> None:
        """Set or update the verification result."""
        if value is None:
            self.verification_results.clear()
        else:
            self.verification_results = [value]

    def __repr__(self) -> str:
        preview = (self.text[:37] + "...") if len(self.text) > 40 else self.text
        return f"<Claim(id={self.id!r}, status={self.status!r}, text={preview!r})>"


class EvidenceItem(Base):
    """
    Represents an external piece of evidence retrieved to verify a claim.
    """
    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to parent Claim
    claim: Mapped["Claim"] = relationship("Claim", back_populates="evidence_items")

    def __repr__(self) -> str:
        return (
            f"<EvidenceItem(id={self.id!r}, claim_id={self.claim_id!r}, "
            f"source_url={self.source_url[:30]!r})>"
        )


class VerificationResult(Base):
    """
    Represents the synthesized analysis, verdict, and explanation for a claim.
    """
    __tablename__ = "verification_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    verdict: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to parent Claim
    claim: Mapped["Claim"] = relationship("Claim", back_populates="verification_results")

    def __repr__(self) -> str:
        return (
            f"<VerificationResult(id={self.id!r}, claim_id={self.claim_id!r}, "
            f"verdict={self.verdict!r}, confidence_score={self.confidence_score!r})>"
        )


__all__ = [
    "Base",
    "Claim",
    "EvidenceItem",
    "VerificationResult",
]
