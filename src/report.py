import sqlite3
import os
import sys
import matplotlib.pyplot as plt
import urllib.request
import urllib.parse
import json
from google import genai
import config  # Gọi token và id chat Telegram từ config.py
import database  # Gọi đường dẫn DB_PATH

# Thiết lập đường dẫn thư mục gốc để lưu ảnh báo cáo an toàn
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_and_send_report(session_id):
    """Hàm tổng hợp: Vẽ đồ thị -> Gọi Gemini AI -> Gửi Telegram cho Mẹ"""
    print(f"📊 [REPORT] Đang xử lý báo cáo phân tích cho Session #{session_id}...")
    
    # =====================================================================
    # LẤY DỮ LIỆU TỪ SQLITE
    # =====================================================================
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    
    # Lấy thông tin tổng quan của session
    cursor.execute("SELECT date, start_time, target_goal, study_time_seconds, distracted_time_seconds, idle_time_seconds, final_flow_score FROM study_sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    
    if not session:
        print("❌ [REPORT] Không tìm thấy dữ liệu phiên học trong Database.")
        conn.close()
        return
        
    date, start_time, target_goal, study_sec, distract_sec, idle_sec, flow_score = session
    
    # Lấy dữ liệu timeline chi tiết để AI phân tích sâu hành vi
    cursor.execute("SELECT window_title, duration_seconds, status FROM focus_timeline WHERE session_id = ? ORDER BY id ASC", (session_id,))
    timeline_rows = cursor.fetchall()
    conn.close()

    # Quy đổi thời gian ra phút cho dễ đọc
    study_min = round(study_sec / 60, 1)
    distract_min = round(distract_sec / 60, 1)
    idle_min = round(idle_sec / 60, 1)
    total_min = round((study_sec + distract_sec + idle_sec) / 60, 1)

    # =====================================================================
    # BƯỚC 1: VẼ BIỂU ĐỒ TRỰC QUAN (MATPLOTLIB)
    # =====================================================================
    labels = ['Tập trung học', 'Xao nhãng tab lạ', 'Treo máy / Idle']
    sizes = [study_sec, distract_sec, idle_sec]
    colors = ['#22c55e', '#ef4444', '#9ca3af'] # Xanh lá | Đỏ xao nhãng | Xám ngủ gục
    
    # Nếu phiên học chưa có dữ liệu xao nhãng hoặc idle, tránh việc biểu đồ bị lỗi chia cho 0
    if sum(sizes) == 0:
        sizes = [1, 0, 0]

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, 
            textprops={'fontsize': 12, 'weight': 'bold'})
    plt.title(f"BÁO CÁO HIỆU SUẤT HỌC TẬP ({date})\nĐiểm Flow Score: {flow_score}%", fontsize=14, weight='bold', pad=20)
    
    # Lưu ảnh biểu đồ ra ổ cứng
    report_img_path = os.path.join(BASE_DIR, "report.png")
    plt.tight_layout()
    plt.savefig(report_img_path, dpi=100)
    plt.close()
    print("📈 [REPORT] Đã vẽ và xuất biểu đồ phân tích thành công!")

    # =====================================================================
    # BƯỚC 2: GỌI GEMINI AI FREE ĐỂ NHẬN XÉT SÒNG PHẲNG
    # =====================================================================
    # Chuẩn bị dữ liệu thô dạng văn bản để nạp làm Prompt cho AI
    timeline_summary = ""
    for row in timeline_rows[:15]: # Lấy tối đa 15 hành vi đổi tab nổi bật nhất để tránh tràn prompt
        timeline_summary += f"- Mở cửa sổ '{row[0]}' trong {row[1]} giây [Trạng thái: {row[2]}].\n"

    prompt = f"""
    Bạn là một chuyên gia phân tích dữ liệu học tập và là một Mentor cực kỳ sòng phẳng, nghiêm khắc nhưng yêu thương học viên.
    Hãy đọc dữ liệu phiên học ngày hôm nay của học viên Nguyễn Bá Tâm và đưa ra một đoạn nhận xét tổng hợp gửi cho Mẹ của bạn ấy.

    DỮ LIỆU THỰC TẾ TỪ HỆ THỐNG:
    - Ngày học: {date} lúc {start_time}
    - Mục tiêu Tâm tự cam kết ban đầu: "{target_goal}"
    - Tổng thời gian ngồi máy: {total_min} phút
    - Thời gian thực sự tập trung học: {study_min} phút
    - Thời gian bị xao nhãng bấm sang tab lạ: {distract_min} phút
    - Thời gian treo máy không tương tác (ngủ gục/rời bàn): {idle_min} phút
    - Điểm hiệu suất chắt lọc cuối cùng (Flow Score): {flow_score}/100

    NHẬT KÝ CHI TIẾT CÁC TAB ĐÃ MỞ:
    {timeline_summary}

    YÊU CẦU ĐOẠN NHẬN XÉT:
    1. Văn phong lịch sự, trang trọng vì đây là báo cáo gửi cho Mẹ của Tâm, nhưng phải tuyệt đối TRUNG THỰC, sòng phẳng, phản ánh đúng số liệu.
    2. Đối chiếu xem với số liệu tập trung đó thì Tâm đã hoàn thành mục tiêu đề ra chưa. Khen ngợi nhiệt tình nếu Flow Score > 80%, nhắc nhở thẳng thắn và chỉ ra lỗ hổng xao nhãng nếu Flow Score thấp.
    3. Đoạn nhận xét ngắn gọn, cô đọng dưới 200 từ để đọc nhanh trên điện thoại.
    """

    ai_verdict = "Hệ thống AI đang bảo trì, không thể xuất lời nhận xét."
    try:
        # Ép nhận diện API Key trực tiếp từ file config.py thay vì tìm biến môi trường lỏng lẻo
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
        ai_verdict = response.text.strip()
        print("🤖 [REPORT] Gemini AI đã hoàn thành việc phán xét hiệu suất!")
    except Exception as e:
        # Dòng này vô cùng quan trọng: Nếu lỗi, nó sẽ in tuốt tuột nguyên nhân thực tế ra Terminal để bro biết đường sửa
        print(f"❌ Lỗi chi tiết tại Gemini API: {e}")

    # =====================================================================
    # BƯỚC 3: TỰ ĐỘNG BẮN BÁO CÁO + BIỂU ĐỒ QUA TELEGRAM CHO MẸ
    # =====================================================================
    # Chuẩn bị nội dung tin nhắn Text tổng hợp
    # Tìm đoạn định nghĩa telegram_text cũ và sửa lại thành thẻ HTML như sau:
    telegram_text = (
        f"🔔 <b>BÁO CÁO KẾT QUẢ HỌC TẬP CỦA BÁ TÂM</b>\n"
        f"📅 Ngày: {date} | Bắt đầu: {start_time}\n"
        f"🎯 Mục tiêu đăng ký: <i>{target_goal}</i>\n"
        f"⏳ Tổng thời gian: {total_min} phút\n"
        f"🔥 <b>Điểm hiệu suất tập trung: {flow_score}/100</b>\n\n"
        f"🤖 <b>Lời nhận xét từ Trọng tài AI:</b>\n{ai_verdict.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}"
    )

    # Sử dụng thư viện urllib có sẵn của Python để gọi API Telegram (Né việc phải cài thêm thư viện phụ)
    bot_token = config.TELEGRAM_BOT_TOKEN
    chat_id = config.TELEGRAM_MOM_CHAT_ID

    if bot_token == "YOUR_BOT_TOKEN_HERE" or chat_id == "YOUR_MOMS_CHAT_ID_HERE":
        print("⚠️ [TELEGRAM] Bạn chưa cấu hình Token hoặc Chat ID trong file config.py! Không thể gửi cho Mẹ.")
        return

    try:
        # Gửi ảnh biểu đồ kèm caption nội dung văn bản qua API `sendPhoto` của Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        
        # Đọc file ảnh biểu đồ
        with open(report_img_path, "rb") as img_file:
            img_data = img_file.read()

        # Tạo Boundary để đóng gói dữ liệu Multipart Form-Data theo chuẩn HTTP
        boundary = "----WebKitFormBoundaryFocusTrackerV2"
        data = []
        
        # Thêm trường chat_id
        data.append(f"--{boundary}".encode())
        data.append(f'Content-Disposition: form-data; name="chat_id"'.encode())
        data.append(''.encode())
        data.append(str(chat_id).encode())
        
        # Thêm trường caption (Nội dung tin nhắn)
        data.append(f"--{boundary}".encode())
        data.append(f'Content-Disposition: form-data; name="caption"'.encode())
        data.append(''.encode())
        data.append(telegram_text.encode())
        
        # Thêm chế độ parse Markdown để in đậm chữ cho đẹp
        data.append(f"--{boundary}".encode())
        data.append(f'Content-Disposition: form-data; name="parse_mode"'.encode())
        data.append(''.encode())
        data.append("HTML".encode())
        
        # Thêm file ảnh dữ liệu
        data.append(f"--{boundary}".encode())
        data.append(f'Content-Disposition: form-data; name="photo"; filename="report.png"'.encode())
        data.append('Content-Type: image/png'.encode())
        data.append(''.encode())
        data.append(img_data)
        
        data.append(f"--{boundary}--".encode())
        
        # Gộp tất cả payload lại bằng dấu xuống dòng \r\n
        body = b"\r\n".join(data)
        
        # Thực hiện gửi Request HTTP POST lên Telegram Server
        req = urllib.request.Request(url, data=body)
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        
        with urllib.request.urlopen(req) as res:
            response_status = res.getcode()
            if response_status == 200:
                print("🚀 [TELEGRAM] Đã bắn toàn bộ biểu đồ và lời nhận xét AI sang máy Mẹ thành công rực rỡ!")
            else:
                print(f"❌ [TELEGRAM] Telegram Server trả về mã lỗi: {response_status}")
                
    except Exception as e:
        print(f"❌ [TELEGRAM] Lỗi kết nối khi gửi dữ liệu qua Telegram: {e}")