"""
NCBI PubMed E-Utilities Client.
Handles query execution, PMID retrieval, XML parsing of full metadata,
abstracts, MeSH terms, and article identifiers.
Works with zero external dependencies (pure standard library urllib + ElementTree).
"""

import json
import logging
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
from .models import Article

logger = logging.getLogger(__name__)


class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(self, api_key: Optional[str] = None, email: str = "medsearch@academic.org"):
        self.api_key = api_key
        self.email = email
        self.tool_name = "MedicalLiteratureAutoSearch"
        # NCBI rate limits: 3 req/sec without key, 10 req/sec with key
        self.min_interval = 0.15 if api_key else 0.35
        self.last_req_time = 0.0

    def _rate_limit(self):
        elapsed = time.time() - self.last_req_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_req_time = time.time()

    def _http_get(self, endpoint: str, params: Dict[str, Any]) -> str:
        self._rate_limit()
        if self.api_key:
            params["api_key"] = self.api_key
        params["email"] = self.email
        params["tool"] = self.tool_name

        query_string = urllib.parse.urlencode(params)
        full_url = f"{self.BASE_URL}{endpoint}?{query_string}"

        req = urllib.request.Request(
            full_url,
            headers={
                "User-Agent": f"{self.tool_name}/1.0 ({self.email})"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")

    def search_pmids(
        self,
        query: str,
        retmax: int = 20,
        sort: str = "pub_date"
    ) -> Tuple[List[str], int]:
        """
        Executes an esearch query and returns (pmids_list, total_count).
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": retmax,
            "retmode": "json",
            "sort": sort,
        }

        raw_json = self._http_get("esearch.fcgi", params)
        data = json.loads(raw_json)
        result = data.get("esearchresult", {})
        id_list = result.get("idlist", [])
        count = int(result.get("count", 0))
        return id_list, count

    def fetch_articles_by_pmids(self, pmids: List[str]) -> List[Article]:
        """
        Fetches detailed article metadata via efetch.fcgi (XML) for a list of PMIDs.
        """
        if not pmids:
            return []

        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }

        xml_data = self._http_get("efetch.fcgi", params)
        return self._parse_pubmed_xml(xml_data)

    def _parse_pubmed_xml(self, xml_text: str) -> List[Article]:
        articles = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error(f"Lỗi phân tích XML từ PubMed: {e}")
            return []

        for article_elem in root.findall(".//PubmedArticle"):
            try:
                # 1. PMID
                pmid_elem = article_elem.find(".//MedlineCitation/PMID")
                pmid = pmid_elem.text.strip() if pmid_elem is not None and pmid_elem.text else ""
                if not pmid:
                    continue

                medline = article_elem.find(".//MedlineCitation")
                art = medline.find("Article") if medline is not None else None
                if art is None:
                    continue

                # 2. Title
                title_elem = art.find("ArticleTitle")
                title = "".join(title_elem.itertext()).strip() if title_elem is not None else "No Title"

                # 3. Journal info
                journal_elem = art.find("Journal")
                journal_title = ""
                journal_iso = ""
                pub_year = None
                pub_date_str = ""

                if journal_elem is not None:
                    jt = journal_elem.find("Title")
                    if jt is not None and jt.text:
                        journal_title = jt.text.strip()
                    
                    j_iso = journal_elem.find("ISOAbbreviation")
                    if j_iso is not None and j_iso.text:
                        journal_iso = j_iso.text.strip()

                    # Date parsing
                    pub_date = journal_elem.find(".//JournalIssue/PubDate")
                    if pub_date is not None:
                        year_el = pub_date.find("Year")
                        if year_el is not None and year_el.text:
                            try:
                                pub_year = int(year_el.text.strip())
                                pub_date_str = year_el.text.strip()
                            except ValueError:
                                pass
                        
                        medline_date = pub_date.find("MedlineDate")
                        if medline_date is not None and medline_date.text:
                            pub_date_str = medline_date.text.strip()
                            # Extract 4-digit year from string like '2023 Jul-Aug'
                            import re
                            match = re.search(r"\b(19\d\d|20\d\d)\b", pub_date_str)
                            if match and not pub_year:
                                pub_year = int(match.group(1))

                # 4. Authors
                authors = []
                author_list = art.find("AuthorList")
                if author_list is not None:
                    for a in author_list.findall("Author"):
                        last_name = a.find("LastName")
                        fore_name = a.find("ForeName")
                        collective = a.find("CollectiveName")
                        if last_name is not None and last_name.text:
                            fn = fore_name.text if fore_name is not None and fore_name.text else ""
                            authors.append(f"{last_name.text} {fn}".strip())
                        elif collective is not None and collective.text:
                            authors.append(collective.text.strip())

                # 5. Abstract (combining structured sections)
                abstract_parts = []
                abstract_elem = art.find("Abstract")
                if abstract_elem is not None:
                    for text_elem in abstract_elem.findall("AbstractText"):
                        label = text_elem.get("Label")
                        content = "".join(text_elem.itertext()).strip()
                        if label and content:
                            abstract_parts.append(f"**{label.upper()}**: {content}")
                        elif content:
                            abstract_parts.append(content)
                abstract = "\n\n".join(abstract_parts) if abstract_parts else ""

                # 6. DOI & PMCID
                doi = ""
                pmcid = ""
                article_ids = article_elem.find(".//PubmedData/ArticleIdList")
                if article_ids is not None:
                    for aid in article_ids.findall("ArticleId"):
                        id_type = aid.get("IdType")
                        if id_type == "doi" and aid.text:
                            doi = aid.text.strip()
                        elif id_type == "pmc" and aid.text:
                            pmcid = aid.text.strip()

                # 7. Publication Types
                pub_types = []
                pt_list = art.find("PublicationTypeList")
                if pt_list is not None:
                    for pt in pt_list.findall("PublicationType"):
                        if pt.text:
                            pub_types.append(pt.text.strip())

                # 8. MeSH Terms
                mesh_terms = []
                mesh_list = medline.find("MeshHeadingList") if medline is not None else None
                if mesh_list is not None:
                    for mh in mesh_list.findall("MeshHeading"):
                        desc = mh.find("DescriptorName")
                        if desc is not None and desc.text:
                            mesh_terms.append(desc.text.strip())

                article_obj = Article(
                    pmid=pmid,
                    title=title,
                    journal=journal_title,
                    journal_iso=journal_iso,
                    pub_year=pub_year,
                    pub_date=pub_date_str,
                    authors=authors,
                    abstract=abstract,
                    doi=doi,
                    pmcid=pmcid,
                    article_types=pub_types,
                    mesh_terms=mesh_terms,
                )
                articles.append(article_obj)
            except Exception as ex:
                logger.warning(f"Bỏ qua 1 bài báo do lỗi phân tích cấu trúc: {ex}")
                continue

        return articles
