"""
Spectra — Natural Language Search Service
Parses user queries with Claude and converts them to Pydantic filter objects.

⚠️ All data is synthetic. Claude is used only to parse intent — no real persons.
"""

import json
import logging
import re

import anthropic

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_NL_SYSTEM_PROMPT = """You are a JSON extraction assistant for a synthetic intelligence platform.
The user will ask a question about synthetic persons and events.
Extract filter parameters from their query and return ONLY a JSON object.

Available filter fields (all optional):
- min_transfer_usd: number (minimum USD transfer amount)
- max_transfer_usd: number (maximum USD transfer amount)
- after_hour: integer 0-23 (events after this hour of day)
- before_hour: integer 0-23 (events before this hour of day)
- event_type: string, one of: "call", "message", "transfer", "meeting"
- occupation: string (job title filter, partial match)
- min_risk_score: number 0-100 (minimum risk score)
- nationality: string (nationality filter)
- has_alias: boolean (true if person must have an alias)

Return ONLY valid JSON. Example:
{"min_transfer_usd": 10000, "after_hour": 22}

If no filters can be extracted, return: {}
Do not include explanations or markdown. Return only the JSON object."""


async def parse_nl_query(user_query: str) -> dict:
    """
    Call Claude API to parse a natural language query into filter parameters.

    Args:
        user_query: Natural language query from the user.

    Returns:
        dict with optional filter keys.
    """
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — returning empty filters")
        return {}

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=256,
            system=_NL_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_query}],
        )
        raw = message.content[0].text.strip()

        # Strip any accidental markdown code fences
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        filters = json.loads(raw)
        logger.info("NL query parsed: %r → %s", user_query, filters)
        return filters

    except (json.JSONDecodeError, IndexError, KeyError) as e:
        logger.warning("Claude returned non-JSON for query %r: %s", user_query, e)
        return {}
    except anthropic.APIError as e:
        logger.error("Anthropic API error: %s", e)
        return {}
