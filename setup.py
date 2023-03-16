import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","subprocess","time","threading","sys","configparser","pystray", "PIL.Image"],
                       "include_files": ["Icons/", "Settings.txt"],
                       "excludes": ["PyQt5", "test"]}
# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="PingTest",
    version="0.1",
    description="My GUI application!",
    options={"build_exe": build_exe_options},
    executables=[Executable("PackageTester.py", base=base)],
)
