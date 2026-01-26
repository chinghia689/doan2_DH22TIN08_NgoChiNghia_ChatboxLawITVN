import customtkinter as ctk
import requests
import threading
import re
from datetime import datetime

# ================= HELPER FUNCTIONS =================
def clean_markdown(text):
    """Loại bỏ markdown formatting cho CTkLabel"""
    # Loại bỏ bold/italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)  # ***text***
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)      # **text**
    text = re.sub(r'\*(.*?)\*', r'\1', text)          # *text*
    text = re.sub(r'_(.*?)_', r'\1', text)            # _text_
    # Loại bỏ markdown links nhưng giữ text
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)   # [text](url)
    return text

# ================= CẤU HÌNH GIAO DIỆN (CHATGPT STYLE) =================
API_URL = "http://localhost:8000/chat"

# Màu sắc chuẩn ChatGPT Dark Mode
COLOR_BG = "#343541"          # Nền chính
COLOR_SIDEBAR = "#202123"     # Sidebar
COLOR_USER_BUBBLE = "#444654" # Màu nền tin nhắn User (Hoặc xanh #10a37f)
COLOR_AI_BUBBLE = "#343541"   # Màu nền tin nhắn AI (trùng nền hoặc sáng hơn chút)
COLOR_INPUT_BG = "#40414f"    # Nền ô nhập liệu
TEXT_COLOR = "#ececf1"        # Màu chữ

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

MAIN_FONT_FAMILY = "sans-serif"
class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chatbox Luật công nghệ thông tin")
        self.geometry("600x850") # Kích thước giống điện thoại hơn

        # Cấu hình lưới
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Chat area
        self.grid_rowconfigure(1, weight=0) # Input area

        # 1. KHUNG CHAT (Scrollable)
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLOR_BG,
            corner_radius=0
        )
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Font objects
        self.font_msg = ctk.CTkFont(family=MAIN_FONT_FAMILY, size=14)
        self.font_bold = ctk.CTkFont(family=MAIN_FONT_FAMILY, size=14, weight="bold")

        # 2. KHUNG INPUT (Floating Bar)
        self.input_container = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.input_container.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.input_container.grid_columnconfigure(0, weight=1)

        # Ô nhập liệu hình viên thuốc
        self.entry = ctk.CTkEntry(
            self.input_container,
            placeholder_text="Nhập câu hỏi...",
            height=50,
            corner_radius=25, # Bo tròn như viên thuốc
            fg_color=COLOR_INPUT_BG,
            border_width=0,
            text_color="white",
            font=self.font_msg
        )
        self.entry.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.entry.bind("<Return>", self.send_message)

        # Nút gửi (Icon mũi tên)
        self.btn_send = ctk.CTkButton(
            self.input_container,
            text="➤",
            width=50,
            height=50,
            corner_radius=25,
            fg_color="#10a37f", # Màu xanh ChatGPT
            hover_color="#0d8a6a",
            font=ctk.CTkFont(size=20),
            command=self.send_message
        )
        self.btn_send.grid(row=0, column=1, padx=(0, 15), pady=15)

        # Tin nhắn chào mừng
        self.add_message("AI", "Xin chào! Tôi là Trợ lý Luật sư AI. Tôi có thể giúp gì cho bạn?")

    def add_message(self, role, text):
        is_user = (role == "BẠN")
        
        # Container cho mỗi tin nhắn
        msg_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        msg_frame.pack(fill="x", pady=10, padx=10)

        # Avatar (Label tròn)
        avatar_text = "👤" if is_user else "⚖️"
        avatar_color = "#5436DA" if is_user else "#10a37f"
        
        avatar = ctk.CTkLabel(
            msg_frame, 
            text=avatar_text, 
            width=35, height=35, 
            fg_color=avatar_color,
            corner_radius=17, # Tròn
            font=ctk.CTkFont(size=20)
        )
        
        # Bong bóng chat
        bubble_color = COLOR_USER_BUBBLE if is_user else "transparent"
        
        bubble = ctk.CTkFrame(
            msg_frame,
            fg_color=bubble_color,
            corner_radius=10 if is_user else 0
        )

        # Label nội dung
        cleaned_text = clean_markdown(text)  # Loại bỏ markdown
        content = ctk.CTkLabel(
            bubble,
            text=cleaned_text,
            font=self.font_msg,
            text_color=TEXT_COLOR,
            wraplength=320, # Tự xuống dòng
            justify="left"
        )
        content.pack(padx=10, pady=8, anchor="w")

        # Bố cục: 
        # Nếu là User: Avatar bên phải
        # Nếu là AI: Avatar bên trái
        if is_user:
            avatar.pack(side="right", anchor="n")
            bubble.pack(side="right", padx=(50, 10), anchor="n")
        else:
            avatar.pack(side="left", anchor="n")
            bubble.pack(side="left", padx=(10, 50), anchor="n")

        # Tự cuộn xuống
        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if not msg: return

        self.add_message("BẠN", msg)
        self.entry.delete(0, "end")
        self.entry.configure(state="disabled")

        threading.Thread(target=self.call_api, args=(msg,), daemon=True).start()

    def call_api(self, question):
        try:
            response = requests.post(API_URL, json={"question": question}, timeout=60)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                ans = response.json().get("answer", "Lỗi dữ liệu")
                self.add_message("AI", ans)
            else:
                self.add_message("AI", f"Lỗi Server: {response.status_code}")
        except:
            self.add_message("AI", "Không kết nối được Server.")
        finally:
            self.entry.configure(state="normal")

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()