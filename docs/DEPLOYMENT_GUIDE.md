# 📦 Deployment Guide - Jewelry Management System

## Creating Standalone Executable

### Quick Start
1. **Run the build script:**
   ```bash
   build.bat
   ```
   OR
   ```bash
   python build_exe.py
   ```

2. **Test the executable:**
   ```bash
   dist\JewelryManagement.exe
   ```

3. **Install on target machine (as Administrator):**
   ```bash
   dist\install.bat
   ```

## 🔧 Manual Build Process

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Basic Build
```bash
pyinstaller --onefile --windowed --name="JewelryManagement" main.py
```

### Step 3: Advanced Build (Recommended)
```bash
pyinstaller --clean --noconfirm JewelryManagement.spec
```

## 🚀 Distribution Options

### Option 1: Single File Executable
- **Pros:** Single .exe file, easy to distribute
- **Cons:** Slower startup, larger file size
- **Command:** `pyinstaller --onefile main.py`

### Option 2: Directory Distribution (Recommended)
- **Pros:** Faster startup, easier debugging
- **Cons:** Multiple files to distribute
- **Command:** `pyinstaller main.py`

### Option 3: Installer Package
- Use tools like **Inno Setup** or **NSIS** for professional installers
- Create MSI packages using **cx_Freeze** with `bdist_msi`

## 📋 Requirements for Target Machines

### For Online Mode (Supabase)
- Windows 10/11 (64-bit recommended)
- Internet connection for Supabase
- `.env` file with Supabase credentials

### For Offline Mode
- SQLite database (modify database_manager.py)
- All data stored locally
- No internet required

## 🔧 Configuration for Offline Use

To make the app work completely offline:

### 1. Switch to SQLite Backend
```python
# In database_manager.py, add SQLite support:
import sqlite3

class LocalDatabaseManager:
    def __init__(self, db_path="jewelry_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        # Create SQLite tables matching Supabase schema
        pass
```

### 2. Bundle SQLite Database
```python
# In PyInstaller spec file, add:
datas=[
    ('jewelry_management.db', '.'),
    # ... other files
],
```

### 3. Create Hybrid Mode
```python
# Auto-detect online/offline mode
def get_database_manager():
    try:
        # Try Supabase connection
        return SupabaseDatabaseManager()
    except:
        # Fallback to SQLite
        return LocalDatabaseManager()
```

## 📦 Build Configurations

### Development Build
```bash
pyinstaller --debug --console main.py
```

### Production Build
```bash
pyinstaller --windowed --optimize 2 --strip main.py
```

### Minimal Size Build
```bash
pyinstaller --onefile --windowed --strip --upx-dir=upx main.py
```

## 🎯 Optimization Tips

### 1. Reduce File Size
- Use `--exclude-module` for unused modules
- Enable UPX compression: `--upx-dir=upx`
- Use `--strip` to remove debug symbols

### 2. Improve Startup Time
- Use directory mode instead of onefile
- Optimize imports in main.py
- Lazy load heavy modules

### 3. Handle Dependencies
```python
# Hidden imports for PyInstaller
# Add to spec file:
hiddenimports=[
    'supabase',
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'reportlab.pdfgen',
    'PIL.Image',
]
```

## 🛠️ Troubleshooting

### Common Issues

1. **Missing DLLs:**
   ```bash
   pyinstaller --collect-all supabase main.py
   ```

2. **PyQt5 Issues:**
   ```bash
   pip install PyQt5-tools
   pyinstaller --hidden-import PyQt5.QtCore main.py
   ```

3. **SSL Certificate Errors:**
   ```bash
   pip install certifi
   # Add to hiddenimports: 'certifi'
   ```

4. **Large File Size:**
   - Exclude unused modules
   - Use virtual environment
   - Enable compression

### Debug Mode
```bash
# Run with console output for debugging
pyinstaller --console --debug main.py
```

## 📂 File Structure After Build

```
dist/
├── JewelryManagement.exe          # Main executable
├── install.bat                    # Installation script
└── _internal/                     # Dependencies (if directory mode)
    ├── PyQt5/
    ├── supabase/
    └── ...

build/                             # Build artifacts
├── JewelryManagement/
└── ...

JewelryManagement.spec             # PyInstaller configuration
```

## 🌐 Network Configuration

### Firewall Settings
- Allow JewelryManagement.exe through Windows Firewall
- Open ports for Supabase (443/HTTPS)

### Proxy Support
```python
# Add proxy support in database_manager.py
import os
os.environ['HTTPS_PROXY'] = 'http://proxy:port'
```

## 📋 Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test application locally: `python main.py`
- [ ] Build executable: `python build_exe.py`
- [ ] Test executable: `dist\JewelryManagement.exe`
- [ ] Create .env file with Supabase credentials
- [ ] Test on clean Windows machine
- [ ] Create installer package (optional)
- [ ] Document installation process
- [ ] Provide user manual

## 📞 Support

For deployment issues:
1. Check build logs in `build/` directory
2. Test with `--debug` and `--console` flags
3. Verify all dependencies are included
4. Test on target operating system

## 🔄 Updates and Maintenance

### Automatic Updates
Consider implementing auto-update functionality:
- Check for updates on startup
- Download and install new versions
- Use tools like `pyupdater` or custom solution

### Version Management
- Embed version info in executable
- Track deployment versions
- Maintain upgrade/downgrade paths