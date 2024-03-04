import asyncio


async def execute_and_handle_errors(tasks):
    try:
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        results_dict = dict(zip(tasks.keys(), results))

        # Check each result for errors. Assuming that errors in responses are indicated
        for _, result in results_dict.items():
            if isinstance(result, Exception) or ("error" in result and isinstance(result, dict)):
                error_msg = "An unexpected error occurred. Please try again later."
                if isinstance(result, dict):
                    error_msg = result.get(
                        "msg", result.get("error", error_msg))
                raise ValueError(error_msg)
        return results_dict

    except ValueError as exc:
        raise exc
    except Exception as exc:
        raise ValueError(
            f"An unexpected error occurred: {exc}\nPlease try again later.")
