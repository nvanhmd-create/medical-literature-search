#!/usr/bin/env python3
"""
Medical Literature Auto Search - Main CLI Entrypoint
Automated pipeline for searching and synthesizing clinical literature
from top-tier journals (NEJM, The Lancet, JAMA, BMJ, AHA, ASH, etc.).
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MedAutoSearch")


def sanitize_filename(name: str) -> str:
    s = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[-\s]+", "_", s)[:50]


def run_pipeline(
    topic: str,
    years_back: int = 5,
    top_tier_only: bool = False,
    journal_groups: list = None,
    article_types: list = None,
    limit: int = 20,
    sort_by: str = "tier",
    enable_ai: bool = True,
    output_dir: str = "./reports",
    config_dir: str = "./config"
) -> SearchResult:
    """
    Executes the end-to-end medical literature search and synthesis pipeline.
    """
    print("=" * 70)
    print("🔬 HỆ THỐNG TỰ ĐỘNG TÌM KIẾM Y VĂN CHUYÊN NGÀNH CHẤT LƯỢNG CAO")
    print("   Nguồn uy tín: PubMed, NEJM, The Lancet, JAMA, BMJ, AHA, ASH...")
    print("=" * 70)
    logger.info(f"Chủ đề nghiên cứu: '{topic}'")
    logger.info(f"Cấu hình: Top-Tier Only={top_tier_only} | {years_back} năm gần nhất | Tối đa {limit} bài")

    # 1. Load Configurations
    journals_cfg_path = os.path.join(config_dir, "journals.yaml")
    journals_cfg = load_yaml_config(journals_cfg_path)

    # 2. Build Query
    builder = QueryBuilder(journals_cfg)
    query = builder.build_pubmed_query(
        topic=topic,
        years_back=years_back,
        top_tier_only=top_tier_only,
        journal_groups=journal_groups,
        article_types=article_types
    )
    logger.info(f"Query PubMed được tạo:\n>>> {query}\n")

    # 3. Search PubMed
    ncbi_api_key = os.getenv("NCBI_API_KEY")
    pubmed_client = PubMedClient(api_key=ncbi_api_key)
    pmids, total_count = pubmed_client.search_pmids(
        query=query,
        retmax=limit,
        sort="pub_date" if sort_by == "pub_date" else "relevance"
    )

    # Fallback if strict query returned 0 results
    if not pmids and top_tier_only:
        logger.warning("Không tìm thấy kết quả trong chế độ 'Chỉ tạp chí danh giá' (Top-Tier Only).")
        logger.info("Đang tự động mở rộng tìm kiếm toàn bộ PubMed và ưu tiên xếp hạng các tạp chí uy tín...")
        query = builder.build_pubmed_query(
            topic=topic,
            years_back=years_back,
            top_tier_only=False,
            journal_groups=None,
            article_types=article_types
        )
        pmids, total_count = pubmed_client.search_pmids(query=query, retmax=limit)

    if not pmids:
        logger.warning(f"Không tìm thấy bài báo nào cho chủ đề: '{topic}'")
        res = SearchResult(
            topic=topic,
            query_executed=query,
            total_found_in_pubmed=0,
            articles=[],
            ai_synthesis="Không có dữ liệu bài báo để tổng hợp."
        )
        return res

    logger.info(f"Đã tìm thấy {total_count} bài báo trên PubMed. Đang trích xuất chi tiết {len(pmids)} bài báo tiêu biểu...")

    # 4. Fetch Full Metadata & Abstracts
    articles = pubmed_client.fetch_articles_by_pmids(pmids)

    # 5. Enrich & Rank with Journal Filter
    j_filter = JournalFilter(journals_cfg)
    articles = j_filter.enrich_and_rank(articles, sort_by=sort_by)

    # 6. Enrich with Europe PMC (Free PDF, OA links, Citations)
    logger.info("Đang liên kết dữ liệu với Europe PMC để tìm kiếm liên kết tải PDF Full-text miễn phí...")
    pmc_client = EuropePMCClient()
    articles = pmc_client.enrich_articles(articles)

    # 7. AI Clinical Evidence Synthesis
    ai_synthesis = None
    if enable_ai:
        logger.info("Đang tổng hợp bằng chứng lâm sàng & phân tích chuyên sâu...")
        synthesizer = ClinicalSynthesizer()
        ai_synthesis = synthesizer.synthesize(topic, articles)

    # Build SearchResult
    result = SearchResult(
        topic=topic,
        query_executed=query,
        total_found_in_pubmed=total_count,
        articles=articles,
        ai_synthesis=ai_synthesis
    )

    # 8. Export Reports
    os.makedirs(output_dir, exist_ok=True)
    slug = sanitize_filename(topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"report_{slug}_{timestamp}"

    md_path = os.path.join(output_dir, f"{base_filename}.md")
    csv_path = os.path.join(output_dir, f"{base_filename}.csv")
    bib_path = os.path.join(output_dir, f"{base_filename}.bib")
    json_path = os.path.join(output_dir, f"{base_filename}.json")

    # Export Markdown
    MarkdownExporter.export(result, md_path)
    # Export CSV
    CSVExporter.export(result, csv_path)
    # Export BibTeX
    BibTeXExporter.export(result, bib_path)
    # Export JSON
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump({
            "topic": result.topic,
            "created_at": result.created_at,
            "query_executed": result.query_executed,
            "total_found_in_pubmed": result.total_found_in_pubmed,
            "articles": [a.to_dict() for a in result.articles],
            "ai_synthesis": result.ai_synthesis
        }, jf, ensure_ascii=False, indent=2)

    top_tier_count = sum(1 for a in articles if a.is_top_tier)
    oa_pdf_count = sum(1 for a in articles if a.pdf_url or a.free_fulltext_url)

    print("\n" + "=" * 70)
    print("✅ QUÁ TRÌNH TÌM KIẾM VÀ TỔNG HỢP HOÀN TẤT THÀNH CÔNG!")
    print(f"📊 Kết quả: {len(articles)} bài báo được tuyển chọn.")
    print(f"⭐ Tạp chí danh giá (NEJM, Lancet, JAMA, AHA, ASH...): {top_tier_count} bài.")
    print(f"📄 Bài báo có thể đọc / tải PDF miễn phí: {oa_pdf_count} bài.")
    print("\n📁 Các tệp báo cáo đã xuất:")
    print(f"  - 📝 Báo cáo tổng quan (Markdown): {md_path}")
    print(f"  - 📊 Bảng dữ liệu sàng lọc (Excel/CSV): {csv_path}")
    print(f"  - 🏷️ Danh mục trích dẫn (BibTeX):   {bib_path}")
    print(f"  - 💾 Dữ liệu máy học (JSON):        {json_path}")
    print("=" * 70 + "\n")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Tự động tìm kiếm & tổng hợp y văn chuyên ngành từ các nguồn uy tín hàng đầu."
    )
    parser.add_argument(
        "-t", "--topic",
        type=str,
        help="Chủ đề nghiên cứu (ví dụ: 'SGLT2 inhibitors heart failure', 'CAR-T lymphoma')"
    )
    parser.add_argument(
        "-y", "--years",
        type=int,
        default=5,
        help="Khoảng năm tìm kiếm (mặc định: 5 năm gần nhất, đặt 0 để không giới hạn)"
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=20,
        help="Số lượng bài báo tối đa cần lấy (mặc định: 20)"
    )
    parser.add_argument(
        "--top-tier-only",
        action="store_true",
        help="Chỉ tìm kiếm trong các tạp chí danh giá hàng đầu (NEJM, Lancet, JAMA, BMJ, AHA, ASH...)"
    )
    parser.add_argument(
        "-g", "--groups",
        type=str,
        nargs="+",
        help="Nhóm tạp chí cụ thể (ví dụ: cardiology_aha, hematology_ash, general_medicine)"
    )
    parser.add_argument(
        "--types",
        type=str,
        help="Danh sách loại bài báo, phân tách bằng dấu phẩy: guidelines,meta_analyses,systematic_reviews,rct,clinical_trials,reviews,all"
    )
    parser.add_argument(
        "--sort",
        type=str,
        default="tier",
        choices=["tier", "pub_date", "relevance"],
        help="Cách sắp xếp kết quả: 'tier' (độ uy tín tạp chí), 'pub_date' (mới nhất), 'relevance'"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Tắt tính năng AI tổng hợp lâm sàng (sử dụng tổng hợp cấu trúc tiêu chuẩn)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="./reports",
        help="Thư mục lưu trữ báo cáo xuất bản (mặc định: ./reports)"
    )

    args = parser.parse_args()

    # Interactive prompt if topic is not passed via CLI
    topic = args.topic
    if not topic:
        try:
            print("Nhập chủ đề nghiên cứu y khoa cần tìm kiếm:")
            topic = input("👉 Chủ đề: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nĐã hủy thao tác.")
            sys.exit(0)

    if not topic:
        print("Lỗi: Chủ đề tìm kiếm không được để trống!")
        sys.exit(1)

    article_types = None
    if args.types:
        article_types = [t.strip() for t in args.types.split(",") if t.strip()]

    run_pipeline(
        topic=topic,
        years_back=args.years,
        top_tier_only=args.top_tier_only,
        journal_groups=args.groups,
        article_types=article_types,
        limit=args.limit,
        sort_by=args.sort,
        enable_ai=not args.no_ai,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
