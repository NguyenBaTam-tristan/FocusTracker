import time
import win32gui
from pynput import mouse, keyboard
from datetime import datetime
import config  # Gọi luật chơi từ config.py
import database  # Gọi hàm lưu log từ database.py

class FocusTracker:
    def __init__(self, session_id, whitelist, study_duration_minutes):
        self.session_id = session_id
        # Chuyển whitelist về chữ thường toàn bộ để đối chiếu chính xác
        self.whitelist = [item.lower() for item in whitelist]
        self.duration_seconds = study_duration_minutes * 60
        
        # Các biến đếm thời gian thực tế (giây)
        self.total_study_time = 0
        self.total_distracted_time = 0
        self.total_idle_time = 0
        self.total_penalty_time = 0  # Thời gian phạt tích lũy
        
        # Biến trạng thái để theo dõi hành vi theo thời gian thực
        self.is_running = False
        self.last_input_time = time.time()
        self.current_window_title = ""
        self.current_status = "idle"  # focus, distracted, idle
        
        # Bộ đếm để tính toán "Độ lún sâu" xao nhãng liên tục
        self.continuous_distraction_seconds = 0
        
        # Mảng lưu vết tạm thời các sự kiện đổi tab trước khi xả vào Database
        self.timeline_events = []
        self.tab_start_time = time.time()
        self.tab_window_title = ""
        self.tab_status = ""

        # Kích hoạt bộ lắng nghe chuột và bàn phím để kiểm tra Idle (Ngủ gục)
        self.mouse_listener = mouse.Listener(on_move=self._on_activity, on_click=self._on_activity, on_scroll=self._on_activity)
        self.keyboard_listener = keyboard.Listener(on_press=self._on_activity)

    def _on_activity(self, *args, **kwargs):
        """Hàm tự động kích hoạt khi có tương tác phần cứng để reset thời gian Idle"""
        self.last_input_time = time.time()

    def _get_active_window_title(self):
        """Gọi Windows API để lấy chính xác tiêu đề cửa sổ / tab Chrome đang active"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title if title else "Unknown Window"
        except Exception:
            return "Unknown Window"

    def _record_tab_segment(self, next_title, next_status):
        """Khi user đổi sang tab khác hoặc đổi trạng thái, đóng gói số giây ở lại tab cũ và lưu lại"""
        now = time.time()
        duration = int(now - self.tab_start_time)
        
        if duration > 0 and self.tab_window_title:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.timeline_events.append({
                "timestamp": timestamp,
                "window_title": self.tab_window_title[:100], # Cắt ngắn tiêu đề cho sạch DB
                "duration": duration,
                "status": self.tab_status
            })
            
        # Reset mốc thời gian cho tab mới
        self.tab_start_time = now
        self.tab_window_title = next_title
        self.tab_status = next_status

    def start_session(self):
        """Kích hoạt cỗ máy quét ngầm hệ thống"""
        self.is_running = True
        self.last_input_time = time.time()
        start_session_time = time.time()
        
        # Chạy bộ lắng nghe phần cứng
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Khởi tạo trạng thái tab đầu tiên
        self.tab_window_title = self._get_active_window_title()
        self.tab_status = "focus"
        self.tab_start_time = time.time()

        print("\n🔥 [ENGINE] Vòng kiểm soát hệ thống đã kích hoạt ngầm!")
        
        try:
            while self.is_running:
                current_time = time.time()
                elapsed_time = current_time - start_session_time
                
                # Điều kiện dừng: Hết thời gian cam kết học của phiên
                if elapsed_time >= self.duration_seconds:
                    print("\n⏰ [ENGINE] Đã hết thời gian cam kết học tập!")
                    break
                
                # 1. KIỂM TRA TRẠNG THÁI IDLE (NGỦ GỤC/RỜI BÀN)
                if current_time - self.last_input_time > config.IDLE_THRESHOLD:
                    new_status = "idle"
                    self.total_idle_time += 1
                    self.continuous_distraction_seconds = 0 # Đang ngủ thì không tính lún sâu xao nhãng
                else:
                    # 2. KIỂM TRA XAO NHÃNG DỰA TRÊN WHITELIST ĐỘNG
                    self.current_window_title = self._get_active_window_title()
                    current_title_lower = self.current_window_title.lower()
                    
                    # Kiểm tra xem tiêu đề hiện tại có chứa từ khóa nào nằm trong whitelist không
                    is_valid = any(allowed_app in current_title_lower for allowed_app in self.whitelist)
                    
                    if is_valid:
                        new_status = "focus"
                        self.total_study_time += 1
                        self.continuous_distraction_seconds = 0
                    else:
                        new_status = "distracted"
                        self.total_distracted_time += 1
                        self.continuous_distraction_seconds += 1
                        
                        # ÁP DỤNG THUẬT TOÁN PHẠT LŨY TIẾN THEO ĐỘ LÚN SÂU
                        if self.continuous_distraction_seconds <= config.SHORT_DISTRACTION_LIMIT:
                            self.total_penalty_time += config.MULTIPLIER_LOW
                        elif self.continuous_distraction_seconds <= config.LONG_DISTRACTION_LIMIT:
                            self.total_penalty_time += config.MULTIPLIER_MED
                        else:
                            self.total_penalty_time += config.MULTIPLIER_HIGH
                            
                        # Tạo áp lực tâm lý: Cứ mỗi 10 giây vi phạm liên tục thì in cảnh báo sát thương
                        if self.continuous_distraction_seconds % config.MAX_DISTRACTION_ALLOWED == 0:
                            import random
                            print(f"\n{random.choice(config.WARNING_MESSAGES)}")

                # Nếu phát hiện đổi tab hoặc đổi trạng thái, thực hiện ghi nhận đoạn dữ liệu cũ
                if self.current_window_title != self.tab_window_title or new_status != self.tab_status:
                    self._record_tab_segment(self.current_window_title, new_status)

                self.tab_status = new_status
                time.sleep(1) # Quét đều đặn mỗi giây
                
        finally:
            return self.stop_session()

    def stop_session(self):
        """Dừng quét hệ thống, đóng gói và xả toàn bộ dữ liệu thô vào SQLite"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # Dừng các bộ lắng nghe phần cứng
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        
        # Ghi nhận đoạn dữ liệu của tab cuối cùng trước khi đóng app
        self._record_tab_segment("", "")
        
        # THUẬT TOÁN CHẮT LỌC HIỆU SUẤT TỔNG THỂ (FINAL FLOW SCORE)
        # Flow Score = (Thời gian học thực tế / (Tổng thời gian phiên + Thời gian phạt tích lũy)) * 100
        total_session_seconds = self.total_study_time + self.total_distracted_time + self.total_idle_time
        if total_session_seconds > 0:
            denominator = total_session_seconds + self.total_penalty_time
            flow_score = (self.total_study_time / denominator) * 100
            flow_score = round(flow_score, 2)
        else:
            flow_score = 0.0
            
        # 1. Đẩy toàn bộ dữ liệu timeline thô từ mảng tạm vào SQLite
        print(f"🔄 [ENGINE] Đang ghi nhận {len(self.timeline_events)} lịch sử đổi tab vào Database...")
        for event in self.timeline_events:
            database.log_timeline_event(
                session_id=self.session_id,
                timestamp=event["timestamp"],
                window_title=event["window_title"],
                duration=event["duration"],
                status=event["status"]
            )
            
        # 2. Cập nhật bảng tổng quan phiên học
        database.update_session_summary(
            session_id=self.session_id,
            study_time=self.total_study_time,
            distracted_time=self.total_distracted_time,
            idle_time=self.total_idle_time,
            flow_score=flow_score
        )
        
        return {
            "study_time": self.total_study_time,
            "distracted_time": self.total_distracted_time,
            "idle_time": self.total_idle_time,
            "flow_score": flow_score
        }