"""
Clinical Evidence Synthesizer & AI Summarizer.
Produces an executive evidence summary across all retrieved high-impact articles.
Supports Google Gemini API with seamless fallback to structured clinical synthesis.
"""

import os
import json
import logging
from typing import List, Optional
from ..core.models import Article

logger = logging.getLogger(__name__)


class ClinicalSynthesizer:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash", language: str = "vi"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.language = language

    def synthesize(self, topic: str, articles: List[Article]) -> str:
        """
        Synthesizes the search results into a coherent clinical summary.
        Uses Gemini API if available, otherwise generates a structured rule-based synthesis.
        """
        if not articles:
            return "Không tìm thấy bài báo nào phù hợp với tiêu chí tìm kiếm."

        if self.api_key:
            try:
                return self._synthesize_with_gemini(topic, articles)
            except Exception as e:
                logger.warning(f"Lỗi khi gọi Gemini API ({e}). Tự động chuyển sang tổng hợp phân tích cấu trúc.")

        return self._synthesize_rule_based(topic, articles)

    def _synthesize_with_gemini(self, topic: str, articles: List[Article]) -> str:
        import urllib.request
        import json

        # Prepare evidence context (top 8 articles to prevent token overflow)
        evidence_text = []
        for i, a in enumerate(articles[:8], 1):
            tier_badge = "[TOP TIER]" if a.is_top_tier else ""
            evidence_text.append(
                f"### Bài báo {i}: {a.title}\n"
                f"- Tạp chí: {a.journal} ({a.pub_year or 'N/A'}) {tier_badge}\n"
                f"- Tác giả: {a.author_display}\n"
                f"- Loại nghiên cứu: {', '.join(a.article_types) if a.article_types else 'Chưa phân loại'}\n"
                f"- Tóm tắt: {a.abstract[:800]}...\n"
            )

        context_str = "\n".join(evidence_text)

        prompt = f"""
Bạn là một chuyên gia y khoa và nhà nghiên cứu lâm sàng cấp cao.
Hãy viết một bản "TỔNG QUAN BẰNG CHỨNG LÂM SÀNG" (Clinical Evidence Synthesis) dựa trên các bài báo từ các tạp chí y khoa uy tín (NEJM, The Lancet, JAMA, BMJ, AHA, ASH, v.v.) về chủ đề:
"{topic}"

Danh sách các bài báo nghiên cứu thu thập được:
{context_str}

Yêu cầu xuất bản (Định dạng Markdown chuyên nghiệp, ngôn ngữ: {"Tiếng Việt" if self.language == 'vi' else 'English'}):
1. **Tóm tắt cốt lõi (Executive Summary)**: 2-3 câu tổng kết phát hiện quan trọng nhất.
2. **Bằng chứng từ các thử nghiệm / Hướng dẫn uy tín**: Phân tích những kết quả lâm sàng then chốt (hiệu quả điều trị, tính an toàn, endpoint chính). Nêu rõ tên tạp chí và năm xuất bản.
3. **Ý nghĩa trong thực hành lâm sàng (Clinical Implications)**: Bác sĩ điều trị nên áp dụng bằng chứng này như thế nào?
4. **Hạn chế & Khoảng trống nghiên cứu (Limitations & Future Directions)**: Những điều chưa rõ hoặc cần theo dõi thêm.
"""

        # Call Gemini REST API directly with standard library to avoid external dependency issues
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048,
            }
        }

        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidate = data.get("candidates", [])[0]
            content = candidate.get("content", {}).get("parts", [])[0].get("text", "")
            return content.strip()

    def _synthesize_rule_based(self, topic: str, articles: List[Article]) -> str:
        """
        Standard structured evidence synthesis without external LLM API.
        """
        top_tier_count = sum(1 for a in articles if a.is_top_tier)
        years = [a.pub_year for a in articles if a.pub_year]
        min_year = min(years) if years else "N/A"
        max_year = max(years) if years else "N/A"

        study_type_counts = {}
        for a in articles:
            for t in a.article_types:
                study_type_counts[t] = study_type_counts.get(t, 0) + 1

        top_journals = set(a.journal for a in articles if a.is_top_tier)

        lines = [
            f"### 📋 Tổng hợp bằng chứng cho chủ đề: **{topic}**",
            f"- **Phạm vi thời gian**: {min_year} – {max_year}",
            f"- **Tổng số bài báo tuyển chọn**: {len(articles)} bài báo.",
            f"- **Bài báo từ tạp chí danh giá (Top-Tier)**: {top_tier_count}/{len(articles)} bài "
            f"({', '.join(list(top_journals)[:5]) if top_journals else 'Đa nguồn uy tín'}).",
        ]

        if study_type_counts:
            top_types = sorted(study_type_counts.items(), key=lambda x: x[1], reverse=True)[:4]
            types_str = ", ".join([f"{k} ({v})" for k, v in top_types])
            lines.append(f"- **Phân bố thiết kế nghiên cứu**: {types_str}")

        lines.append("\n#### 💡 Các điểm sáng lâm sàng đáng chú ý:")
        for i, a in enumerate(articles[:5], 1):
            badge = "⭐ [TOP-TIER]" if a.is_top_tier else "📄"
            lines.append(f"{i}. {badge} **{a.title}** ({a.journal}, {a.pub_year or 'N/A'})")
            if a.abstract:
                # Get first 200 characters of abstract
                brief = a.abstract.replace("\n", " ")[:220].strip() + "..."
                lines.append(f"   > *{brief}*")

        lines.append("\n> 💡 *Gợi ý: Cấu hình biến môi trường `GEMINI_API_KEY` để tự động kích hoạt tính năng tổng hợp lâm sàng chuyên sâu bằng AI.*")

        return "\n".join(lines)
