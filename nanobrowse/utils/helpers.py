async def toggle_every_n(n):
    """Utility async generator to toggle True every N iterations, otherwise False."""
    count = 0
    while True:
        yield count % n == 0
        count += 1
