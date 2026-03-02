"""
Spectra — Unit Tests: EventGenerator
"""

import pytest

from app.data_gen.event_generator import EventGenerator
from app.data_gen.location_generator import LocationGenerator
from app.data_gen.person_generator import PersonGenerator
from app.models.event import EventType


@pytest.fixture
def sample_persons():
    gen = PersonGenerator()
    return gen.generate(10)


@pytest.fixture
def sample_locations():
    gen = LocationGenerator()
    return gen.generate(5)


@pytest.fixture
def generator():
    return EventGenerator()


def test_generator_returns_correct_count(generator, sample_persons, sample_locations):
    """generate(n) must return exactly n Event objects."""
    events = generator.generate(sample_persons, sample_locations, 30)
    assert len(events) == 30


def test_no_self_events(generator, sample_persons, sample_locations):
    """actor_id must never equal target_id."""
    events = generator.generate(sample_persons, sample_locations, 50)
    for e in events:
        assert e.actor_id != e.target_id, (
            f"Self-event detected: actor_id={e.actor_id!r} == target_id={e.target_id!r}"
        )


def test_all_events_have_synthetic_flag(generator, sample_persons, sample_locations):
    """metadata_ must always contain _synthetic: True."""
    events = generator.generate(sample_persons, sample_locations, 30)
    for e in events:
        assert isinstance(e.metadata_, dict)
        assert e.metadata_.get("_synthetic") is True


def test_event_type_is_valid(generator, sample_persons, sample_locations):
    """event_type must be one of the valid EventType enum values."""
    valid_types = set(EventType)
    events = generator.generate(sample_persons, sample_locations, 50)
    for e in events:
        assert e.event_type in valid_types, f"Invalid event_type: {e.event_type!r}"
