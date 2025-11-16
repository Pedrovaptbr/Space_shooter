# setup.py
import cx_Freeze
import sys

# --- Opções de Build ---
base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "packages": ["pygame", "threading"],
    "include_files": ["starter/"],
    "excludes": ["tkinter", "unittest"],
}

# --- Configuração do Executável ---
executables = [
    cx_Freeze.Executable(
        "menu_principal.py",
        base=base,
        target_name="SpaceShooter.exe",
        icon="starter/sounds/ico.ico"
    )
]

# --- Setup Final ---
cx_Freeze.setup(
    name="Space Shooter",
    version="3.0",
    description="Jogo de nave multiplayer",
    options={"build_exe": build_exe_options},
    executables=executables
)