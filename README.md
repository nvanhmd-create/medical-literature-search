# 🔬 Medical Literature Auto Search & Clinical Evidence Synthesis
### Hệ thống Tự Động Tìm Kiếm & Tổng Hợp Y Văn Chuyên Ngành Từ Các Nguồn Uy Tín Cao

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated%20Workflow-blue?logo=github-actions)](https://github.com)
[![PubMed](https://img.shields.io/badge/Source-PubMed%20%7C%20NCBI-green)](https://pubmed.ncbi.nlm.nih.gov/)
[![Journals](https://img.shields.io/badge/Top--Tier-NEJM%20%7C%20Lancet%20%7C%20JAMA%20%7C%20AHA%20%7C%20ASH-red)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dự án mã nguồn mở hỗ trợ bác sĩ, nhà nghiên cứu lâm sàng, học viên cao học và nghiên cứu sinh tự động tìm kiếm, phân loại và tổng hợp y văn từ các nguồn tạp chí danh tiếng nhất thế giới dựa trên một chủ đề nghiên cứu bất kỳ.

---

## 🌟 Các Nguồn Y Văn & Tạp Chí Danh Giá Được Hỗ Trợ

Hệ thống được tích hợp sẵn bộ lọc và thuật toán xếp hạng ưu tiên các tạp chí y khoa có Impact Factor cao và các hội chuyên khoa hàng đầu:

1. **Đa khoa lâm sàng tổng quát (General Medicine)**:
   - **NEJM** (*The New England Journal of Medicine*)
   - **The Lancet** & các chuyên san (*Lancet Oncology, Lancet Infectious Diseases, Lancet Neurology, Lancet Diabetes & Endocrinology, Lancet Haematology...*)
   - **JAMA** & hệ thống JAMA Network (*JAMA Internal Medicine, JAMA Cardiology, JAMA Oncology, JAMA Neurology...*)
   - **The BMJ** (*British Medical Journal*)
   - **Annals of Internal Medicine**
2. **Tim mạch & Mạch máu (AHA / ACC / ESC)**:
   - **Circulation** (*American Heart Association - AHA*)
   - **Circulation Research**, **Circulation: Heart Failure**
   - **JAHA** (*Journal of the American Heart Association*)
   - **Stroke** (*AHA*)
   - **JACC** (*Journal of the American College of Cardiology*)
   - **European Heart Journal** (*ESC*)
3. **Huyết học & Ung thư học (ASH / ASCO)**:
   - **Blood** (*American Society of Hematology - ASH*)
   - **Blood Advances** (*ASH*)
   - **JCO** (*Journal of Clinical Oncology - ASCO*)
   - **Leukemia**
4. **Y sinh dịch mã & Đỉnh cao nghiên cứu (Translational & High Impact)**:
   - **Nature Medicine**, **Science Translational Medicine**, **Cell**

---

## 🚀 Tính Năng Cốt Lõi

- 🔍 **Truy vấn PubMed thông minh**: Tự động chuyển đổi chủ đề sang cú pháp Boolean & MeSH chuẩn quốc tế.
- 🎯 **Lọc theo tháp bằng chứng (Evidence-Based Medicine)**: Ưu tiên Hướng dẫn điều trị (*Guidelines*), Phân tích gộp (*Meta-Analyses*), Tổng quan hệ thống (*Systematic Reviews*), Thử nghiệm ngẫu nhiên có đối chứng (*RCTs*).
- 📄 **Tự động liên kết tải PDF toàn văn miễn phí**: Tích hợp API **Europe PMC** để phát hiện các bài báo Open Access và gắn link tải PDF trực tiếp.
- 🧠 **AI Clinical Evidence Synthesis**: Tự động tổng kết kết quả lâm sàng then chốt, ý nghĩa thực hành và hạn chế nghiên cứu.
- 📊 **Xuất đa định dạng chuyên nghiệp**:
  - `report.md`: Báo cáo chi tiết dạng Markdown kèm bảng tóm tắt và abstract.
  - `report.csv`: Bảng dữ liệu sàng lọc dùng cho Excel / Google Sheets hoặc sơ đồ PRISMA.
  - `report.bib`: Danh mục trích dẫn chuẩn BibTeX để import trực tiếp vào **Zotero, EndNote, Mendeley**.
  - `report.json`: Dữ liệu có cấu trúc cho các ứng dụng phần mềm khác.
- 🤖 **Tự động hóa hoàn toàn trên GitHub (GitHub Actions)**: Chạy tìm kiếm trực tiếp trên giao diện web GitHub mà không cần cài đặt phần mềm trên máy tính.
- 💻 **Giao diện Web tương tác (Streamlit)**: Tìm kiếm trực quan trên trình duyệt chỉ với 1 dòng lệnh.

---

## 📂 Cấu Trúc Thư Mục

```text
├── .github/
│   └── workflows/
│       └── search.yml          # GitHub Actions: Chạy tự động trên web GitHub
├── config/
│   ├── journals.yaml           # Danh mục và từ khóa của các tạp chí danh giá
│   └── default_config.yaml     # Cấu hình tìm kiếm mặc định
├── src/
│   ├── core/
│   │   ├── models.py           # Data models: Article, SearchResult
│   │   ├── query_builder.py    # Xây dựng cú pháp truy vấn MeSH & Top-Tier
│   │   ├── pubmed_client.py    # Kết nối NCBI PubMed E-Utilities API
│   │   └── europe_pmc_client.py# Lấy link PDF Open Access và số trích dẫn
│   ├── filters/
│   │   └── journal_filter.py   # Nhận diện và xếp hạng tạp chí (Top-Tier vs Indexed)
│   ├── summarizer/
│   │   └── ai_synthesizer.py   # Phân tích & tổng hợp bằng chứng lâm sàng
│   ├── exporters/
│   │   ├── markdown_exporter.py# Xuất báo cáo Markdown
│   │   ├── bibtex_exporter.py  # Xuất danh mục BibTeX
│   │   └── csv_exporter.py     # Xuất bảng Excel/CSV
│   └── utils/
│       └── config_loader.py    # Nạp cấu hình an toàn
├── reports/                    # Thư mục lưu các báo cáo đã xuất
├── scripts/
│   └── example_search.sh       # Script ví dụ mẫu
├── tests/
│   └── test_search.py          # Bộ kiểm thử tự động (Unit Tests)
├── main.py                     # Giao diện dòng lệnh (CLI)
├── app.py                      # Giao diện Web tương tác (Streamlit)
├── requirements.txt            # Thư viện phụ thuộc
├── .gitignore
├── LICENSE                     # MIT License
└── README.md                   # Hướng dẫn sử dụng chi tiết
```

---

## 🛠️ Cài Đặt & Sử Dụng Trên Máy Tính Cá Nhân

### 1. Yêu cầu hệ thống
- Python 3.9 trở lên
- Git

### 2. Cài đặt môi trường
```bash
# Clone repository về máy
git clone <URL_REPO_CUA_BAN>
cd "Tìm kiếm tài liệu chuyên ngành"

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

> **Lưu ý**: Công cụ lõi CLI `main.py` được tối ưu hóa để có thể hoạt động hoàn toàn bằng thư viện chuẩn của Python mà không bắt buộc phải cài thêm gói bên ngoài nếu chỉ chạy tìm kiếm cơ bản.

---

## 🖥️ Cách 1: Chạy Từ Giao Diện Dòng Lệnh (CLI)

### Cú pháp cơ bản:
```bash
python3 main.py -t "TÊN_CHỦ_ĐỀ_NGHIÊN_CỨU"
```

### Các ví dụ thực tế:

**Ví dụ 1: Tìm kiếm trong Tim mạch (AHA/ACC) 5 năm gần nhất, chỉ lấy tạp chí Top-Tier:**
```bash
python3 main.py \
  --topic "SGLT2 inhibitors in heart failure" \
  --years 5 \
  --limit 20 \
  --top-tier-only \
  --groups cardiology_aha general_medicine
```

**Ví dụ 2: Tìm kiếm Huyết học & Ung thư (ASH/ASCO) về liệu pháp tế bào CAR-T:**
```bash
python3 main.py \
  --topic "CAR-T cell therapy in diffuse large B-cell lymphoma" \
  --years 3 \
  --limit 15 \
  --top-tier-only \
  --groups hematology_ash
```

**Ví dụ 3: Chỉ tìm kiếm Hướng dẫn điều trị (Guidelines) và Thử nghiệm lâm sàng (RCTs):**
```bash
python3 main.py \
  --topic "acute ischemic stroke endovascular thrombectomy" \
  --types guidelines,rct \
  --years 5
```

### Bảng tham số dòng lệnh:

| Tham số | Viết tắt | Mặc định | Ý nghĩa |
| :--- | :---: | :---: | :--- |
| `--topic` | `-t` | *Nhập tay* | Chủ đề nghiên cứu y khoa |
| `--years` | `-y` | `5` | Số năm gần nhất cần tìm (đặt `0` để không giới hạn) |
| `--limit` | `-n` | `20` | Số lượng bài báo tối đa cần lấy |
| `--top-tier-only`| | `False` | Chỉ lấy bài báo thuộc danh sách NEJM, Lancet, JAMA, AHA, ASH... |
| `--groups` | `-g` | Tất cả | Nhóm tạp chí: `general_medicine`, `cardiology_aha`, `hematology_ash`, `biomedical_top` |
| `--types` | | Đa dạng | Lọc theo loại bài báo: `guidelines`, `meta_analyses`, `systematic_reviews`, `rct`, `clinical_trials`, `reviews` |
| `--sort` | | `tier` | Tiêu chí xếp hạng: `tier` (uy tín tạp chí), `pub_date` (mới nhất), `relevance` |
| `--output-dir`| `-o` | `./reports` | Thư mục lưu kết quả xuất bản |

---

## 🌐 Cách 2: Chạy Giao Diện Web Trực Quan (Streamlit UI)

Chỉ cần gõ lệnh sau trên terminal:
```bash
streamlit run app.py
```
Trình duyệt web sẽ tự động mở giao diện trực quan cho phép bạn:
- Nhập chủ đề nghiên cứu.
- Kéo thanh trượt chọn số năm và số bài báo.
- Tích chọn lọc chuyên khoa (Tim mạch AHA, Huyết học ASH, Đa khoa NEJM/Lancet...).
- Xem bảng tổng hợp, đọc tóm tắt nghiên cứu (Abstract) và click tải trực tiếp PDF toàn văn.
- Tải về file Markdown, Excel CSV và BibTeX chỉ với một cú nhấp chuột.

---

## ⚡ Cách 3: Tự Động Hóa Hoàn Toàn Trên GitHub (GitHub Actions)

Bạn có thể chạy tìm kiếm y văn trực tiếp trên trang GitHub của bạn mà không cần mở máy tính!

1. Đẩy code lên GitHub repository của bạn.
2. Trên giao diện GitHub của repository, bấm vào tab **Actions**.
3. Chọn workflow **"🔍 Automated Medical Literature Search"** ở cột bên trái.
4. Bấm nút **Run workflow**:
   - Nhập chủ đề nghiên cứu (ví dụ: `GLP-1 receptor agonists in chronic kidney disease`).
   - Chọn số năm, số lượng bài báo và bật/tắt chế độ Top-Tier Only.
   - Bấm **Run workflow**.
5. Sau 1-2 phút, GitHub Actions sẽ:
   - Tự động chạy toàn bộ quy trình tìm kiếm và tổng hợp y văn.
   - Hiển thị bản tóm tắt lâm sàng ngay trên trang tóm tắt của GitHub (**Job Summary**).
   - Tự động lưu và commit các file báo cáo vào thư mục `reports/` trong repository của bạn.
   - Đóng gói file zip trong phần **Artifacts** để bạn tải về máy bất cứ lúc nào.

---

## 🔑 Cấu Hình Biến Môi Trường (Tùy Chọn)

Hệ thống hoạt động ngay lập tức mà không bắt buộc có API key. Tuy nhiên, bạn có thể bổ sung các khóa sau để tăng cường sức mạnh:

1. **`NCBI_API_KEY`** (Miễn phí từ [NCBI Account](https://www.ncbi.nlm.nih.gov/account/)):
   - Tăng tốc độ truy vấn PubMed từ 3 requests/giây lên 10 requests/giây.
2. **`GEMINI_API_KEY`** (Miễn phí từ [Google AI Studio](https://aistudio.google.com/)):
   - Tự động kích hoạt tính năng AI tổng hợp bằng chứng lâm sàng chuyên sâu bằng Tiếng Việt (hoặc Tiếng Anh).

### Cách thiết lập:
- **Trên máy tính**:
  ```bash
  export NCBI_API_KEY="your_ncbi_key"
  export GEMINI_API_KEY="your_gemini_key"
  ```
- **Trên GitHub Repository**:
  Vào `Settings` -> `Secrets and variables` -> `Actions` -> Thêm `GEMINI_API_KEY` và `NCBI_API_KEY`.

---

## 🧪 Kiểm Thử Hệ Thống (Unit Tests)

Để kiểm tra độ chính xác của các thuật toán nhận diện tạp chí và trích xuất dữ liệu:
```bash
python3 -m unittest discover tests
```

---

## 📄 Bản Quyền & Giấy Phép

Dự án được phân phối dưới giấy phép **MIT License**. Bạn được toàn quyền sử dụng, sao chép, sửa đổi cho mục đích nghiên cứu học thuật và y khoa lâm sàng.
