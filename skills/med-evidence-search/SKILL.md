---
name: med-evidence-search
description: Tự động tìm kiếm, sàng lọc và tổng hợp y văn quốc tế chuyên sâu từ các nguồn uy tín cao như PubMed, NEJM, The Lancet, JAMA, BMJ, AHA (Circulation, Stroke, JAHA), ASH (Blood), JCO... Tự động phân cấp bằng chứng lâm sàng (Guidelines, Meta-analyses, Systematic Reviews, RCTs), tích hợp link tải trực tiếp PDF miễn phí qua Europe PMC và xuất báo cáo Markdown, CSV, BibTeX. Kích hoạt khi user cần tìm tài liệu y văn quốc tế, tra cứu bằng chứng lâm sàng, tổng hợp nghiên cứu từ các tạp chí uy tín.
---

# Medical Evidence Search Skill

Kỹ năng tìm kiếm, trích xuất và tổng hợp y văn y khoa quốc tế từ các nguồn có độ tin cậy và Impact Factor hàng đầu thế giới.

## 🎯 Khi nào kích hoạt Skill này?
Kích hoạt skill này khi người dùng:
- Yêu cầu tìm kiếm tài liệu, bài báo khoa học, y văn y học quốc tế về một chủ đề lâm sàng.
- Muốn tra cứu các nghiên cứu từ các tạp chí danh giá: **NEJM, The Lancet, JAMA, BMJ, Circulation (AHA), Blood (ASH), JCO, Annals of Internal Medicine, Nature Medicine...**
- Cần tổng hợp bằng chứng theo tháp y học thực chứng: **Practice Guidelines, Meta-Analyses, Systematic Reviews, Randomized Controlled Trials (RCTs)**.
- Cần danh mục trích dẫn chuẩn **BibTeX** cho Zotero/EndNote hoặc bảng **CSV/Excel** để sàng lọc tài liệu làm đề cương/luận văn.

---

## 🛠️ Cách thực thi tìm kiếm

Chạy script Python tích hợp sẵn trong plugin:

```bash
python3 ~/.gemini/config/plugins/med-evidence-search/skills/med-evidence-search/scripts/search_runner.py \
  --topic "<CHỦ_ĐỀ_NGHIÊN_CỨU>" \
  --years <SỐ_NĂM> \
  --limit <SỐ_BÀI_TỐI_ĐA> \
  --top-tier-only \
  --output-dir "<THƯ_MỤC_XUẤT_BÁO_CÁO>"
```

### Các tùy chọn chính:
- `--topic` / `-t`: Chủ đề nghiên cứu (tiếng Anh hoặc thuật ngữ y khoa quốc tế, ví dụ: `"SGLT2 inhibitors in heart failure"`, `"CAR-T cell therapy lymphoma"`).
- `--years` / `-y`: Giới hạn số năm gần nhất (mặc định: 5 năm, đặt `0` để không giới hạn).
- `--limit` / `-n`: Số lượng bài báo tối đa cần lấy (mặc định: 20).
- `--top-tier-only`: Chỉ tìm kiếm trong các tạp chí Top-Tier (NEJM, Lancet, JAMA, BMJ, AHA, ASH...).
- `--groups` / `-g`: Chọn chuyên khoa cụ thể:
  - `general_medicine`: NEJM, The Lancet, JAMA, BMJ, Ann Intern Med.
  - `cardiology_aha`: Circulation, JAHA, Stroke, JACC, European Heart Journal.
  - `hematology_ash`: Blood, Blood Advances, JCO, Leukemia.
  - `biomedical_top`: Nature Medicine, Science Transl Med, Cell.
- `--types`: Lọc loại nghiên cứu: `guidelines,meta_analyses,systematic_reviews,rct,clinical_trials,reviews`.
- `--json-output`: Xuất kết quả dạng JSON ra màn hình để agent đọc và xử lý tiếp.

---

## 📄 Các tệp xuất bản tự động
Mỗi lần chạy sẽ tự động sinh ra các file tại thư mục đích:
1. `report_<topic>.md`: Báo cáo tổng quan chi tiết, bảng tổng hợp bằng chứng, tóm tắt abstract từng bài và các liên kết trực tiếp (PubMed, DOI, link tải PDF Free).
2. `report_<topic>.csv`: Bảng dữ liệu sàng lọc mở được bằng Microsoft Excel / Google Sheets.
3. `report_<topic>.bib`: Danh mục trích dẫn chuẩn BibTeX để import vào EndNote, Zotero, Mendeley.
