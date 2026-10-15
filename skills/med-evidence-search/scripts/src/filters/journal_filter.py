"""
Journal recognition, ranking, and evidence tier filtering module.
Matches articles against the curated whitelist of top-tier journals (NEJM, Lancet, JAMA, AHA, ASH, etc.).
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from ..core.models import Article


class JournalFilter:
    def __init__(self, journals_config: Optional[Dict[str, Any]] = None):
        self.journals_config = journals_config or {}
        self._compiled_patterns = self._build_matcher()

    def _build_matcher(self) -> List[Tuple[re.Pattern, Dict[str, Any]]]:
        """
        Compiles regex patterns from journal configuration for fast lookup.
        """
        patterns = []
        groups = self.journals_config.get("groups", {})
        for group_id, group_info in groups.items():
            g_name = group_info.get("name", group_id)
            g_tier = group_info.get("tier", 1)
            for j in group_info.get("journals", []):
                title = j.get("title", "")
                short = j.get("short", "")
                iso = j.get("iso_abbr", "")
                weight = j.get("weight", 80)
                
                # Combine search tokens
                tokens = [re.escape(t) for t in [title, short, iso] if t]
                
                # Extra common variations
                if "N Engl J Med" in iso or "NEJM" in short:
                    tokens.extend([r"new\s+england\s+journal\s+of\s+medicine", r"n\s+engl\s+j\s+med"])
                elif "Lancet" in short:
                    tokens.extend([r"the\s+lancet", r"lancet"])
                elif "JAMA" in short:
                    tokens.extend([r"\bjama\b", r"journal\s+of\s+the\s+american\s+medical\s+association"])
                elif "Circulation" in short:
                    tokens.extend([r"\bcirculation\b", r"circ\s+res", r"circ\s+heart\s+fail"])
                elif "Blood" in short:
                    tokens.extend([r"\bblood\b", r"\bblood\s+adv\b"])
                elif "Stroke" in short:
                    tokens.extend([r"\bstroke\b"])
                elif "Nat Med" in iso:
                    tokens.extend([r"nature\s+medicine", r"nat\s+med"])

                regex_str = r"(?:^|\b)(?:" + "|".join(tokens) + r")(?:\b|$)"
                pattern = re.compile(regex_str, re.IGNORECASE)
                patterns.append((pattern, {
                    "title": title,
                    "short": short,
                    "iso_abbr": iso,
                    "group_id": group_id,
                    "group_name": g_name,
                    "tier": g_tier,
                    "weight": weight
                }))
        return patterns

    def enrich_article(self, article: Article) -> Article:
        """
        Detects if article is published in a top-tier journal and enriches its metadata.
        """
        journal_str = f"{article.journal} {article.journal_iso}".strip()
        matched = False

        for pattern, meta in self._compiled_patterns:
            if pattern.search(journal_str):
                article.is_top_tier = True
                article.journal_tier = meta["tier"]
                article.journal_group = meta["group_id"]
                article.journal_weight = meta["weight"]
                matched = True
                break

        if not matched:
            article.is_top_tier = False
            article.journal_tier = 3
            article.journal_group = "other"
            article.journal_weight = 40

        return article

    def enrich_and_rank(self, articles: List[Article], sort_by: str = "tier") -> List[Article]:
        """
        Enriches all articles and ranks them according to sorting strategy.
        """
        for a in articles:
            self.enrich_article(a)

        if sort_by == "tier":
            # Sort primarily by: Top tier first, highest journal weight, then most recent year
            return sorted(
                articles,
                key=lambda a: (
                    1 if a.is_top_tier else 0,
                    a.journal_weight,
                    a.pub_year or 0
                ),
                reverse=True
            )
        elif sort_by == "pub_date":
            return sorted(articles, key=lambda a: a.pub_year or 0, reverse=True)
        else:
            return articles
