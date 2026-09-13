"""
NETRYX EVIDENCE — Event Bus
Redis Streams-based event bus for event-driven architecture (CQRS).
Enables the evidence processing cascade: upload → hash → store → analyze → correlate → score.
"""

import json
import asyncio
from datetime import datetime, timezone
from typing import Callable, Optional
from uuid import uuid4

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()


class EventBus:
    """
    Event bus using Redis Streams for reliable, ordered event delivery.

    Events flow:
        evidence.uploaded → evidence.hashed → evidence.stored →
        analysis.started → analysis.completed → ioc.extracted →
        ioc.enriched → correlation.found → graph.updated →
        timeline.updated → risk.scored → notification.sent
    """

    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._handlers: dict[str, list[Callable]] = {}
        self._consumer_group = "netryx-workers"
        self._consumer_name = f"worker-{uuid4().hex[:8]}"

    async def connect(self):
        """Initialize Redis connection."""
        self._redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()

    async def emit(self, event_type: str, payload: dict) -> str:
        """
        Emit an event to the event bus.

        Args:
            event_type: Dot-separated event name (e.g., 'evidence.uploaded')
            payload: Event data dictionary

        Returns:
            Stream message ID
        """
        if not self._redis:
            await self.connect()

        message = {
            "event_id": uuid4().hex,
            "event_type": event_type,
            "payload": json.dumps(payload, default=str),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add to Redis Stream (creates stream if not exists)
        stream_name = f"netryx:events:{event_type.split('.')[0]}"
        message_id = await self._redis.xadd(stream_name, message, maxlen=10000)

        # Also publish to pub/sub for real-time WebSocket notifications
        await self._redis.publish(
            "netryx:realtime",
            json.dumps({"type": event_type, "data": payload}, default=str),
        )

        return message_id

    def on(self, event_type: str, handler: Callable):
        """Register a handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def listen(self, streams: list[str], batch_size: int = 10):
        """
        Listen for events on specified streams (consumer group pattern).
        This runs in Celery workers.
        """
        if not self._redis:
            await self.connect()

        # Create consumer groups if they don't exist
        for stream in streams:
            try:
                await self._redis.xgroup_create(
                    stream, self._consumer_group, id="0", mkstream=True
                )
            except aioredis.ResponseError:
                pass  # Group already exists

        while True:
            try:
                # Read new messages from streams
                results = await self._redis.xreadgroup(
                    groupname=self._consumer_group,
                    consumername=self._consumer_name,
                    streams={s: ">" for s in streams},
                    count=batch_size,
                    block=5000,  # Block for 5s max
                )

                for stream_name, messages in results:
                    for msg_id, data in messages:
                        event_type = data.get("event_type", "")
                        payload = json.loads(data.get("payload", "{}"))

                        # Dispatch to registered handlers
                        handlers = self._handlers.get(event_type, [])
                        for handler in handlers:
                            try:
                                await handler(payload)
                            except Exception as e:
                                print(f"Handler error for {event_type}: {e}")

                        # Acknowledge message
                        await self._redis.xack(
                            stream_name, self._consumer_group, msg_id
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Event bus listener error: {e}")
                await asyncio.sleep(1)


# ── Singleton ────────────────────────────────────────────────
event_bus = EventBus()
