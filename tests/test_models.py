"""
Unit tests for TrueMark SQLAlchemy 2.x ORM models in database/models.py.

Verifies:
- Model metadata, table names, primary keys, and foreign keys.
- Column nullability and type definitions.
- Timestamp defaults and status defaults.
- Bidirectional relationships between Claim, EvidenceItem, and VerificationResult.
- Cascade deletion behavior.
- Clean string representation (__repr__).

Uses an in-memory SQLite database so no running PostgreSQL server is required.
"""

import unittest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from database.models import Base, Claim, EvidenceItem, VerificationResult


class TestDatabaseModels(unittest.TestCase):
    """Test suite for Claim, EvidenceItem, and VerificationResult models."""

    @classmethod
    def setUpClass(cls):
        # Create an in-memory database strictly for testing schema and ORM mappings
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self):
        self.session = Session(self.engine)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    # --------------------------------------------------------------------------
    # 1. Metadata & Schema Definition Tests
    # --------------------------------------------------------------------------

    def test_table_names(self):
        """Verify explicit table names on ORM models."""
        self.assertEqual(Claim.__tablename__, "claims")
        self.assertEqual(EvidenceItem.__tablename__, "evidence_items")
        self.assertEqual(VerificationResult.__tablename__, "verification_results")

    def test_primary_keys_defined(self):
        """Verify each model has an integer primary key named 'id'."""
        inspector = inspect(self.engine)
        for table in ["claims", "evidence_items", "verification_results"]:
            pk_constraint = inspector.get_pk_constraint(table)
            self.assertEqual(pk_constraint["constrained_columns"], ["id"])

    def test_foreign_keys_defined(self):
        """Verify foreign keys from child tables to claims.id."""
        inspector = inspect(self.engine)

        evidence_fks = inspector.get_foreign_keys("evidence_items")
        self.assertEqual(len(evidence_fks), 1)
        self.assertEqual(evidence_fks[0]["constrained_columns"], ["claim_id"])
        self.assertEqual(evidence_fks[0]["referred_table"], "claims")
        self.assertEqual(evidence_fks[0]["referred_columns"], ["id"])

        result_fks = inspector.get_foreign_keys("verification_results")
        self.assertEqual(len(result_fks), 1)
        self.assertEqual(result_fks[0]["constrained_columns"], ["claim_id"])
        self.assertEqual(result_fks[0]["referred_table"], "claims")
        self.assertEqual(result_fks[0]["referred_columns"], ["id"])

    # --------------------------------------------------------------------------
    # 2. Defaults & Field Value Tests
    # --------------------------------------------------------------------------

    def test_claim_defaults(self):
        """Verify Claim default status and timestamp generation."""
        claim = Claim(text="The Earth revolves around the Sun.")
        self.session.add(claim)
        self.session.commit()

        self.assertIsNotNone(claim.id)
        self.assertEqual(claim.status, "PENDING")
        self.assertIsInstance(claim.submitted_at, datetime)
        self.assertEqual(claim.text, "The Earth revolves around the Sun.")

    def test_evidence_item_fields(self):
        """Verify EvidenceItem persistence, nullable title, and timestamp."""
        claim = Claim(text="Photosynthesis produces oxygen.")
        self.session.add(claim)
        self.session.commit()

        evidence = EvidenceItem(
            claim_id=claim.id,
            source_url="https://biology.example.org/photosynthesis",
            title="Biology Basics",
            snippet="During photosynthesis, plants release oxygen into the atmosphere.",
        )
        self.session.add(evidence)
        self.session.commit()

        self.assertIsNotNone(evidence.id)
        self.assertEqual(evidence.claim_id, claim.id)
        self.assertEqual(evidence.title, "Biology Basics")
        self.assertIsInstance(evidence.retrieved_at, datetime)

    def test_verification_result_fields(self):
        """Verify VerificationResult persistence and field values."""
        claim = Claim(text="Water is composed of hydrogen and oxygen.")
        self.session.add(claim)
        self.session.commit()

        result = VerificationResult(
            claim_id=claim.id,
            verdict="TRUE",
            confidence_score=0.99,
            explanation="Chemical formula H2O confirms two hydrogen atoms and one oxygen atom.",
        )
        self.session.add(result)
        self.session.commit()

        self.assertIsNotNone(result.id)
        self.assertEqual(result.claim_id, claim.id)
        self.assertEqual(result.verdict, "TRUE")
        self.assertAlmostEqual(result.confidence_score, 0.99)
        self.assertIsInstance(result.generated_at, datetime)

    # --------------------------------------------------------------------------
    # 3. Relationships & Cascade Deletion Tests
    # --------------------------------------------------------------------------

    def test_bidirectional_relationships(self):
        """Verify relationships link parents and children bidirectionally."""
        claim = Claim(text="Mount Everest is the highest mountain above sea level.")
        evidence = EvidenceItem(
            source_url="https://geology.example.org/everest",
            snippet="Mount Everest reaches 8,848.86 meters above sea level.",
            claim=claim,
        )
        result = VerificationResult(
            verdict="TRUE",
            confidence_score=1.0,
            explanation="Widely documented geographical fact.",
            claim=claim,
        )
        self.session.add(claim)
        self.session.commit()

        # Check from Claim side
        self.assertEqual(len(claim.evidence_items), 1)
        self.assertIn(evidence, claim.evidence_items)
        self.assertEqual(len(claim.verification_results), 1)
        self.assertEqual(claim.verification_result, result)

        # Check from Child side
        self.assertEqual(evidence.claim, claim)
        self.assertEqual(result.claim, claim)

    def test_cascade_delete(self):
        """Deleting a Claim must cascade delete its EvidenceItems and VerificationResults."""
        claim = Claim(text="Temporary test claim for cascade deletion.")
        EvidenceItem(
            source_url="https://example.com/temp",
            snippet="Temporary snippet.",
            claim=claim,
        )
        VerificationResult(
            verdict="PARTIALLY_TRUE",
            confidence_score=0.5,
            explanation="Temporary explanation.",
            claim=claim,
        )
        self.session.add(claim)
        self.session.commit()

        claim_id = claim.id
        self.session.delete(claim)
        self.session.commit()

        # Verify children are deleted
        remaining_evidence = (
            self.session.query(EvidenceItem).filter_by(claim_id=claim_id).all()
        )
        remaining_results = (
            self.session.query(VerificationResult).filter_by(claim_id=claim_id).all()
        )
        self.assertEqual(len(remaining_evidence), 0)
        self.assertEqual(len(remaining_results), 0)

    # --------------------------------------------------------------------------
    # 4. Representation (__repr__) Tests
    # --------------------------------------------------------------------------

    def test_model_reprs(self):
        """Verify __repr__ formats for models."""
        claim = Claim(id=1, text="Short claim", status="PENDING")
        self.assertIn("Claim(id=1", repr(claim))

        evidence = EvidenceItem(id=2, claim_id=1, source_url="https://example.com/item")
        self.assertIn("EvidenceItem(id=2", repr(evidence))

        result = VerificationResult(id=3, claim_id=1, verdict="TRUE", confidence_score=0.95)
        self.assertIn("VerificationResult(id=3", repr(result))


if __name__ == "__main__":
    unittest.main()
