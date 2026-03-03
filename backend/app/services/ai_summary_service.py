"""
Spectra — AI Summary Service
Generates intelligence analyst reports for synthetic persons using Claude.

⚠️ All data is 100% synthetic. Reports describe patterns in generated data only.
"""

import logging

import anthropic

from app.config import get_settings
from app.models.anomaly import AnomalyRecord
from app.models.event import Event
from app.models.person import Person

logger = logging.getLogger(__name__)
settings = get_settings()

_ANALYST_SYSTEM_PROMPT = """You are an intelligence analyst summarizing synthetic activity patterns.
This is 100% synthetic data — no real people are involved.
Write as if you are an analyst summarizing activity patterns for a classified intelligence brief.
Write 2-3 paragraphs in formal, analytical prose. Be specific about the patterns you observe.
Focus on: communication patterns, financial activity, group affiliations, risk indicators, and behavioral anomalies.
Do not use bullet points. Do not add headers. Just write the paragraphs directly.
Always begin with "SUBJECT PROFILE SUMMARY — SYNTHETIC ENTITY [ID]:" followed by the content."""


async def generate_person_summary(
    person: Person,
    events: list[Event],
    anomalies: list[AnomalyRecord],
) -> str:
    """
    Generate a 2–3 paragraph analyst report for a synthetic person.

    Args:
        person:    The Person ORM object.
        events:    List of recent events (last 20 used).
        anomalies: List of anomaly records related to this person.

    Returns:
        A string containing the Claude-generated analyst report.
    """
    if not settings.ANTHROPIC_API_KEY:
        return (
            "AI summary unavailable — ANTHROPIC_API_KEY not configured. "
            "Set this environment variable to enable Claude-powered reports."
        )

    # Build context for Claude
    recent_events = events[:20]

    event_lines = []
    for e in recent_events:
        meta = e.metadata_ or {}
        line = f"- [{e.event_type.upper()}] at {e.occurred_at.strftime('%Y-%m-%d %H:%M')} UTC"
        if e.event_type.value == "transfer":
            line += f" · ${meta.get('amount_usd', 0):,.0f} {meta.get('currency', 'USD')}"
        elif e.event_type.value == "call":
            line += f" · {meta.get('duration_seconds', 0)}s · channel: {meta.get('channel', 'voice')}"
        elif e.event_type.value == "message":
            line += f" · platform: {meta.get('platform', 'unknown')}"
        elif e.event_type.value == "meeting":
            line += f" · {meta.get('attendee_count', 2)} attendees"
            if meta.get("is_covert"):
                line += " · COVERT"
        event_lines.append(line)

    anomaly_summary = (
        f"{len(anomalies)} anomaly records detected" if anomalies
        else "No anomalies detected"
    )

    dob = str(person.date_of_birth) if person.date_of_birth else "unknown"
    alias_str = f'known alias "{person.fake_alias}"' if person.fake_alias else "no known alias"
    groups_str = ", ".join(person.group_memberships or []) or "no known affiliations"

    user_content = f"""Synthetic Person Profile:
- ID: {person.id[:8]}…
- Name: {person.fake_name}
- DOB: {dob}
- Occupation: {person.occupation or 'Unknown'}
- Nationality: {person.fake_nationality or 'Unknown'}
- Alias: {alias_str}
- Risk Score: {f'{person.risk_score:.1f}/100' if person.risk_score is not None else 'N/A'}
- Risk Category: {person.risk_category or 'unknown'}
- Group Affiliations: {groups_str}
- Anomaly Status: {anomaly_summary}

Recent Activity ({len(recent_events)} events of {len(events)} total):
{chr(10).join(event_lines) if event_lines else '- No events recorded'}

Please write the intelligence summary."""

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=_ANALYST_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        return message.content[0].text.strip()

    except anthropic.APIError as e:
        logger.error("Anthropic API error generating summary: %s", e)
        return f"Summary generation failed: {type(e).__name__}. Please try again later."
