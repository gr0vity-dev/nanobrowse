import asyncio
from deps.rpc_client import nanorpc


class NetworkParams:
    # Initialize available_supply as a class variable
    available_supply: int = 133246401824662258600496820004700378675


class NetworkParamManager:
    _update_lock = asyncio.Lock()  # Lock to manage concurrent updates

    def __init__(self):
        # Now params is not an instance of NetworkParams, but directly accesses the class variable
        self.params = NetworkParams

    def get_params(self) -> NetworkParams:
        return self.params

    async def run(self):
        # Ensure that only one coroutine can update the value at a time
        async with self._update_lock:
            if not hasattr(self, "_update_task") or self._update_task.done():
                self._update_task = asyncio.create_task(
                    self.background_set_params())

    async def background_set_params(self):
        await self.set_params()

    async def set_params(self):
        available_supply = await nanorpc.available_supply()
        # Update the class variable directly
        NetworkParams.available_supply = available_supply.get(
            "available", NetworkParams.available_supply)
