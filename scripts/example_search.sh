#!/usr/bin/env bash
# Script ví dụ chạy tìm kiếm y văn nhanh chóng từ dòng lệnh

echo "🔬 Đang chạy ví dụ tìm kiếm y văn chuyên ngành..."

# Ví dụ 1: Tìm kiếm trong Tim mạch (AHA/ACC) về ức chế SGLT2 trong suy tim
python3 main.py \
  --topic "SGLT2 inhibitors in heart failure" \
  --years 5 \
  --limit 10 \
  --top-tier-only \
  --sort tier

echo "✅ Hoàn tất! Vui lòng kiểm tra báo cáo trong thư mục ./reports"
