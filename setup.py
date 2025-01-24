import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["pygame", "google.generativeai", "tkinter"],
    "include_files": [
        "block.png",
        "floor.png",
        "player.png",
        "treasure.png",
        "heart.png"
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Лабіринт Знань",
    version="1.0",
    description="Освітня гра для вивчення програмування",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)]
) 