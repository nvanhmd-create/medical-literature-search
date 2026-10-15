"""
Europe PMC API Client.
Enriches articles with Open Access PDF links, PMCID, and citation metrics.
Uses standard library urllib and JSON parsing.
"""

import json
import logging
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Any
from .models import Article

logger = logging.getLogger(__name__)


class EuropePMCClient:
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __init__(self, email: str = "medsearch@academic.org"):
        self.email = email
        self.user_agent = f"MedicalLiteratureAutoSearch/1.0 ({self.email})"

    def enrich_articles(self, articles: List[Article], batch_size: int = 25) -> List[Article]:
        """
        Enriches a list of articles in batches by querying Europe PMC for PMCIDs,
        Open Access status, citation counts, and PDF download links.
        """
        if not articles:
            return articles

        # Group by chunks of batch_size
        for i in range(0, len(articles), batch_size):
            chunk = articles[i:i + batch_size]
            pmid_map = {a.pmid: a for a in chunk if a.pmid}
            if not pmid_map:
                continue

            # Query format: (ext_id:12345 OR ext_id:67890) AND src:med
            query_parts = [f"ext_id:{pmid}" for pmid in pmid_map.keys()]
            query = f"({' OR '.join(query_parts)}) AND src:med"

            params = {
                "query": query,
                "format": "json",
                "pageSize": str(batch_size),
                "resultType": "core",
            }

            try:
                url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                result_list = data.get("resultList", {}).get("result", [])
                for res in result_list:
                    pmid = res.get("pmid")
                    if pmid and pmid in pmid_map:
                        art = pmid_map[pmid]
                        
                        # Citations
                        art.citation_count = res.get("citedByCount")
                        
                        # PMCID
                        if not art.pmcid and res.get("pmcid"):
                            art.pmcid = res.get("pmcid")
                            
                        # Open access & full text links
                        is_oa = res.get("isOpenAccess") == "Y"
                        if is_oa:
                            art.free_fulltext_url = f"https://europepmc.org/article/MED/{pmid}"
                        
                        # Look for PDF url in fullTextUrlList
                        ft_list = res.get("fullTextUrlList", {}).get("fullTextUrl", [])
                        for ft in ft_list:
                            doc_style = ft.get("documentStyle", "").lower()
                            availability = ft.get("availabilityCode", "").lower()
                            url_val = ft.get("url")
                            if "pdf" in doc_style and url_val:
                                art.pdf_url = url_val
                                break
                            elif availability == "oa" and not art.free_fulltext_url and url_val:
                                art.free_fulltext_url = url_val

            except Exception as e:
                logger.warning(f"Không thể kết nối hoặc phân tích dữ liệu Europe PMC: {e}")
                continue

        return articles
