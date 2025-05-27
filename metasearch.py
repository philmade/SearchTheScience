from habanero import Crossref
import requests
from typing import List


class Metasearch:
    def __init__(self):
        self.cr = Crossref()

    async def search_by_title(
        self,
        title: str,
        limit: int = 1,
    ) -> List[dict]:
        """Search for research papers by title on Crossref. Returns a list of matching papers with their metadata."""
        results = self.cr.works(query_title=title, limit=limit)
        return results["message"]["items"]

    def sync_search_by_doi(self, doi: str) -> dict:
        if doi is None:
            return
        try:
            results = self.cr.works(ids=doi)
            return results["message"]
        except requests.exceptions.HTTPError as err:
            return {"error": str(err)}

    async def search_by_doi(
        self,
        doi: str,
    ) -> dict:
        """Search for a research paper by its DOI on Crossref. Returns the metadata of the paper."""
        try:
            results = self.cr.works(ids=doi)
            return results["message"]
        except requests.exceptions.HTTPError as err:
            return {"error": str(err)}

    async def search_science_by_abstract(
        self,
        abstract: str,
        limit: int = 1,
    ) -> List[dict]:
        """Search for research papers by abstract on Crossref. Returns a list of matching papers with their metadata."""
        results = self.cr.works(query_container_title=abstract, limit=limit)
        return results["message"]["items"]

    async def search_by_author(
        self,
        author: str,
        limit: int = 1,
    ) -> List[dict]:
        """Search for research papers by author on Crossref. Returns a list of matching papers with their metadata."""
        results = self.cr.works(query_author=author, limit=limit)
        return results["message"]["items"]

    async def search_science_by_keyword(
        self,
        keyword: str,
        limit: int = 1,
    ) -> List[dict]:
        """Search for research papers by keyword on Crossref. Returns a list of matching papers with their metadata."""
        results = self.cr.works(query=keyword, limit=limit)
        return results["message"]["items"]
