"""
Build script for creating standalone executable
Run this script to create a .exe file for the Jewelry Management System
"""

import os
import sys
import subprocess
from pathlib import Path


def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller

        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller"]
            )
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install PyInstaller: {e}")
            return False


def create_spec_file():
    """Create a PyInstaller spec file for custom configuration."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('settings.json', '.'),
        ('database/*.sql', 'database'),
        ('database/*.md', 'database'),
        ('docs/*', 'docs'),
        ('examples/*', 'examples'),
        ('ui/*.py', 'ui'),
        ('logic/*.py', 'logic'),
    ],
    hiddenimports=[
        'supabase',
        'gotrue',
        'postgrest',
        'storage3',
        'realtime',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'dotenv',
        'decimal',
        'uuid',
        'json',
        'csv',
        'datetime',
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JewelryManagement',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""

    with open("JewelryManagement.spec", "w") as f:
        f.write(spec_content)
    print("✅ Spec file created: JewelryManagement.spec")


def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")

    # Create spec file
    create_spec_file()

    # Build using spec file for more control
    cmd = ["pyinstaller", "--clean", "--noconfirm", "JewelryManagement.spec"]

    try:
        subprocess.check_call(cmd)
        print("✅ Executable built successfully!")
        print("📁 Output location: dist/JewelryManagement.exe")
        print("📁 Distribution folder: dist/")

        # Check if the executable was created
        exe_path = Path("dist/JewelryManagement.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📊 Executable size: {size_mb:.1f} MB")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

    return True


def create_installer_script():
    """Create a simple installer script."""
    installer_content = """@echo off
echo ================================================
echo    Jewelry Management System Installer
echo ================================================
echo.

REM Create application directory
if not exist "C:\\Program Files\\JewelryManagement" (
    mkdir "C:\\Program Files\\JewelryManagement"
)

REM Copy executable and files
copy "JewelryManagement.exe" "C:\\Program Files\\JewelryManagement\\"
copy "settings.json" "C:\\Program Files\\JewelryManagement\\" 2>nul

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Jewelry Management.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\JewelryManagement\\JewelryManagement.exe'; $Shortcut.Save()"

REM Create start menu shortcut
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Jewelry Management" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Jewelry Management"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Jewelry Management\\Jewelry Management.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\JewelryManagement\\JewelryManagement.exe'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo.
echo The application has been installed to:
echo C:\\Program Files\\JewelryManagement\\
echo.
echo Desktop shortcut created: Jewelry Management
echo Start menu shortcut created
echo.
pause
"""

    with open("dist/install.bat", "w", encoding="utf-8") as f:
        f.write(installer_content)
    print("✅ Installer script created: dist/install.bat")


def main():
    """Main build process."""
    print("🚀 Jewelry Management System - Executable Builder")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print(
            "❌ Error: main.py not found. Please run this script from the project root directory."
        )
        return

    # Install PyInstaller
    if not install_pyinstaller():
        return

    # Build executable
    if build_executable():
        create_installer_script()
        print("\n🎉 Build process completed!")
        print("\nNext steps:")
        print("1. Test the executable: dist/JewelryManagement.exe")
        print("2. Run installer (as admin): dist/install.bat")
        print("3. Distribute the dist/ folder to other computers")
        print(
            "\n⚠️  Note: Make sure to set up .env file with Supabase credentials on target machines"
        )


if __name__ == "__main__":
    main()
