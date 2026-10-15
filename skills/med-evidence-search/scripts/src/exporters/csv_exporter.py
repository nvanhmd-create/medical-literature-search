"""
CSV Exporter.
Exports articles into structured CSV format for Excel, Google Sheets, or PRISMA review tracking.
Uses standard library csv module with utf-8-sig encoding for perfect Excel compatibility.
"""

import csv
from typing import Optional
from ..core.models import SearchResult


class CSVExporter:
    @staticmethod
    def export(search_result: SearchResult, filepath: str) -> None:
        headers = [
            "STT",
            "PMID",
            "Title",
            "Journal",
            "Journal_ISO",
            "Is_Top_Tier",
            "Journal_Group",
            "Pub_Year",
            "Pub_Date",
            "First_Author",
            "All_Authors",
            "Article_Types",
            "DOI",
            "PMCID",
            "PubMed_URL",
            "DOI_URL",
            "Free_FullText_URL",
            "PDF_URL",
            "Citation_Count",
            "MeSH_Terms",
            "Abstract",
        ]

        with open(filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)

            for i, a in enumerate(search_result.articles, 1):
                writer.writerow([
                    i,
                    a.pmid,
                    a.title,
                    a.journal,
                    a.journal_iso,
                    "YES" if a.is_top_tier else "NO",
                    a.journal_group,
                    a.pub_year or "",
                    a.pub_date,
                    a.authors[0] if a.authors else "",
                    "; ".join(a.authors),
                    "; ".join(a.article_types),
                    a.doi,
                    a.pmcid,
                    a.pubmed_url,
                    a.doi_url or "",
                    a.free_fulltext_url or "",
                    a.pdf_url or "",
                    a.citation_count if a.citation_count is not None else "",
                    "; ".join(a.mesh_terms),
                    a.abstract,
                ])
