"""
Spectra — Person Generator
Produces unsaved Person ORM objects with fully synthetic data.
⚠️ All names, dates, and occupations are computer-generated. No real people.

Phase 8: Added phone numbers, email, nationality, alias, risk_category,
         group_memberships, fake_id_number fields.
"""

import random
import string
from datetime import date, timedelta

from faker import Faker

from app.data_gen.constants import (
    FAKE_ALIASES,
    NATIONALITIES,
    OCCUPATIONS,
    RISK_CATEGORIES,
    RISK_CATEGORY_WEIGHTS,
    SYNTHETIC_ORGS,
)
from app.models.person import Person

_faker = Faker()


def _fake_id_number() -> str:
    """Generate a synthetic ID in format SYN-XXXXXXXX (8 random digits)."""
    digits = "".join(random.choices(string.digits, k=8))
    return f"SYN-{digits}"


class PersonGenerator:
    """Generate synthetic Person objects (not yet persisted to DB)."""

    def generate(self, n: int) -> list[Person]:
        """
        Return a list of *n* unsaved Person ORM objects.

        Each person has:
        - fake_name          : Faker full name
        - date_of_birth      : random date keeping age between 20 and 70
        - occupation         : random choice from constants.OCCUPATIONS
        - fake_phone_primary : Faker phone number
        - fake_phone_secondary: optional (40% of persons)
        - fake_email         : Faker free email
        - fake_nationality   : random from NATIONALITIES list
        - fake_alias         : optional code name (20% of persons)
        - risk_category      : weighted random: low/medium/high/critical
        - group_memberships  : JSONB list of 0–3 org names
        - fake_id_number     : format "SYN-XXXXXXXX"
        - metadata_          : {"_synthetic": True}
        """
        persons: list[Person] = []
        today = date.today()

        for _ in range(n):
            # Age 20–70 → date_of_birth between (today - 70y) and (today - 20y)
            age_days = random.randint(20 * 365, 70 * 365)
            dob = today - timedelta(days=age_days)

            # Optional secondary phone (40% chance)
            secondary_phone = (
                _faker.phone_number() if random.random() < 0.40 else None
            )

            # Optional alias (20% chance)
            alias = (
                random.choice(FAKE_ALIASES) if random.random() < 0.20 else None
            )

            # Risk category — weighted distribution
            risk_cat = random.choices(RISK_CATEGORIES, weights=RISK_CATEGORY_WEIGHTS, k=1)[0]

            # Group memberships — 0 to 3 orgs
            num_groups = random.randint(0, 3)
            group_memberships = random.sample(SYNTHETIC_ORGS, min(num_groups, len(SYNTHETIC_ORGS)))

            persons.append(
                Person(
                    fake_name=_faker.name(),
                    date_of_birth=dob,
                    occupation=random.choice(OCCUPATIONS),
                    fake_phone_primary=_faker.phone_number(),
                    fake_phone_secondary=secondary_phone,
                    fake_email=_faker.free_email(),
                    fake_nationality=random.choice(NATIONALITIES),
                    fake_alias=alias,
                    risk_category=risk_cat,
                    group_memberships=group_memberships,
                    fake_id_number=_fake_id_number(),
                    # last_seen_* will be filled in after events are generated
                    last_seen_lat=None,
                    last_seen_lon=None,
                    last_seen_at=None,
                    metadata_={"_synthetic": True},
                )
            )

        return persons
