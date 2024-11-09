import requests
import tkinter as tk
from PIL import Image, ImageTk
import os
import ctypes
from io import BytesIO
import customtkinter as ctk
import darkdetect
import threading

class WallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SplashPaper")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        self.root.overrideredirect(True)
        
        # Initialize variables
        self.wallpapers = []
        self.current_index = 0
        self.is_maximized = False
        self.last_normal_geometry = None
        
        # Set up theme and UI
        self.is_dark = darkdetect.isDark()
        self.setup_theme()
        self.create_widgets()

        # Bind resize events
        self.container.bind("<Configure>", self.on_resize)
        
        # Draggable functionality
        self.x = 0
        self.y = 0
        self.top_bar.bind("<Button-1>", self.get_pos)
        self.top_bar.bind("<B1-Motion>", self.drag_window)

    def setup_theme(self):
        self.colors = {
            "dark": {
                "bg": "#1A1A1A",
                "card": "#242424",
                "button": "#333333",
                "button_hover": "#404040",
                "accent": "#4A4A4A",
                "text": "#FFFFFF",
                "text_secondary": "#AAAAAA",
                "surface": "#2A2A2A",
                "border": "#333333"
            },
            "light": {
                "bg": "#FFFFFF",
                "card": "#F5F5F5",
                "button": "#E0E0E0",
                "button_hover": "#CCCCCC",
                "accent": "#DDDDDD",
                "text": "#000000",
                "text_secondary": "#666666",
                "surface": "#FAFAFA",
                "border": "#CCCCCC"
            }
        }
        
        theme = "dark" if self.is_dark else "light"
        ctk.set_appearance_mode(theme)
        self.current_theme = self.colors[theme]
        
        self.fonts = {
            "button": ("Segoe UI", 13),
            "title": ("Segoe UI", 12),
            "text": ("Segoe UI", 12),
            "window_controls": ("Segoe UI", 10)
        }

    def create_widgets(self):
        # Main container
        self.container = ctk.CTkFrame(
            self.root,
            fg_color=self.current_theme["bg"],
            corner_radius=0
        )
        self.container.pack(fill="both", expand=True)
        
        # Top bar
        self.top_bar = ctk.CTkFrame(
            self.container,
            fg_color=self.current_theme["surface"],
            height=32,
            corner_radius=0
        )
        self.top_bar.pack(fill="x", padx=0, pady=0)
        
        # App title
        self.title = ctk.CTkLabel(
            self.top_bar,
            text="SplashPaper",
            font=self.fonts["title"],
            text_color=self.current_theme["text"]
        )
        self.title.pack(side="left", padx=10)
        
        # Window controls
        self.setup_window_controls()
        
        # Main content area
        self.content = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Preview frame and label
        self.setup_preview_area()
        
        # Controls bar
        self.setup_controls()

    def setup_window_controls(self):
        self.window_controls = ctk.CTkFrame(
            self.top_bar,
            fg_color="transparent",
            height=32
        )
        self.window_controls.pack(side="right", padx=0)
        
        button_width = 46
        button_height = 32
        
        
        # Maximize/Restore button
        self.max_button = ctk.CTkButton(
            self.window_controls,
            text="🗖",
            width=button_width,
            height=button_height,
            command=self.toggle_maximize,
            fg_color="transparent",
            text_color=self.current_theme["text"],
            hover_color=self.current_theme["button_hover"],
            font=self.fonts["window_controls"],
            corner_radius=0
        )
        self.max_button.pack(side="left", padx=0)
        
        # Close button
        self.close_button = ctk.CTkButton(
            self.window_controls,
            text="🗙",
            width=button_width,
            height=button_height,
            command=self.quit_app,
            fg_color="transparent",
            text_color=self.current_theme["text"],
            hover_color="#FF0000",
            font=self.fonts["window_controls"],
            corner_radius=0
        )
        self.close_button.pack(side="left", padx=0)

    def setup_preview_area(self):
        self.preview_frame = ctk.CTkFrame(
            self.content,
            fg_color=self.current_theme["card"],
            corner_radius=0,
            border_width=1,
            border_color=self.current_theme["border"]
        )
        self.preview_frame.pack_propagate(False)
        self.preview_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Loading wallpapers...",
            text_color=self.current_theme["text"],
            anchor="center"
        )
        self.preview_label.pack(fill="both", expand=True)

    def setup_controls(self):
        self.controls = ctk.CTkFrame(
            self.content,
            fg_color=self.current_theme["surface"],
            corner_radius=0,
            height=50,
            border_width=1,
            border_color=self.current_theme["border"]
        )
        self.controls.pack(fill="x")
        
        button_style = {
            "fg_color": self.current_theme["button"],
            "text_color": self.current_theme["text"],
            "hover_color": self.current_theme["button_hover"],
            "font": self.fonts["button"],
            "corner_radius": 0,
            "height": 32,
            "border_width": 1,
            "border_color": self.current_theme["border"]
        }
        
        self.prev_btn = ctk.CTkButton(
            self.controls,
            text="Previous",
            command=self.show_previous,
            width=100,
            **button_style
        )
        self.prev_btn.pack(side="left", padx=(10, 5), pady=10)
        
        self.next_btn = ctk.CTkButton(
            self.controls,
            text="Next",
            command=self.show_next,
            width=100,
            **button_style
        )
        self.next_btn.pack(side="left", padx=5, pady=10)
        
        self.apply_btn = ctk.CTkButton(
            self.controls,
            text="Set as Wallpaper",
            command=self.set_wallpaper,
            width=140,
            **button_style
        )
        self.apply_btn.pack(side="left", padx=5, pady=10)

    def on_resize(self, event):
        if hasattr(self, 'preview_label'):
            self.show_current_wallpaper()

    def toggle_maximize(self):
        if not self.is_maximized:
            self.last_normal_geometry = self.root.geometry()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.max_button.configure(text="❐")
            self.is_maximized = True
        else:
            if self.last_normal_geometry:
                self.root.geometry(self.last_normal_geometry)
            self.max_button.configure(text="🗖")
            self.is_maximized = False
        self.on_resize(None)

    def minimize_window(self):
        self.root.iconify()

    def quit_app(self):
        self.root.quit()

    def get_pos(self, event):
        if not self.is_maximized:
            self.x = event.x
            self.y = event.y

    def drag_window(self, event):
        if not self.is_maximized:
            deltax = event.x - self.x
            deltay = event.y - self.y
            new_x = self.root.winfo_x() + deltax
            new_y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{new_x}+{new_y}")

    def show_current_wallpaper(self):
        if self.wallpapers:
            try:
                wallpaper = self.wallpapers[self.current_index]
                response = requests.get(wallpaper["urls"]["regular"])
                image_data = Image.open(BytesIO(response.content))
                
                display_width = self.preview_frame.winfo_width()
                display_height = self.preview_frame.winfo_height()
                if display_width > 0 and display_height > 0:
                    image_data.thumbnail((display_width, display_height))
                    
                photo = ImageTk.PhotoImage(image_data)
                self.preview_label.configure(image=photo, text="")
                self.preview_label.image = photo
            except Exception as e:
                self.preview_label.configure(text=f"Error loading image: {str(e)}")

    def show_previous(self):
        if self.wallpapers:
            self.current_index = (self.current_index - 1) % len(self.wallpapers)
            self.show_current_wallpaper()

    def show_next(self):
        if self.wallpapers:
            self.current_index = (self.current_index + 1) % len(self.wallpapers)
            self.show_current_wallpaper()

    def set_wallpaper(self):
        if self.wallpapers:
            wallpaper = self.wallpapers[self.current_index]
            response = requests.get(wallpaper["urls"]["full"])
            image_data = Image.open(BytesIO(response.content))
            temp_path = os.path.join(os.getenv("TEMP"), "temp_wallpaper.bmp")
            image_data.save(temp_path, "BMP")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_path, 0)

    def fetch_wallpapers(self):
        url = "https://api.unsplash.com/photos/random?count=10&client_id=GZZW66KTiEtmpJfNUVpWv935X16aERpE1XTTdADfl6o"
        response = requests.get(url)
        if response.status_code == 200:
            self.wallpapers = response.json()
            self.current_index = 0
            self.show_current_wallpaper()
        else:
            self.preview_label.configure(text="Error fetching wallpapers.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperApp(root)
    threading.Thread(target=app.fetch_wallpapers).start()
    root.mainloop()
