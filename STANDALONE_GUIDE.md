# 📦 Standalone Executable Guide

## 🚀 Quick Build Process

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Build Executable
```bash
# Option A: Use the automated script
build.bat

# Option B: Use Python script directly
python build_exe.py

# Option C: Manual PyInstaller command
pyinstaller --clean --noconfirm JewelryManagement.spec
```

### Step 3: Test the Executable
```bash
dist\JewelryManagement.exe
```

## 🌐 Online vs Offline Modes

### Online Mode (Default)
- Requires internet connection
- Uses Supabase cloud database
- Real-time data synchronization
- Requires `.env` file with Supabase credentials

### Offline Mode
- Works without internet
- Uses local SQLite database
- All data stored locally
- No external dependencies

### Switching Modes

#### Force Offline Mode
Create a `.env` file with:
```
OFFLINE_MODE=true
```

#### Auto-Detection
The app automatically switches to offline mode if:
- No internet connection
- Supabase credentials missing
- Supabase connection fails

## 📋 Distribution Options

### Option 1: Simple Distribution
1. Copy the entire `dist/` folder
2. Include `.env` file (for online mode)
3. Run `JewelryManagement.exe`

### Option 2: Professional Installation
1. Build the executable
2. Run `dist\install.bat` as Administrator
3. Creates desktop and start menu shortcuts
4. Installs to `C:\Program Files\JewelryManagement\`

### Option 3: Portable Version
1. Copy `dist/` folder to USB drive
2. Rename to "Jewelry Management Portable"
3. Add `OFFLINE_MODE=true` to `.env`
4. Works on any Windows computer

## 🔧 Configuration Files

### .env File (Online Mode)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OFFLINE_MODE=false
```

### .env File (Offline Mode)
```env
OFFLINE_MODE=true
```

### settings.json (Always Required)
```json
{
    "company": {
        "name": "Your Jewelry Store",
        "address": "Your Address",
        "phone": "Your Phone",
        "email": "your@email.com",
        "gstin": "Your GSTIN"
    },
    "tax": {
        "cgst_rate": 1.5,
        "sgst_rate": 1.5
    },
    "invoice": {
        "prefix": "INV",
        "start_number": 1001
    }
}
```

## 📂 File Structure for Distribution

```
JewelryManagement/
├── JewelryManagement.exe          # Main application
├── .env                           # Database configuration
├── settings.json                  # Application settings
├── jewelry_management.db          # SQLite database (offline mode)
├── install.bat                    # Installation script
└── README.txt                     # User instructions
```

## 🎯 Deployment Scenarios

### Scenario 1: Single Store (Offline)
- Install on one computer
- All data stored locally
- No internet required
- Backup database file regularly

### Scenario 2: Multiple Stores (Online)
- Each store has the application
- Shared Supabase database
- Real-time inventory sync
- Centralized reporting

### Scenario 3: Hybrid Mode
- Primary store online (Supabase)
- Branch stores offline (SQLite)
- Periodic data synchronization
- Manual data export/import

## 🛠️ Troubleshooting

### Common Issues

1. **App won't start**
   - Check Windows Defender/Antivirus
   - Run as Administrator
   - Install Visual C++ Redistributable

2. **Database connection failed**
   - Check internet connection
   - Verify `.env` file contents
   - App will auto-switch to offline mode

3. **Missing DLL errors**
   - Install latest Windows updates
   - Install Visual C++ Redistributable 2015-2022

4. **Performance issues**
   - Use directory mode instead of single file
   - Exclude antivirus from scanning app folder
   - Run on SSD for better performance

### Debug Mode
Run with console output for debugging:
```bash
JewelryManagement.exe --debug
```

## 📊 System Requirements

### Minimum Requirements
- Windows 10 (64-bit)
- 4 GB RAM
- 500 MB free disk space
- Internet connection (for online mode)

### Recommended Requirements
- Windows 11 (64-bit)
- 8 GB RAM
- 2 GB free disk space
- Stable internet connection
- SSD storage

## 🔐 Security Considerations

### For Online Mode
- Keep Supabase keys secure
- Use environment variables
- Enable RLS (Row Level Security) in Supabase
- Regular backup of cloud data

### For Offline Mode
- Encrypt SQLite database
- Regular local backups
- Secure physical access to computer
- User access controls

## 📈 Maintenance

### Updates
1. Build new executable
2. Replace old `JewelryManagement.exe`
3. Preserve user data and settings
4. Test thoroughly before deployment

### Backups
- **Online Mode**: Automatic Supabase backups
- **Offline Mode**: Copy `jewelry_management.db` file
- **Settings**: Backup `settings.json` file

### Monitoring
- Check application logs
- Monitor database size
- Verify backup integrity
- User feedback collection

## 🎓 User Training

### Basic Operations
1. Starting the application
2. Adding inventory items
3. Creating invoices
4. Generating reports
5. Backup procedures

### Advanced Features
1. Multi-category management
2. Supplier management
3. Analytics and reporting
4. Data export/import
5. System configuration

## 📞 Support and Documentation

### User Manual
Create a comprehensive user manual covering:
- Installation process
- Daily operations
- Troubleshooting guide
- Feature documentation
- FAQ section

### Technical Support
- Error logging system
- Remote diagnostic tools
- Update notification system
- Help documentation

---

## 📝 Quick Deployment Checklist

- [ ] Install Python dependencies
- [ ] Configure Supabase (online) or SQLite (offline)
- [ ] Test application locally
- [ ] Build executable with PyInstaller
- [ ] Test executable on clean system
- [ ] Create installation package
- [ ] Prepare user documentation
- [ ] Train end users
- [ ] Set up backup procedures
- [ ] Plan update strategy

Your Jewelry Management System is now ready for standalone deployment! 🎉