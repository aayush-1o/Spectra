# ETHICS.md — SimSight Data Ethics Statement

> This document is part of the SimSight project.
> It explains what the project does, what it deliberately does NOT do,
> and why those choices matter.

---

## What SimSight Is

SimSight is a **portfolio and learning project** that simulates the appearance of a data-analytics platform using entirely computer-generated, synthetic (fake) data. It was built to demonstrate technical skills in backend development, graph databases, anomaly detection, and frontend dashboards.

**Every single piece of data inside SimSight was invented by a computer.**

- The "people" do not exist.
- The "phone calls" never happened.
- The "locations" are fictional coordinates.
- The "money transfers" are random numbers.

Nothing in this system was sourced from any real human being, any public dataset, any social media platform, any government database, or any other external source.

---

## What SimSight Is NOT

SimSight is **not** a surveillance tool.
SimSight **cannot** track real people.
SimSight **does not** collect, store, or process any real personal information.
SimSight **was not** designed to be used on real data. It actively rejects it.

This project intentionally avoids every capability that would make it dangerous:
- No web scrapers
- No API integrations with real data sources
- No file upload endpoint
- No real-time data feeds
- No ability to deanonymise or correlate real persons

---

## Why This Matters: The Real Risks of Surveillance Technology

Tools like the ones SimSight simulates — relationship graph analysers, location trackers, communication pattern detectors — are genuinely powerful and genuinely dangerous when used on real data without oversight.

**Known harms from real surveillance tools include:**

1. **Chilling effects on free speech and association.** When people know they may be watched, they self-censor. They avoid political groups, religious institutions, or advocacy organisations. This is documented in democracies, not just authoritarian states.

2. **Discriminatory targeting.** Algorithmic pattern detection has repeatedly been shown to amplify existing racial, ethnic, and socioeconomic biases. "Anomaly detection" on real populations will disproportionately flag already-marginalised communities.

3. **Mission creep.** Tools built for one stated purpose (e.g., financial fraud detection) routinely expand into broader surveillance roles once the infrastructure exists. Once built, these systems are hard to limit.

4. **Data breaches.** Any system that aggregates detailed profiles of real individuals becomes a high-value target. Breaches expose real people to identity theft, harassment, and targeted violence.

5. **Abuse by bad actors.** Surveillance infrastructure built by well-intentioned governments or companies can be inherited by future administrations or buyers with different values.

---

## The Responsible Engineering Choice Made Here

This project was **deliberately built with synthetic data** as a first-class constraint, not as a shortcut. That choice reflects the following engineering ethic:

> **"You can demonstrate a capability without building a weapon."**

Demonstrating that you can build a relationship graph viewer or an anomaly detector does not require actually surveilling human beings. Building it on fake data is safer, and communicating that choice clearly is an act of professional responsibility.

---

## Technical Safeguards Implemented

| Safeguard | How It Works |
|-----------|-------------|
| Ethics banner | Every page of the web app shows a persistent warning that all data is synthetic |
| PII rejection middleware | The FastAPI backend rejects any POST body matching real PII patterns (SSN format, E.164 phone numbers, real email addresses) with a `400 ETHICS_VIOLATION` error |
| Synthetic watermark | Every generated record contains `"_synthetic": true` in its metadata |
| No external data sources | Zero API integrations with real-world data providers |
| No file upload | No endpoint accepts user-uploaded data files |
| About page | The frontend has a dedicated page explaining this ethics statement to any visitor |

---

## A Note to Future Engineers

If you adapt this project, fork it, or build something inspired by it, please:

1. **Do not remove the ethics layer.** The PII guard middleware exists for a reason.
2. **Do not connect it to real data sources** without fundamentally rethinking the system's safety architecture.
3. **Communicate your purpose clearly.** If you build anything that *could* be misused, say so prominently.
4. **Read about the harms before you build.** Start with the [EFF Surveillance Self-Defense guide](https://ssd.eff.org) and the [AI Now Institute's reports](https://ainowinstitute.org/reports.html).

---

*SimSight is a demo. Use knowledge responsibly.*
