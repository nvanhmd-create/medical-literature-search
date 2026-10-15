"""
Data models for medical literature search engine.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class JournalMetadata:
    title: str
    short: str
    iso_abbr: str
    group_id: str
    group_name: str
    tier: int = 1
    weight: int = 100


@dataclass
class Article:
    pmid: str
    title: str
    journal: str
    journal_iso: str = ""
    pub_year: Optional[int] = None
    pub_date: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    doi: str = ""
    pmcid: str = ""
    article_types: List[str] = field(default_factory=list)
    mesh_terms: List[str] = field(default_factory=list)
    
    # Enrichment fields
    is_top_tier: bool = False
    journal_tier: int = 3  # 1 = Top (NEJM/Lancet/AHA/ASH), 2 = Major, 3 = Standard indexed
    journal_group: str = "other"
    journal_weight: int = 50
    citation_count: Optional[int] = None
    free_fulltext_url: Optional[str] = None
    pdf_url: Optional[str] = None
    
    # AI Summary & clinical synthesis
    clinical_summary: Optional[str] = None
    key_findings: List[str] = field(default_factory=list)
    
    @property
    def pubmed_url(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"
    
    @property
    def doi_url(self) -> Optional[str]:
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return None

    @property
    def author_display(self) -> str:
        if not self.authors:
            return "Anonymous"
        if len(self.authors) == 1:
            return self.authors[0]
        if len(self.authors) == 2:
            return f"{self.authors[0]} and {self.authors[1]}"
        return f"{self.authors[0]} et al."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pmid": self.pmid,
            "title": self.title,
            "journal": self.journal,
            "journal_iso": self.journal_iso,
            "pub_year": self.pub_year,
            "pub_date": self.pub_date,
            "authors": self.authors,
            "author_display": self.author_display,
            "abstract": self.abstract,
            "doi": self.doi,
            "pmcid": self.pmcid,
            "article_types": self.article_types,
            "mesh_terms": self.mesh_terms,
            "is_top_tier": self.is_top_tier,
            "journal_tier": self.journal_tier,
            "journal_group": self.journal_group,
            "journal_weight": self.journal_weight,
            "citation_count": self.citation_count,
            "free_fulltext_url": self.free_fulltext_url,
            "pdf_url": self.pdf_url,
            "pubmed_url": self.pubmed_url,
            "doi_url": self.doi_url,
            "clinical_summary": self.clinical_summary,
            "key_findings": self.key_findings,
        }


@dataclass
class SearchResult:
    topic: str
    query_executed: str
    total_found_in_pubmed: int
    articles: List[Article] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    stats: Dict[str, Any] = field(default_factory=dict)
    ai_synthesis: Optional[str] = None
