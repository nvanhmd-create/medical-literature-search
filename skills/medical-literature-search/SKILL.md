---
name: medical-literature-search
description: Tự động tìm kiếm, phân loại và tổng hợp y văn chuyên ngành từ các tạp chí y khoa danh giá nhất thế giới (NEJM, The Lancet, JAMA, BMJ, AHA, ASH...). Truy vấn PubMed với bộ lọc MeSH/EBM, liên kết Europe PMC tải PDF toàn văn miễn phí và xuất báo cáo đa định dạng (Markdown, BibTeX, CSV, JSON).
---

# Kỹ Năng Tìm Kiếm & Tổng Hợp Y Văn Chuyên Ngành (Medical Literature Search)

Kỹ năng này trang bị cho Agent quy trình chuyên nghiệp để hỗ trợ các bác sĩ, nhà nghiên cứu lâm sàng, học viên sau đại học tìm kiếm, chọn lọc và tổng hợp y văn từ các nguồn uy tín cao nhất.

---

## 📌 Các Phương Thức Thực Hiện (Operation Modes)

Agent có thể linh hoạt thực hiện theo 2 phương thức tùy theo ngữ cảnh của người dùng:

### Cách 1 — Trực tiếp trên Chat (Direct In-Chat Synthesis)
Khi người dùng đặt câu hỏi lâm sàng cần tra cứu nhanh (ví dụ: *"Tìm các thử nghiệm RCTs mới nhất về can thiệp lấy huyết khối cơ học"*):
1. Phân tích câu hỏi theo mô hình **PICO**:
   - **P (Population):** Đối tượng bệnh nhân hoặc bệnh lý cụ thể.
   - **I (Intervention):** Thuốc, thủ thuật hoặc phương pháp điều trị cần đánh giá.
   - **C (Comparison):** Nhóm chứng, giả dược hoặc phác đồ chuẩn.
   - **O (Outcomes):** Kết cục lâm sàng then chốt (tử vong, tàn phế mRS, biến cố tái phát...).
2. Thiết lập truy vấn PubMed tối ưu (sử dụng thuật ngữ MeSH và từ khóa trong `[tiab]`).
3. Ưu tiên bài báo từ các tạp chí **Tier 1** (NEJM, Lancet, JAMA, BMJ, Circulation, Stroke, JACC, Blood...).
4. Trình bày **Bảng ma trận bằng chứng** kèm liên kết tải PDF toàn văn miễn phí (Europe PMC / PMC) và mã trích dẫn BibTeX.

### Cách 2 — Thực thi Pipeline Tự Động (Python Engine Execution)
Khi người dùng muốn xuất file báo cáo hoàn chỉnh vào thư mục `./reports`:
Chạy script `main.py` với các tham số tương ứng:
```bash
python3 main.py \
  --topic "<Chủ đề nghiên cứu>" \
  --years <Số năm gần nhất, mặc định 5> \
  --limit <Số lượng bài tối đa, mặc định 20> \
  --top-tier-only \
  --sort tier
```

---

## 🏗️ Cấu Trúc Báo Cáo Tổng Hợp Bằng Chứng (Synthesis Output Format)

Báo cáo tổng hợp bằng chứng lâm sàng chuẩn mực PHẢI bao gồm:

### 1. Tóm Tắt Tổng Quan (Executive Clinical Summary)
- Bối cảnh lâm sàng và vấn đề thời sự cần giải quyết.
- Đánh giá tổng quan về mức độ đồng thuận giữa các nghiên cứu.

### 2. Bảng Ma Trận Bằng Chứng (Evidence Matrix Table)
| STT | Năm | Tạp chí | Tác giả | Thiết kế | Cỡ mẫu ($N$) | Can thiệp vs Đối chứng | Kết quả chính ($p$, HR/RR, 95% CI) | Liên kết toàn văn |
|:---:|:---:|:---|:---|:---:|:---:|:---|:---|:---:|
| 1 | 2024 | NEJM | Smith et al. | RCT đa trung tâm | 1,200 | Thuốc A vs Placebo | Giảm 24% tử vong (HR 0.76; 95% CI 0.62–0.93; $p=0.008$) | [PMID](https://pubmed.ncbi.nlm.nih.gov/...) / [PDF Free](...) |

### 3. Phân Tích Chuyên Sâu & Khuyến Cáo Thực Hành (Clinical Practice Insights)
- Điểm mới nổi bật so với các phác đồ cũ.
- Tác dụng phụ, biến cố bất lợi hoặc các cảnh báo an toàn.
- Hướng dẫn điều trị mới nhất của hiệp hội chuyên khoa đã cập nhật kết quả này hay chưa.

### 4. Hạn Chế Của Nghiên Cứu (Study Limitations & Risk of Bias)
- Nguy cơ sai số chọn mẫu, mất dấu theo dõi (loss to follow-up), hoặc tài trợ từ công ty dược phẩm.
- Tính khái quát hóa (generalizability) trên quần thể bệnh nhân Việt Nam/Châu Á.

### 5. Danh Mục Trích Dẫn Chuẩn BibTeX (BibTeX Citations)
Cung cấp sẵn khối mã BibTeX để người dùng sao chép vào Zotero / EndNote / Overleaf:
```bibtex
@article{Smith2024,
  author = {Smith, John and Doe, Jane},
  title = {Efficacy of Novel Therapy in Clinical Practice},
  journal = {The New England Journal of Medicine},
  year = {2024},
  doi = {10.1056/NEJMoa2400000},
  pmid = {38000000}
}
```

---

## 💻 Giao Diện Web Tương Tác (Streamlit Web Dashboard)
Để mở bảng điều khiển trực quan trên trình duyệt:
```bash
streamlit run app.py
```
Giao diện cho phép:
- Nhập chủ đề nghiên cứu bằng ngôn ngữ tự nhiên.
- Chọn lọc tạp chí theo từng phân chuyên khoa (Đa khoa, Tim mạch AHA, Huyết học ASH, Y sinh đỉnh cao).
- Tùy chỉnh bộ lọc tháp bằng chứng (Guidelines, Meta-Analyses, RCTs...).
- Tải ngay các file báo cáo (`.md`, `.csv`, `.bib`, `.json`) chỉ với một cú nhấp chuột.
