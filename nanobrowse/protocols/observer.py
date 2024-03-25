from typing import Protocol


class ObserverProtocol(Protocol):
    async def update_observer(self, message: str) -> None:
        pass
