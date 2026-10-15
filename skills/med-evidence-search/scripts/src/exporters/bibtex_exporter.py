"""
BibTeX Exporter.
Exports articles to .bib format for import into EndNote, Zotero, Mendeley, and LaTeX.
"""

import re
from typing import Optional
from ..core.models import SearchResult, Article


class BibTeXExporter:
    @staticmethod
    def _clean_str(text: str) -> str:
        if not text:
            return ""
        # Remove markdown bold/italics
        cleaned = re.sub(r"[*_`]", "", text)
        return cleaned.replace("{", "\\{").replace("}", "\\}")

    @staticmethod
    def article_to_bibtex(article: Article) -> str:
        # Generate cite key: e.g. FirstAuthor2023 or PMID_123456
        first_author = "Author"
        if article.authors:
            parts = article.authors[0].split()
            if parts:
                first_author = re.sub(r"[^a-zA-Z]", "", parts[0])

        year = str(article.pub_year or "no_date")
        cite_key = f"{first_author}_{year}_{article.pmid}"

        authors_str = " and ".join(article.authors) if article.authors else "Unknown"

        entry_lines = [
            f"@article{{{cite_key},",
            f"  title = {{{BibTeXExporter._clean_str(article.title)}}},",
            f"  author = {{{authors_str}}},",
            f"  journal = {{{BibTeXExporter._clean_str(article.journal or article.journal_iso)}}},",
            f"  year = {{{year}}},",
        ]

        if article.doi:
            entry_lines.append(f"  doi = {{{article.doi}}},")
            entry_lines.append(f"  url = {{{article.doi_url}}},")
        else:
            entry_lines.append(f"  url = {{{article.pubmed_url}}},")

        if article.pmid:
            entry_lines.append(f"  pmid = {{{article.pmid}}},")
        if article.pmcid:
            entry_lines.append(f"  pmcid = {{{article.pmcid}}},")

        entry_lines.append("}")
        return "\n".join(entry_lines)

    @staticmethod
    def export(search_result: SearchResult, filepath: Optional[str] = None) -> str:
        entries = [BibTeXExporter.article_to_bibtex(a) for a in search_result.articles]
        content = "\n\n".join(entries) + "\n"

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

        return content
