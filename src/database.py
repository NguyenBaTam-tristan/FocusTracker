import sqlite3
import os
import sys

# Đảm bảo đường dẫn tuyệt đối an toàn tuyệt đối kể cả khi đóng gói thành file .exe sau này
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "focus_data.db")

def init_db():
    """Khởi tạo cấu trúc cơ sở dữ liệu SQLite v2.0 gồm 2 bảng quan hệ"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Bảng 1: Lưu trữ tổng quan của cả phiên học sau khi kết thúc
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            start_time TEXT,
            target_goal TEXT,           -- Mục tiêu tự gõ ban đầu
            study_time_seconds INTEGER,
            distracted_time_seconds INTEGER,
            idle_time_seconds INTEGER,
            final_flow_score REAL       -- Điểm hiệu suất chắt lọc cuối ngày
        )
    ''')
    
    # Bảng 2: Nhật ký Timeline chi tiết vĩnh viễn (Tab gì, ở lại bao lâu, trạng thái gì)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp TEXT,             -- Mốc thời gian chính xác ghi nhận
            window_title TEXT,          -- Tên chính xác của ứng dụng/tab trình duyệt
            duration_seconds INTEGER,   -- Số giây ở lại ứng dụng này
            status TEXT,                -- 'focus', 'distracted', hoặc 'idle'
            FOREIGN KEY (session_id) REFERENCES study_sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("💾 [DATABASE v2.0] Hệ thống cơ sở dữ liệu thô đã thiết lập thành công!")

def insert_session(date, start_time, target_goal):
    """Khởi tạo trước 1 bản ghi phiên học khi bấm Start để lấy ID liên kết dữ liệu"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO study_sessions (date, start_time, target_goal, study_time_seconds, distracted_time_seconds, idle_time_seconds, final_flow_score)
            VALUES (?, ?, ?, 0, 0, 0, 0.0)
        ''', (date, start_time, target_goal))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    except Exception as e:
        print(f"❌ Lỗi khởi tạo phiên học trong Database: {e}")
        return None

def log_timeline_event(session_id, timestamp, window_title, duration, status):
    """Ghi lại chi tiết tab gì, mở bao lâu để lưu trữ làm tài nguyên cho AI và biểu đồ"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO focus_timeline (session_id, timestamp, window_title, duration_seconds, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, timestamp, window_title, duration, status))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi ghi nhật ký timeline: {e}")

def update_session_summary(session_id, study_time, distracted_time, idle_time, flow_score):
    """Cập nhật dữ liệu chắt lọc tổng quan khi bấm hoàn thành phiên học"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE study_sessions
            SET study_time_seconds = ?, distracted_time_seconds = ?, idle_time_seconds = ?, final_flow_score = ?
            WHERE id = ?
        ''', (study_time, distracted_time, idle_time, flow_score, session_id))
        conn.commit()
        conn.close()
        print(f"✅ [DATABASE] Đã đồng bộ tổng kết phiên học #{session_id} vào ổ cứng thành công!")
    except Exception as e:
        print(f"❌ Lỗi cập nhật tổng kết phiên học: {e}")