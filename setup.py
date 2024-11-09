# setup.py
from cx_Freeze import setup, Executable
import sys

# Use "Win32GUI" base to hide the console window on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="SplashPaper",
    version="1.0",
    description="Wallpaper application",
    executables=[Executable("main.py", base=base, icon="Static/icon.png")]
)
