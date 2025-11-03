"""
Build script for creating standalone executable for Roopkala Jewellers Billing System.
Uses PyInstaller to create a Windows .exe file.
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def clean_build_folders():
    """Clean previous build artifacts."""
    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"Cleaning {folder}...")
            shutil.rmtree(folder)
    
    # Remove old spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removing old spec file: {spec_file}")
        spec_file.unlink()

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building Roopkala Jewellers Billing System executable...")
    
    # Clean previous builds
    clean_build_folders()
    
    # PyInstaller options
    options = [
        'main.py',  # Main entry point
        '--name=RoopkalaBillingSystem',  # Name of the executable
        '--onefile',  # Create a single executable file
        '--windowed',  # No console window (GUI app)
        '--icon=NONE',  # Add icon path if you have one
        
        # Add data files
        '--add-data=settings.json;.',
        '--add-data=.env.template;.',
        
        # Add hidden imports for PyQt5
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        
        # Add hidden imports for reportlab
        '--hidden-import=reportlab',
        '--hidden-import=reportlab.pdfgen',
        '--hidden-import=reportlab.lib',
        '--hidden-import=reportlab.platypus',
        
        # Add hidden imports for supabase
        '--hidden-import=supabase',
        '--hidden-import=dotenv',
        
        # Add hidden imports for PIL/Pillow
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        
        # Collect all submodules
        '--collect-all=PyQt5',
        '--collect-all=reportlab',
        
        # Exclude unnecessary modules to reduce size
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        
        # Exclude other Qt bindings (only use PyQt5)
        '--exclude-module=PyQt6',
        '--exclude-module=PySide2',
        '--exclude-module=PySide6',
        
        # Clean build
        '--clean',
        
        # No confirmation
        '--noconfirm',
    ]
    
    print("\nPyInstaller options:")
    for opt in options:
        print(f"  {opt}")
    
    print("\nStarting build process...\n")
    
    # Run PyInstaller
    PyInstaller.__main__.run(options)
    
    print("\n" + "="*60)
    print("Build complete!")
    print("="*60)
    print(f"\nExecutable location: dist\\RoopkalaBillingSystem.exe")
    print("\nNOTE: The .exe needs the following files in the same directory:")
    print("  - settings.json (configuration file)")
    print("  - .env (if using Supabase)")
    print("\nThe 'invoices' and 'labels' folders will be created automatically.")
    print("\nFor distribution, create a folder with:")
    print("  1. RoopkalaBillingSystem.exe")
    print("  2. settings.json")
    print("  3. .env (if needed)")
    print("  4. README or user manual")
    print("="*60)

if __name__ == "__main__":
    try:
        build_executable()
    except Exception as e:
        print(f"\n❌ Build failed with error: {e}")
        print("\nPlease ensure:")
        print("  1. All dependencies are installed (pip install -r requirements.txt)")
        print("  2. You're running this from the project root directory")
        print("  3. Python and PyInstaller are properly configured")
        raise
