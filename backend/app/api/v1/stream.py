"""
Spectra — Asset Stream API  (Phase 9)
WebSocket endpoint that pushes synthetic asset telemetry at 1-second intervals.

Routes:
  GET  /stream/assets/snapshot  — REST: current positions of all assets
  WS   /stream/assets           — WebSocket: live 1 Hz position stream

⚠️ ALL DATA IS SYNTHETIC. No real ADS-B / GPS data ingested.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.data_gen.synthetic_telemetry import (
    AssetPosition,
    AssetType,
    get_fleet,
    get_generator,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Fleet size (configurable via module constant) ──────────────────────────────
FLEET_SIZE = 60

# ── Connection manager ─────────────────────────────────────────────────────────

class ConnectionManager:
    """Track all active WebSocket subscribers."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        logger.info("Asset stream: client connected. Total=%d", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.remove(ws)
        logger.info("Asset stream: client disconnected. Total=%d", len(self._connections))

    async def send_json(self, ws: WebSocket, payload: dict[str, Any]) -> None:
        """Send a JSON payload to one client; silently handle send errors."""
        try:
            await ws.send_text(json.dumps(payload, default=str))
        except Exception:
            pass  # client already gone; disconnect handled below

    @property
    def connected_count(self) -> int:
        return len(self._connections)


_manager = ConnectionManager()


# ── Serialisation helper ───────────────────────────────────────────────────────

def _position_to_dict(pos: AssetPosition) -> dict[str, Any]:
    """Convert an AssetPosition dataclass to a JSON-serialisable dict."""
    return dataclasses.asdict(pos)


# ── REST snapshot endpoint ─────────────────────────────────────────────────────

@router.get(
    "/assets/snapshot",
    summary="Current synthetic asset positions (REST)",
    tags=["stream"],
)
async def get_asset_snapshot() -> dict[str, Any]:
    """
    Return the current position of every synthetic asset as a one-shot JSON
    response. Useful for the initial frontend render before the WebSocket handshake.

    ⚠️ 100% synthetic coordinates — no real ADS-B or GPS data.
    """
    fleet = get_fleet(FLEET_SIZE)
    gen   = get_generator()
    positions = gen.snapshot(fleet)
    return {
        "synthetic": True,
        "ethics":    "100% synthetic data — no real aircraft or vehicles tracked.",
        "count":     len(positions),
        "assets":    [_position_to_dict(p) for p in positions],
        "types":     {t.value: sum(1 for p in positions if p.asset_type == t.value)
                      for t in AssetType},
    }


# ── WebSocket stream endpoint ──────────────────────────────────────────────────

@router.websocket("/assets")
async def asset_stream(websocket: WebSocket) -> None:
    """
    WebSocket endpoint that pushes synthetic asset telemetry at 1-second intervals.

    Protocol:
      1. On connect → sends {"type": "manifest", "assets": [...]} listing all assets
         with id, label, asset_type.
      2. Every second → sends {"type": "positions", "data": [...AssetPosition...]}
      3. On client disconnect → loop exits cleanly.

    ⚠️ ALL DATA IS SYNTHETIC. No real tracking data is involved.
    """
    await _manager.connect(websocket)

    fleet = get_fleet(FLEET_SIZE)
    gen   = get_generator()

    # ── 1. Send manifest so the client knows all asset IDs/labels upfront ──────
    manifest = {
        "type":      "manifest",
        "synthetic": True,
        "ethics":    "100% synthetic — no real entities tracked.",
        "assets": [
            {"id": a.id, "label": a.label, "asset_type": a.asset_type.value}
            for a in fleet
        ],
    }
    await _manager.send_json(websocket, manifest)

    # ── 2. Stream position updates at 1 Hz ────────────────────────────────────
    try:
        while True:
            await asyncio.sleep(1.0)
            positions = gen.tick_all(fleet, delta_seconds=1.0)
            payload = {
                "type": "positions",
                "data": [_position_to_dict(p) for p in positions],
            }
            await _manager.send_json(websocket, payload)

    except WebSocketDisconnect:
        _manager.disconnect(websocket)
    except asyncio.CancelledError:
        _manager.disconnect(websocket)
        raise
    except Exception as exc:
        logger.error("Asset stream error: %s", exc)
        _manager.disconnect(websocket)
