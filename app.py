"""
Medical Literature Auto Search - Streamlit Interactive Web Application.
Launch with: streamlit run app.py
"""

import os
import sys
from pathlib import Path
import streamlit as st

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

st.set_page_config(
    page_title="Hệ Thống Tìm Kiếm Y Văn Chuyên Ngành Uy Tín",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load configuration
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
journals_cfg = load_yaml_config(os.path.join(CONFIG_DIR, "journals.yaml"))

st.title("🔬 Hệ Thống Tìm Kiếm & Tổng Hợp Y Văn Chuyên Ngành")
st.caption("Tìm kiếm tự động từ các nguồn uy tín hàng đầu: **PubMed, NEJM, The Lancet, JAMA, BMJ, AHA (Circulation), ASH (Blood)...**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Cấu Hình Tìm Kiếm")
    
    topic = st.text_input(
        "Chủ đề y khoa cần tra cứu:",
        value="SGLT2 inhibitors in heart failure",
        help="Nhập bệnh lý, thuốc, can thiệp hoặc câu hỏi lâm sàng PICO."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        years_back = st.number_input("Khoảng năm (năm gần nhất):", min_value=0, max_value=30, value=5, step=1)
    with col2:
        max_results = st.number_input("Số bài báo tối đa:", min_value=5, max_value=100, value=20, step=5)
        
    top_tier_only = st.checkbox(
        "⭐ Chỉ tìm trong tạp chí Top-Tier",
        value=False,
        help="Nếu bật, chỉ giữ lại các bài đăng trên NEJM, Lancet, JAMA, BMJ, Circulation, Blood... Nếu tắt, tìm toàn bộ PubMed và ưu tiên xếp hạng cao các tạp chí này."
    )
    
    # Journal Groups
    available_groups = {
        "general_medicine": "Đa khoa (NEJM, The Lancet, JAMA, BMJ, Ann Intern Med)",
        "cardiology_aha": "Tim mạch (AHA Circulation, JAHA, Stroke, JACC, ESC EHJ)",
        "hematology_ash": "Huyết học & Ung thư (ASH Blood, ASCO JCO, Leukemia...)",
        "biomedical_top": "Y sinh dịch mã (Nature Medicine, Science Transl Med, Cell...)"
    }
    selected_groups = st.multiselect(
        "Lọc chuyên khoa tạp chí:",
        options=list(available_groups.keys()),
        format_func=lambda x: available_groups[x],
        default=[]
    )
    
    # Evidence Types
    article_types_opts = {
        "guidelines": "Hướng dẫn thực hành (Practice Guidelines)",
        "meta_analyses": "Phân tích gộp (Meta-Analysis)",
        "systematic_reviews": "Tổng quan hệ thống (Systematic Review)",
        "rct": "Thử nghiệm ngẫu nhiên có đối chứng (RCT)",
        "clinical_trials": "Thử nghiệm lâm sàng (Clinical Trials)",
        "reviews": "Tổng quan (Reviews)"
    }
    selected_types = st.multiselect(
        "Phân hạng thiết kế nghiên cứu:",
        options=list(article_types_opts.keys()),
        format_func=lambda x: article_types_opts[x],
        default=["guidelines", "meta_analyses", "systematic_reviews", "rct"]
    )
    
    sort_by = st.selectbox(
        "Sắp xếp kết quả:",
        options=["tier", "pub_date", "relevance"],
        format_func=lambda x: "⭐ Độ uy tín tạp chí (Tier)" if x == "tier" else ("📅 Mới nhất" if x == "pub_date" else "🎯 Độ liên quan")
    )
    
    enable_ai = st.checkbox("🧠 Tự động tổng hợp bằng chứng lâm sàng", value=True)
    
    search_button = st.button("🚀 BẮT ĐẦU TÌM KIẾM", type="primary", use_container_width=True)

if search_button:
    if not topic.strip():
        st.error("Vui lòng nhập chủ đề nghiên cứu!")
    else:
        with st.spinner("Đang xây dựng cú pháp truy vấn chuyên sâu và quét cơ sở dữ liệu PubMed..."):
            builder = QueryBuilder(journals_cfg)
            query = builder.build_pubmed_query(
                topic=topic,
                years_back=years_back,
                top_tier_only=top_tier_only,
                journal_groups=selected_groups if selected_groups else None,
                article_types=selected_types if selected_types else None
            )
            
            client = PubMedClient()
            pmids, count = client.search_pmids(query=query, retmax=max_results, sort="pub_date" if sort_by == "pub_date" else "relevance")
            
            # Fallback if zero found in top tier
            if not pmids and top_tier_only:
                st.warning("Không có kết quả trong chế độ 'Chỉ tạp chí danh giá'. Đang tự động mở rộng toàn bộ PubMed và ưu tiên xếp hạng cao các tạp chí này...")
                query = builder.build_pubmed_query(topic=topic, years_back=years_back, top_tier_only=False, article_types=selected_types)
                pmids, count = client.search_pmids(query=query, retmax=max_results)

        if not pmids:
            st.warning(f"Không tìm thấy bài báo nào cho chủ đề: '{topic}'. Vui lòng thử từ khóa rộng hơn.")
        else:
            with st.spinner(f"Đã phát hiện {count} bài báo. Đang tải dữ liệu chi tiết {len(pmids)} bài báo và kiểm tra Open Access..."):
                articles = client.fetch_articles_by_pmids(pmids)
                
                # Filter & rank
                j_filter = JournalFilter(journals_cfg)
                articles = j_filter.enrich_and_rank(articles, sort_by=sort_by)
                
                # Europe PMC PDF links
                pmc_client = EuropePMCClient()
                articles = pmc_client.enrich_articles(articles)
                
                # AI synthesis
                ai_synth = None
                if enable_ai:
                    with st.spinner("Đang phân tích và tổng hợp bằng chứng y văn..."):
                        synthesizer = ClinicalSynthesizer()
                        ai_synth = synthesizer.synthesize(topic, articles)
                
                result = SearchResult(
                    topic=topic,
                    query_executed=query,
                    total_found_in_pubmed=count,
                    articles=articles,
                    ai_synthesis=ai_synth
                )
                st.session_state["search_result"] = result

if "search_result" in st.session_state:
    res: SearchResult = st.session_state["search_result"]
    articles = res.articles
    top_tier_count = sum(1 for a in articles if a.is_top_tier)
    oa_pdf_count = sum(1 for a in articles if a.pdf_url or a.free_fulltext_url)

    # Metrics
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng trên PubMed", f"{res.total_found_in_pubmed:,}")
    m2.metric("Bài tuyển chọn", len(articles))
    m3.metric("Tạp chí Top-Tier ⭐", top_tier_count)
    m4.metric("Có PDF Miễn phí 📄", oa_pdf_count)
    
    with st.expander("🔍 Xem cú pháp truy vấn PubMed đã thực thi"):
        st.code(res.query_executed, language="sql")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧠 Tổng Hợp Bằng Chứng",
        "📊 Bảng Danh Sách Bài Báo",
        "📖 Đọc Chi Tiết & Abstract",
        "💾 Tải Xuống Báo Cáo"
    ])

    with tab1:
        st.markdown(res.ai_synthesis or "Chưa có bản tổng hợp.")

    with tab2:
        table_data = []
        for i, a in enumerate(articles, 1):
            table_data.append({
                "STT": i,
                "Tên bài báo": a.title,
                "Tạp chí": a.journal_iso or a.journal,
                "Top-Tier": "⭐ Có" if a.is_top_tier else "Không",
                "Năm": a.pub_year or "N/A",
                "Thiết kế": ", ".join(a.article_types[:2]) if a.article_types else "Study",
                "PMID": a.pmid,
                "PubMed": a.pubmed_url,
                "PDF Link": a.pdf_url or a.free_fulltext_url or "N/A"
            })
        st.dataframe(table_data, use_container_width=True)

    with tab3:
        for i, a in enumerate(articles, 1):
            badge = "⭐ TOP-TIER JOURNAL" if a.is_top_tier else "INDEXED JOURNAL"
            with st.container():
                st.subheader(f"{i}. {a.title}")
                st.caption(f"**Tạp chí:** {a.journal} ({a.journal_iso}) | **Hạng:** `{badge}` | **Năm:** {a.pub_year or 'N/A'}")
                st.write(f"**Tác giả:** {a.author_display}")
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                with col_btn1:
                    st.link_button("🌐 Mở PubMed", a.pubmed_url)
                with col_btn2:
                    if a.pdf_url:
                        st.link_button("📄 Tải PDF Free", a.pdf_url)
                    elif a.free_fulltext_url:
                        st.link_button("📖 Xem Full-Text", a.free_fulltext_url)
                
                with st.expander("Xem tóm tắt nghiên cứu (Abstract)", expanded=False):
                    st.markdown(a.abstract if a.abstract else "*Không có tóm tắt công khai.*")
                st.markdown("---")

    with tab4:
        st.subheader("Tải xuống toàn bộ tài liệu nghiên cứu đã tổng hợp")
        
        md_content = MarkdownExporter.export(res)
        bib_content = BibTeXExporter.export(res)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                label="📝 Tải báo cáo Markdown (.md)",
                data=md_content,
                file_name=f"report_{res.topic}.md",
                mime="text/markdown"
            )
        with col_d2:
            st.download_button(
                label="🏷️ Tải file trích dẫn BibTeX (.bib) cho EndNote/Zotero",
                data=bib_content,
                file_name=f"references_{res.topic}.bib",
                mime="text/plain"
            )
