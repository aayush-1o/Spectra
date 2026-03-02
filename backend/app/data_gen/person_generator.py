"""
Spectra — Person Generator
Produces unsaved Person ORM objects with fully synthetic data.
⚠️ All names, dates, and occupations are computer-generated. No real people.
"""

import random
from datetime import date, timedelta

from faker import Faker

from app.data_gen.constants import OCCUPATIONS
from app.models.person import Person

_faker = Faker()


class PersonGenerator:
    """Generate synthetic Person objects (not yet persisted to DB)."""

    def generate(self, n: int) -> list[Person]:
        """
        Return a list of *n* unsaved Person ORM objects.

        Each person has:
        - fake_name  : Faker full name
        - date_of_birth : random date keeping age between 20 and 70
        - occupation    : random choice from constants.OCCUPATIONS
        - metadata_     : {"_synthetic": True}
        """
        persons: list[Person] = []
        today = date.today()

        for _ in range(n):
            # Age 20–70 → date_of_birth between (today - 70y) and (today - 20y)
            age_days = random.randint(20 * 365, 70 * 365)
            dob = today - timedelta(days=age_days)

            persons.append(
                Person(
                    fake_name=_faker.name(),
                    date_of_birth=dob,
                    occupation=random.choice(OCCUPATIONS),
                    metadata_={"_synthetic": True},
                )
            )

        return persons
