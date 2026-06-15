# AntiGravity Security Testing Framework

Hệ thống Kiểm thử An ninh Mạng không dây (WiFi) & Thiết bị Mạng Quang (GPON).

## 🚀 Tính năng

- **Lõi xử lý đa nhiệm (Core Engine)**: Điều phối toàn bộ vòng đời kiểm thử (setup, execution, teardown, reporting) qua Event Bus.
- **Kiểm thử WiFi**: Evil Twin, 802.1X Enterprise authentication, WPA2 KRACK, Kr00k, FragAttacks, và WPA3 SAE Dragonfly fuzzing.
- **Kiểm thử GPON**: LOID/SN Cloning, Rogue ONU auto-discovery, Downstream AES-128, Optical Tapping detection, và Command Injection/FTP bypass.
- **Tích hợp CVE Engine**: Tự động ánh xạ và kiểm tra các lỗ hổng đã công bố (CVE-2025-29525, CVE-2025-63353, CVE-2026-2907, CVE-2026-5339, CVE-2025-10957).
- **Phân tích Anomaly bằng AI/ML**: Sử dụng mô hình *Isolation Forest* và *Random Forest Classifier* để phát hiện ONU giả mạo từ hành vi, công suất tín hiệu và tần suất bản tin đăng ký.
- **Báo cáo chuyên sâu**: Xuất báo cáo dưới dạng JSON và giao diện HTML tương tác cao.

## 🛠️ Cài đặt

Yêu cầu Python 3.11+.

```bash
# Phân quyền cho tập lệnh cài đặt
chmod +x scripts/setup_env.sh scripts/run_tests.sh

# Chạy tập lệnh cài đặt môi trường
./scripts/setup_env.sh

# Kích hoạt môi trường ảo
source venv/bin/activate
```

## 💻 Sử dụng CLI

Framework hỗ trợ CLI linh hoạt bằng `typer`:

```bash
# Chạy tất cả các plugin kiểm thử ở chế độ mô phỏng (Simulated Mode)
antigravity scan

# Chạy kiểm thử cho riêng module GPON
antigravity scan --module gpon

# Khởi chạy REST API Backend Server (FastAPI)
antigravity serve --host 127.0.0.1 --port 8000

# Khởi chạy Web Dashboard để xem báo cáo HTML
antigravity dashboard --host 127.0.0.1 --port 8080
```

## 🧪 Chạy Kiểm thử (Unit Tests)

```bash
./scripts/run_tests.sh
```
# BTL_ATTT
