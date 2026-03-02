"""Tests for data models."""

from contractguard.models import AnalysisResult, ContractType, Issue, Protection, Severity


def test_issue_creation():
    """Test creating an Issue instance."""
    issue = Issue(
        title="Non-refundable deposit",
        severity=Severity.RED,
        clause="Section 3",
        quote="The security deposit is non-refundable",
        explanation="Most jurisdictions require security deposits to be refundable.",
        suggestion="Negotiate to make the deposit refundable minus legitimate deductions.",
    )
    assert issue.severity == Severity.RED
    assert "non-refundable" in issue.quote.lower()


def test_analysis_result():
    """Test creating a complete AnalysisResult."""
    result = AnalysisResult(
        contract_type=ContractType.LEASE,
        summary="A standard residential lease with some concerning clauses.",
        parties=["Landlord LLC", "John Doe"],
        key_terms=["Duration: 12 months", "Rent: $2,000/month"],
        red_flags=[
            Issue(
                title="Non-refundable deposit",
                severity=Severity.RED,
                clause="Section 3",
                quote="deposit is non-refundable",
                explanation="This is unusual and potentially illegal.",
                suggestion="Remove non-refundable clause.",
            )
        ],
        warnings=[],
        good_clauses=[
            Protection(
                title="30-day notice period",
                clause="Section 1",
                explanation="Standard notice period protects both parties.",
            )
        ],
        missing_protections=["No habitability guarantee"],
        fairness_score=45,
        fairness_grade="C",
    )
    assert result.fairness_score == 45
    assert len(result.red_flags) == 1
    assert result.contract_type == ContractType.LEASE


def test_fairness_score_bounds():
    """Test that fairness score is bounded 0-100."""
    import pytest

    with pytest.raises(Exception):
        AnalysisResult(
            contract_type=ContractType.UNKNOWN,
            summary="test",
            fairness_score=101,
            fairness_grade="A+",
        )
