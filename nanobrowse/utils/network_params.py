import asyncio
from deps.rpc_client import nanorpc
from utils.logger import logger


class NetworkParams:
    # Initialize available_supply as a class variable
    available_supply: int = 133246401824662258600496820004700378675

    @staticmethod
    def get_supply():
        return NetworkParams.available_supply

    @staticmethod
    def set_supply(available_supply):
        if available_supply:
            logger.info("Set available_supply : %s", available_supply)
            NetworkParams.available_supply = available_supply


class NetworkParamManager:
    _update_lock = asyncio.Lock()  # Lock to manage concurrent updates

    def __init__(self):
        # Directly access the NetworkParams class
        self.params = NetworkParams
        self._update_task = None  # Define _update_task here to avoid the pylint warning

    def get_params(self) -> NetworkParams:
        return self.params

    async def run(self):
        # Ensure that only one coroutine can update the value at a time
        async with self._update_lock:
            # Check if _update_task is None or if the task is done
            if self._update_task is None or self._update_task.done():
                self._update_task = asyncio.create_task(
                    self.background_set_params())

    async def background_set_params(self):
        await self.set_params()

    async def set_params(self):
        # Assuming nanorpc.available_supply() is an async call
        response = await nanorpc.available_supply()
        available_supply = response.get("available")
        NetworkParams.set_supply(available_supply)
