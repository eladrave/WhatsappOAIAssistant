import httpx
from .Tool import Tool


class WebSearch(Tool):
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def execute(self, query: str) -> str:
        url = f"https://eladsearngx-w4o7wofqcq-nn.a.run.app/search?format=json&q={query}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()  # Raise an error for bad responses
                search_results = response.json()
                return str(search_results)
            except httpx.ReadTimeout:
                return "Request timed out. Please try again."
            except httpx.HTTPStatusError as e:
                return f"HTTP error occurred: {e.response.status_code}"
            except Exception as e:
                return f"An error occurred: {str(e)}"

    def __str__(self) -> str:
        return "web_search"

__all__ = ['WebSearch']
