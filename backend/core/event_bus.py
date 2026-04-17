from collections import defaultdict
from utils.logging import get_logger

log = get_logger("core.event_bus")


class EventBus:
    def __init__(self):
        self._subscribers: dict = defaultdict(list)

    def subscribe(self, event: str, handler):
        self._subscribers[event].append(handler)
        log.info(f"Subscriber registrado: event={event}")

    async def publish(self, event: str, data: dict):
        handlers = self._subscribers.get(event, [])
        for handler in handlers:
            await handler(data)


event_bus = EventBus()
