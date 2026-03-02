"""
Spectra — Unit Tests: PersonGenerator
"""

from datetime import date

import pytest

from app.data_gen.person_generator import PersonGenerator


@pytest.fixture
def generator() -> PersonGenerator:
    return PersonGenerator()


def test_generator_returns_correct_count(generator: PersonGenerator) -> None:
    """generate(n) must return exactly n Person objects."""
    persons = generator.generate(15)
    assert len(persons) == 15


def test_all_persons_have_nonempty_fake_name(generator: PersonGenerator) -> None:
    """Every person must have a non-empty string fake_name."""
    persons = generator.generate(20)
    for p in persons:
        assert isinstance(p.fake_name, str)
        assert len(p.fake_name.strip()) > 0


def test_all_persons_have_synthetic_flag(generator: PersonGenerator) -> None:
    """Every person must have _synthetic: True in metadata_."""
    persons = generator.generate(20)
    for p in persons:
        assert isinstance(p.metadata_, dict)
        assert p.metadata_.get("_synthetic") is True


def test_date_of_birth_within_age_range(generator: PersonGenerator) -> None:
    """date_of_birth must correspond to an age between 20 and 70."""
    persons = generator.generate(50)
    today = date.today()
    for p in persons:
        assert p.date_of_birth is not None
        age_years = (today - p.date_of_birth).days / 365
        assert 20 <= age_years <= 71, f"Age out of range: {age_years:.1f} for dob {p.date_of_birth}"
