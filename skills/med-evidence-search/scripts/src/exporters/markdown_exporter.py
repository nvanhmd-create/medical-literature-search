"""
Markdown Report Exporter.
Generates an executive clinical evidence report in Markdown format.
"""

from typing import Optional
from ..core.models import SearchResult, Article


class MarkdownExporter:
    @staticmethod
    def export(search_result: SearchResult, filepath: Optional[str] = None) -> str:
        lines = []

        # Header
        lines.append(f"# 📚 BÁO CÁO TỔNG QUAN Y VĂN CHUYÊN NGÀNH: {search_result.topic.upper()}")
        lines.append(f"**Ngày trích xuất:** {search_result.created_at} | **Tổng số bài báo:** {len(search_result.articles)} bài báo")
        lines.append("")

        # Search Query & Metadata Box
        lines.append("> [!NOTE]")
        lines.append(f"> **Chủ đề tìm kiếm:** `{search_result.topic}`  ")
        lines.append(f"> **Câu lệnh truy vấn (PubMed Query):** `{search_result.query_executed}`  ")
        lines.append(f"> **Tổng số kết quả trên PubMed:** {search_result.total_found_in_pubmed}  ")
        top_count = sum(1 for a in search_result.articles if a.is_top_tier)
        lines.append(f"> **Bài báo từ tạp chí Top-Tier (NEJM, Lancet, JAMA, AHA, ASH...):** {top_count}/{len(search_result.articles)}")
        lines.append("")

        # Clinical Synthesis Section
        lines.append("## 🧠 1. TỔNG QUAN & TỔNG HỢP BẰNG CHỨNG LÂM SÀNG")
        lines.append("")
        if search_result.ai_synthesis:
            lines.append(search_result.ai_synthesis)
        else:
            lines.append("*Chưa có bản tổng hợp bằng chứng lâm sàng.*")
        lines.append("")

        # Summary Table
        lines.append("## 📊 2. BẢNG TỔNG HỢP CÁC BÀI BÁO TIÊU BIỂU")
        lines.append("")
        lines.append("| STT | Tên bài báo | Tạp chí | Năm | Thiết kế nghiên cứu | Nguồn Full-text |")
        lines.append("| :---: | :--- | :---: | :---: | :--- | :---: |")

        for i, a in enumerate(search_result.articles, 1):
            tier_badge = "⭐ **[TOP]** " if a.is_top_tier else ""
            title_esc = a.title.replace("|", "\\|")
            journal_esc = (a.journal_iso or a.journal or "Unknown").replace("|", "\\|")
            year_str = str(a.pub_year or "N/A")
            types_str = "<br>".join(a.article_types[:2]) if a.article_types else "Study"
            
            links = [f"[PubMed]({a.pubmed_url})"]
            if a.doi_url:
                links.append(f"[DOI]({a.doi_url})")
            if a.pdf_url:
                links.append(f"[📄 PDF Free]({a.pdf_url})")
            elif a.free_fulltext_url:
                links.append(f"[FullText]({a.free_fulltext_url})")
            link_str = " \\| ".join(links)

            lines.append(f"| {i} | {tier_badge}{title_esc} | {journal_esc} | {year_str} | {types_str} | {link_str} |")

        lines.append("")

        # Detailed Abstracts
        lines.append("## 📖 3. CHI TIẾT TỪNG CÔNG TRÌNH NGHIÊN CỨU")
        lines.append("")

        for i, a in enumerate(search_result.articles, 1):
            badge = "⭐ TOP-TIER JOURNAL" if a.is_top_tier else "INDEXED JOURNAL"
            lines.append(f"### {i}. {a.title}")
            lines.append(f"- **Tạp chí:** `{a.journal}` ({a.journal_iso}) — `{badge}`")
            lines.append(f"- **Tác giả:** {a.author_display} ({', '.join(a.authors[:3]) + ('...' if len(a.authors) > 3 else '')})")
            lines.append(f"- **Năm xuất bản:** {a.pub_date or a.pub_year or 'N/A'}")
            if a.article_types:
                lines.append(f"- **Loại ấn phẩm:** {', '.join(a.article_types)}")
            if a.doi:
                lines.append(f"- **DOI:** [{a.doi}]({a.doi_url})")
            lines.append(f"- **PMID:** [{a.pmid}]({a.pubmed_url})")
            if a.pdf_url:
                lines.append(f"- **Link tải PDF trực tiếp:** [Tải bài báo PDF]({a.pdf_url})")
            elif a.free_fulltext_url:
                lines.append(f"- **Toàn văn miễn phí:** [Đọc Full-Text]({a.free_fulltext_url})")
            
            if a.mesh_terms:
                lines.append(f"- **Từ khóa MeSH:** `{', '.join(a.mesh_terms[:6])}`")

            lines.append("")
            lines.append("#### Tóm tắt (Abstract):")
            if a.abstract:
                lines.append(a.abstract)
            else:
                lines.append("*Bài báo này không có tóm tắt công khai trên PubMed.*")
            lines.append("")
            lines.append("---")
            lines.append("")

        content = "\n".join(lines)
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

        return content
