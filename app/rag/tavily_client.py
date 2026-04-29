from tavily import TavilyClient
from app.core.config import settings

class TavilySearch:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Perform web search using Tavily API.
        Returns list of search results with title, url, content, etc.
        """
        response = self.client.search(query=query, max_results=max_results)
        return response.get("results", [])
