import asyncio
from deps.rpc_client import nanorpc
from utils.logger import logger


class NetworkParams:
    # Initialize available_supply as a class variable
    available_supply: int = 133246401824662258600496820004700378675
    # Add quorum and total weight parameters with default values
    quorum_weight: int = int(available_supply * 0.67)  # Initial quorum weight
    total_weight: int = available_supply  # Initial total weight
    weight_min = 40200000000000000000000000000000000000  # (60m * 0,67)

    @staticmethod
    def get_supply():
        return NetworkParams.available_supply

    @staticmethod
    def get_quorum_weight():
        return NetworkParams.quorum_weight

    @staticmethod
    def get_total_weight():
        return NetworkParams.total_weight

    @staticmethod
    def set_supply(available_supply):
        if available_supply:
            logger.info("Set available_supply : %s", available_supply)
            NetworkParams.available_supply = available_supply

    @staticmethod
    def set_quorum_weight(quorum_weight):
        if quorum_weight:
            logger.info("Set quorum_weight : %s", quorum_weight)
            NetworkParams.quorum_weight = quorum_weight

    @staticmethod
    def set_total_weight(total_weight):
        if total_weight:
            logger.info("Set total_weight : %s", total_weight)
            NetworkParams.total_weight = total_weight


class NetworkParamManager:
    _update_lock = asyncio.Lock()  # Lock to manage concurrent updates
    UPDATE_INTERVAL = 3600  # 1 hour in seconds

    def __init__(self):
        self.params = NetworkParams
        self._update_task = None
        self._is_running = False

    def get_params(self) -> NetworkParams:
        return self.params

    async def run(self):
        # Ensure that only one coroutine can update the value at a time
        async with self._update_lock:
            if not self._is_running:
                self._is_running = True
                self._update_task = asyncio.create_task(self._periodic_update())

    async def _periodic_update(self):
        while self._is_running:
            try:
                await self.set_params()
                # Add other parameter fetching calls here

                await asyncio.sleep(self.UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Error updating network parameters: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying on error

    async def stop(self):
        self._is_running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

    async def set_params(self):
        try:
            # Fetch available supply
            supply_response = await nanorpc.available_supply()
            available_supply = supply_response.get("available")
            NetworkParams.set_supply(available_supply)

            # Fetch confirmation quorum data
            quorum_response = await nanorpc.confirmation_quorum()

            # Get total weight as max of trended, online and minimum
            online_weight = int(quorum_response.get("online_stake_total"))
            trended_weight = int(quorum_response.get("trended_stake_total"))
            total_weight = max(online_weight, trended_weight, NetworkParams.weight_min)
            NetworkParams.set_total_weight(total_weight)

            # Get quorum weight directly from response
            quorum_weight = int(quorum_response.get("quorum_delta"))
            NetworkParams.set_quorum_weight(quorum_weight)

            logger.info("Network parameters updated successfully")
        except Exception as e:
            logger.error(f"Error updating network parameters: {e}")
            raise
