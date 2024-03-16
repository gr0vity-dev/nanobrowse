import asyncio


async def execute_and_handle_errors(tasks, droppable_errors=None):
    if droppable_errors is None:
        droppable_errors = []

    try:
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        results_dict = dict(zip(tasks.keys(), results))

        # Check each result for errors. Assuming that errors in responses are indicated
        for _, result in results_dict.items():
            error_msg = "An unexpected error occurred. Please try again later."
            if isinstance(result, dict) and result.get("error") in droppable_errors:
                # Move the error to ignored_error if in the list of droppable errors.
                # Avoids raising a ValueError
                result["ignored_error"] = result.pop("error")

            if isinstance(result, dict) and "error" in result or isinstance(result, Exception):
                # Adjust to handle both dict and Exception cases
                error_msg = result.get("msg", result.get("error", error_msg)) if isinstance(
                    result, dict) else str(result)
                raise ValueError(error_msg)
        return results_dict
    except ValueError as exc:
        raise exc
    except Exception as exc:
        raise ValueError(
            f"An unexpected error occurred: {exc}\nPlease try again later.")
