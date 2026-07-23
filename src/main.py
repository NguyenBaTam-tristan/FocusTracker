import customtkinter as ctk
import win32gui
from datetime import datetime
import multiprocessing
import database  # Gọi module database.py
from tracker import FocusTracker

# Cấu hình giao diện chuẩn Dark Mode hiện đại
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LauncherGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("FOCUS TRACKER v2.0")
        self.geometry("600x550")
        self.resizable(False, False)
        
        # Lấy danh sách các ứng dụng thực tế đang mở trên máy
        self.running_windows = self._get_all_running_windows()
        self.selected_whitelist = []
        
        self._build_ui()
        
    def _get_all_running_windows(self):
        """Quét toàn bộ hệ thống để lấy tiêu đề các cửa sổ đang hiển thị trên Taskbar"""
        titles = set()
        
        def enum_windows_proc(hwnd, lParam):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and not title.isspace():
                    titles.add(title)
            return True
            
        win32gui.EnumWindows(enum_windows_proc, None)
        return sorted(list(titles))

    def _build_ui(self):
        """Thiết kế bố cục giao diện trực quan"""
        # 1. Tiêu đề chính
        self.lbl_title = ctk.CTkLabel(self, text="⚡ THIẾT LẬP PHIÊN HỌC TẬP KỶ LUẬT ⚡", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_title.pack(pady=15)
        
        # 2. Ô nhập mục tiêu
        self.lbl_goal = ctk.CTkLabel(self, text="Hôm nay bạn quyết tâm hoàn thành mục tiêu gì?", font=ctk.CTkFont(size=13))
        self.lbl_goal.pack(pady=2)
        self.txt_goal = ctk.CTkEntry(self, width=500, placeholder_text="Ví dụ: Học 50 từ vựng Kanji, Code xong module DB...")
        self.txt_goal.pack(pady=5)
        
        # 3. Ô chọn thời gian học (Phút)
        self.lbl_time = ctk.CTkLabel(self, text="Chọn thời gian bạn muốn tập trung (Phút):", font=ctk.CTkFont(size=13))
        self.lbl_time.pack(pady=5)
        self.txt_time = ctk.CTkEntry(self, width=150, placeholder_text="Ví dụ: 45, 60, 90...")
        self.txt_time.pack(pady=2)
        
        # 4. Khu vực lựa chọn Whitelist động
        self.lbl_whitelist = ctk.CTkLabel(self, text="Tích chọn các ứng dụng/tab bạn ĐƯỢC PHÉP mở để học:", font=ctk.CTkFont(size=13))
        self.lbl_whitelist.pack(pady=10)
        
        # Khung cuộn chứa danh sách Checkbox
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=480, height=200)
        self.scroll_frame.pack(pady=5)
        
        self.checkboxes = []
        for win_title in self.running_windows:
            display_text = win_title[:60] + "..." if len(win_title) > 60 else win_title
            cb = ctk.CTkCheckBox(self.scroll_frame, text=display_text, font=ctk.CTkFont(size=11))
            cb.pack(anchor="w", pady=4, padx=10)
            self.checkboxes.append((cb, win_title.lower()))
            
        # 5. Nút bấm Start
        self.btn_start = ctk.CTkButton(self, text="BẮT ĐẦU PHIÊN HỌC STATE FLOW", font=ctk.CTkFont(size=14, weight="bold"), 
                                       fg_color="#1f538d", hover_color="#14375e", height=40, command=self._start_session)
        self.btn_start.pack(pady=15)

    def _start_session(self):
        """Xử lý kích hoạt khi người dùng bấm Start"""
        target_goal = self.txt_goal.get().strip()
        study_time_str = self.txt_time.get().strip()
        
        # Ép buộc nhập mục tiêu
        if not target_goal:
            self.lbl_goal.configure(text="⚠️ BẮT BUỘC: Bạn phải nhập mục tiêu!", text_color="red")
            return
            
        # Ép buộc kiểm tra thời gian hợp lệ
        try:
            study_minutes = int(study_time_str)
            if study_minutes <= 0:
                raise ValueError
        except ValueError:
            self.lbl_time.configure(text="⚠️ BẮT BUỘC: Thời gian phải là số nguyên dương!", text_color="red")
            return
            
        # Thu thập whitelist được chọn
        for cb, original_title in self.checkboxes:
            if cb.get() == 1:
                self.selected_whitelist.append(original_title)
                
        # Tự động cho phép các công cụ lập trình cốt lõi hoạt động để tránh tự phạt
        self.selected_whitelist.extend(["gemini", "visual studio code", "cursor", "main.py", "focustracker"])
        
        # Khởi tạo phiên học trong Database
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        session_id = database.insert_session(current_date, current_time, target_goal)
        
        # Ẩn giao diện cài đặt tạm thời
        self.withdraw()
        
        # Khởi chạy bộ quét ngầm
        self._run_core_tracker(session_id, self.selected_whitelist, study_minutes)

    def _run_core_tracker(self, session_id, whitelist, duration_minutes):
        print(f"\n🚀 [GUI] Đang thu nhỏ app chạy ngầm. Bắt đầu tính giờ {duration_minutes} phút tập trung...")
        
        tracker = FocusTracker(session_id=session_id, whitelist=whitelist, study_duration_minutes=duration_minutes)
        summary_data = tracker.start_session()
        
        # Khi tracker chạy xong (hết giờ cam kết), luồng sẽ quay lại đây
        self._finish_session(session_id, summary_data)

    def _finish_session(self, session_id, summary_data):
        """Hiện thông báo chúc mừng và chuyển giao tiếp sang module Báo cáo phân tích"""
        # Hiện lại cửa sổ GUI chính
        self.deiconify()
        
        # Xóa sạch các widget cũ để biến thành màn hình chúc mừng
        for widget in self.winfo_children():
            widget.destroy()
            
        self.geometry("500x350")
        
        # Giao diện thông báo chúc mừng
        lbl_congratulations = ctk.CTkLabel(self, text="🎉 CHÚC MỪNG BẠN! 🎉", font=ctk.CTkFont(size=22, weight="bold"), text_color="#22c55e")
        lbl_congratulations.pack(pady=20)
        
        lbl_msg = ctk.CTkLabel(self, text="Bạn đã hoàn thành khoảng thời gian học tập xuất sắc.\nHệ thống đang chắt lọc dữ liệu và gửi báo cáo cho Mẹ...", font=ctk.CTkFont(size=14))
        lbl_msg.pack(pady=10)
        
        # In nhanh kết quả thô lên màn hình
        lbl_score = ctk.CTkLabel(self, text=f"Điểm hiệu suất tập trung: {summary_data['flow_score']}%", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_score.pack(pady=15)
        
        btn_close = ctk.CTkButton(self, text="Đóng ứng dụng", width=150, command=self.quit)
        btn_close.pack(pady=20)
        
        # KÍCH HOẠT SPRINT TIẾP THEO: Gọi module báo cáo (Vẽ đồ thị + Gemini + Telegram)
        print(f"📊 [GUI] Đang kích hoạt module Report cho Session #{session_id}...")
        try:
            import report
            report.generate_and_send_report(session_id)
        except Exception as e:
            print(f"❌ Lỗi khi khởi chạy module báo cáo cuối ngày: {e}")

def main():
    multiprocessing.freeze_support()
    database.init_db()  # Khởi tạo database
    
    app = LauncherGUI()
    app.mainloop()

if __name__ == "__main__":
    main()