#!/usr/bin/env python3
"""
Medical Evidence Search Runner for Antigravity Plugin.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from src.core.models import SearchResult
from src.core.query_builder import QueryBuilder
from src.core.pubmed_client import PubMedClient
from src.core.europe_pmc_client import EuropePMCClient
from src.filters.journal_filter import JournalFilter
from src.summarizer.ai_synthesizer import ClinicalSynthesizer
from src.exporters.markdown_exporter import MarkdownExporter
from src.exporters.bibtex_exporter import BibTeXExporter
from src.exporters.csv_exporter import CSVExporter
from src.utils.config_loader import load_yaml_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("MedPluginSearch")


def main():
    parser = argparse.ArgumentParser(description="Plugin CLI for Medical Evidence Search")
    parser.add_argument("-t", "--topic", type=str, required=True, help="Clinical research topic")
    parser.add_argument("-y", "--years", type=int, default=5, help="Years back")
    parser.add_argument("-n", "--limit", type=int, default=20, help="Maximum articles")
    parser.add_argument("--top-tier-only", action="store_true", help="Only search within Top-Tier journals")
    parser.add_argument("-g", "--groups", type=str, nargs="+", help="Journal groups")
    parser.add_argument("--types", type=str, help="Comma-separated article types")
    parser.add_argument("--sort", type=str, default="tier", choices=["tier", "pub_date", "relevance"])
    parser.add_argument("-o", "--output-dir", type=str, default="./reports")
    parser.add_argument("--json-output", action="store_true", help="Output JSON result directly to stdout")

    args = parser.parse_args()

    # Load configuration
    cfg_dir = os.path.join(PLUGIN_ROOT, "config")
    journals_cfg = load_yaml_config(os.path.join(cfg_dir, "journals.yaml"))

    article_types = [t.strip() for t in args.types.split(",") if t.strip()] if args.types else None

    # 1. Query Builder
    builder = QueryBuilder(journals_cfg)
    query = builder.build_pubmed_query(
        topic=args.topic,
        years_back=args.years,
        top_tier_only=args.top_tier_only,
        journal_groups=args.groups,
        article_types=article_types
    )

    # 2. PubMed search
    ncbi_key = os.getenv("NCBI_API_KEY")
    client = PubMedClient(api_key=ncbi_key)
    pmids, total_count = client.search_pmids(
        query=query,
        retmax=args.limit,
        sort="pub_date" if args.sort == "pub_date" else "relevance"
    )

    # Fallback if zero found in top tier
    if not pmids and args.top_tier_only:
        query = builder.build_pubmed_query(
            topic=args.topic,
            years_back=args.years,
            top_tier_only=False,
            journal_groups=None,
            article_types=article_types
        )
        pmids, total_count = client.search_pmids(query=query, retmax=args.limit)

    if not pmids:
        print(f"Không tìm thấy bài báo nào cho chủ đề: '{args.topic}'")
        sys.exit(0)

    # 3. Fetch detailed articles
    articles = client.fetch_articles_by_pmids(pmids)

    # 4. Filter & Rank
    j_filter = JournalFilter(journals_cfg)
    articles = j_filter.enrich_and_rank(articles, sort_by=args.sort)

    # 5. Enrich with Europe PMC
    pmc_client = EuropePMCClient()
    articles = pmc_client.enrich_articles(articles)

    # 6. Synthesize
    synthesizer = ClinicalSynthesizer()
    ai_synth = synthesizer.synthesize(args.topic, articles)

    result = SearchResult(
        topic=args.topic,
        query_executed=query,
        total_found_in_pubmed=total_count,
        articles=articles,
        ai_synthesis=ai_synth
    )

    # Export
    os.makedirs(args.output_dir, exist_ok=True)
    import re
    slug = re.sub(r"[^\w\s-]", "", args.topic).strip().lower()
    slug = re.sub(r"[-\s]+", "_", slug)[:50]
    base_file = os.path.join(args.output_dir, f"report_{slug}")

    md_path = f"{base_file}.md"
    csv_path = f"{base_file}.csv"
    bib_path = f"{base_file}.bib"

    MarkdownExporter.export(result, md_path)
    CSVExporter.export(result, csv_path)
    BibTeXExporter.export(result, bib_path)

    if args.json_output:
        print(json.dumps({
            "topic": result.topic,
            "total_found": result.total_found_in_pubmed,
            "articles_count": len(result.articles),
            "top_tier_count": sum(1 for a in result.articles if a.is_top_tier),
            "markdown_path": os.path.abspath(md_path),
            "csv_path": os.path.abspath(csv_path),
            "bibtex_path": os.path.abspath(bib_path),
            "ai_synthesis": result.ai_synthesis
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Đã xuất báo cáo thành công tại: {md_path}")


if __name__ == "__main__":
    main()
