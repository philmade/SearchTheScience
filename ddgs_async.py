import asyncio
from typing import Any, Dict, List
from loguru import logger
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
import os


class AsyncDDGS:
    """Async wrapper for DuckDuckGo Search with retries and concurrency control"""

    def __init__(self):
        self.session = None
        self.rate_limit_delay = 1.5
        self.max_retries = 3
        self.backoff_factor = 2
        proxy = os.getenv('PROXY_AUTH')
        self._ddgs = DDGS(
            proxy=f"http://{proxy}@geo.iproyal.com:12321" if proxy else None,
            timeout=20,
        )
        self._semaphore = asyncio.Semaphore(5)  # Limit concurrent requests

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._ddgs, "close"):
            await asyncio.to_thread(self._ddgs.close)

    async def _retry(self, func, *args, **kwargs):
        for attempt in range(self.max_retries + 1):
            try:
                async with self._semaphore:
                    return await asyncio.to_thread(func, *args, **kwargs)
            except RatelimitException as e:
                if attempt == self.max_retries:
                    raise
                await self._handle_rate_limit(attempt)
            except Exception as e:
                logger.error(f"Search failed: {func.__name__} - {str(e)}")
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(self.rate_limit_delay)
        return []

    async def _handle_rate_limit(self, attempt: int):
        delay = self.rate_limit_delay * (self.backoff_factor**attempt)
        logger.warning(f"Rate limited, waiting {delay}s before retry")
        await asyncio.sleep(delay)

    async def news(self, keywords: str, **kwargs) -> List[Dict[str, Any]]:
        return await self._retry(self._ddgs.news, keywords=keywords, **kwargs)

    async def text(self, keywords: str, **kwargs) -> List[Dict[str, Any]]:
        return await self._retry(self._ddgs.text, keywords=keywords, **kwargs)

    async def images(self, keywords: str, **kwargs) -> List[Dict[str, Any]]:
        return await self._retry(self._ddgs.images, keywords=keywords, **kwargs)

    async def videos(self, keywords: str, **kwargs) -> List[Dict[str, Any]]:
        return await self._retry(self._ddgs.videos, keywords=keywords, **kwargs)

    async def answers(self, keywords: str, **kwargs) -> List[Dict[str, Any]]:
        return await self._retry(self._ddgs.answers, keywords=keywords, **kwargs)
