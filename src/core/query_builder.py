"""
Query builder for medical literature databases (PubMed and Europe PMC).
Constructs optimized Boolean and MeSH search queries with support for
high-impact journal filtering and evidence-based study types.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


ARTICLE_TYPE_FILTERS = {
    "guidelines": '("Practice Guideline"[pt] OR "Guideline"[pt] OR "Consensus Development Conference"[pt])',
    "systematic_reviews": '("systematic review"[tiab] OR "Systematic Review"[pt])',
    "meta_analyses": '("Meta-Analysis"[pt] OR "meta-analysis"[tiab])',
    "rct": '("Randomized Controlled Trial"[pt] OR "randomized controlled trial"[tiab])',
    "clinical_trials": '("Clinical Trial"[pt] OR "Clinical Trial, Phase III"[pt] OR "Clinical Trial, Phase IV"[pt])',
    "reviews": '("Review"[pt])',
}


class QueryBuilder:
    def __init__(self, journals_config: Optional[Dict[str, Any]] = None):
        self.journals_config = journals_config or {}

    def get_journal_query_clause(self, selected_groups: Optional[List[str]] = None) -> str:
        """
        Builds the OR-connected PubMed query for top-tier journals
        (NEJM, Lancet, JAMA, BMJ, AHA, ASH, etc.).
        """
        groups = self.journals_config.get("groups", {})
        if not groups:
            return ""

        queries = []
        for group_id, group_info in groups.items():
            if selected_groups and group_id not in selected_groups:
                continue
            for j in group_info.get("journals", []):
                q = j.get("pubmed_query")
                if q:
                    queries.append(q)

        if not queries:
            return ""
        return " OR ".join(queries)

    def get_article_type_clause(self, article_types: Optional[List[str]] = None) -> str:
        """
        Builds the OR-clause for evidence-based study types.
        """
        if not article_types or "all" in article_types:
            return ""

        clauses = []
        for t in article_types:
            t_clean = t.lower().strip()
            if t_clean in ARTICLE_TYPE_FILTERS:
                clauses.append(ARTICLE_TYPE_FILTERS[t_clean])

        if not clauses:
            return ""
        return " OR ".join(clauses)

    def get_date_clause(self, years_back: int) -> str:
        """
        Builds the publication date filter clause.
        """
        if not years_back or years_back <= 0:
            return ""
        current_year = datetime.now().year
        start_year = current_year - years_back
        return f'("{start_year}/01/01"[Date - Publication] : "3000"[Date - Publication])'

    def build_pubmed_query(
        self,
        topic: str,
        years_back: int = 5,
        top_tier_only: bool = False,
        journal_groups: Optional[List[str]] = None,
        article_types: Optional[List[str]] = None,
    ) -> str:
        """
        Assembles the complete search query for PubMed.
        """
        topic_clean = topic.strip()
        if not topic_clean:
            raise ValueError("Chủ đề tìm kiếm không được để trống!")

        # Wrap topic in parentheses if multi-word without quotes
        base_topic = f"({topic_clean})" if not topic_clean.startswith("(") else topic_clean
        parts = [base_topic]

        # Journal filter if requested
        if top_tier_only or journal_groups:
            j_clause = self.get_journal_query_clause(journal_groups)
            if j_clause:
                parts.append(f"({j_clause})")

        # Study type filter
        type_clause = self.get_article_type_clause(article_types)
        if type_clause:
            parts.append(f"({type_clause})")

        # Date filter
        date_clause = self.get_date_clause(years_back)
        if date_clause:
            parts.append(date_clause)

        return " AND ".join(parts)
