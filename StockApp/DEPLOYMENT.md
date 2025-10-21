# Jewelry Shop Stock Management System - Deployment Guide

## 🚀 Running the Application

### **Method 1: Local Development (Recommended)**

1. **Install Python 3.7+** if not already installed
2. **Install dependencies:**
   ```bash
   pip install streamlit pandas plotly
   ```
3. **Run the application:**
   ```bash
   streamlit run app.py
   ```
4. **Access the application:** Open `http://localhost:8501` in your browser

### **Method 2: Standalone Executable (Offline Distribution)**

For creating a standalone executable that can run offline:

1. **Install PyInstaller:**

   ```bash
   pip install pyinstaller
   ```

2. **Create a launcher script** (`run_app.py`):

   ```python
   import subprocess
   import sys
   import os

   if __name__ == "__main__":
       # Change to the app directory
       app_dir = os.path.dirname(os.path.abspath(__file__))
       os.chdir(app_dir)

       # Run streamlit
       cmd = [sys.executable, "-m", "streamlit", "run", "app.py",
              "--server.headless", "true", "--server.port", "8501"]
       subprocess.run(cmd)
   ```

3. **Create executable:**

   ```bash
   pyinstaller --onefile --add-data "utils;utils" --add-data "db;db" run_app.py
   ```

4. **Distribute the `dist` folder** with your executable

### **Method 3: Docker Container (Cross-platform)**

1. **Create Dockerfile:**

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
   ```

2. **Build and run:**
   ```bash
   docker build -t jewelry-shop .
   docker run -p 8501:8501 jewelry-shop
   ```

### **Method 4: Portable Installation**

1. **Create a portable folder structure:**

   ```
   JewelryShop/
   ├── python/          # Portable Python installation
   ├── app/             # Your application files
   ├── run.bat          # Windows launcher
   └── run.sh           # Linux/Mac launcher
   ```

2. **Windows launcher (run.bat):**

   ```batch
   @echo off
   cd app
   ..\python\python.exe -m streamlit run app.py
   pause
   ```

3. **Linux/Mac launcher (run.sh):**
   ```bash
   #!/bin/bash
   cd app
   ../python/bin/python -m streamlit run app.py
   ```

## 📱 Making it Mobile-Friendly

The Streamlit interface is already responsive and works well on tablets and mobile devices. For better mobile experience:

1. **Add to home screen** - The web app can be added to device home screens
2. **PWA capabilities** - Can be enhanced to work as a Progressive Web App
3. **Offline mode** - Data is stored locally in SQLite database

## 🌐 Network Access

### **Local Network Access:**

- Run: `streamlit run app.py --server.address 0.0.0.0`
- Access from other devices: `http://[your-ip]:8501`

### **Remote Access (Advanced):**

- Use ngrok for temporary public access
- Deploy to cloud platforms (Heroku, AWS, etc.)
- Set up reverse proxy with nginx

## 💾 Data Backup & Portability

### **Database Location:**

- SQLite database: `db/jewelry_shop.db`
- Portable and can be copied between installations

### **Backup Strategy:**

1. **Manual backup:** Copy the `db` folder
2. **Automated backup:** Use the built-in backup feature in Settings
3. **Export data:** Use CSV export functions

### **Migration:**

1. Copy `db` folder to new installation
2. Ensure same file structure
3. Run application normally

## 🔒 Security Considerations

### **For Offline Use:**

- ✅ Data stays local (SQLite database)
- ✅ No internet connection required
- ✅ Full control over data

### **For Network Use:**

- 🔐 Consider authentication (Streamlit supports basic auth)
- 🔐 Use HTTPS in production
- 🔐 Restrict network access as needed

## 🛠️ Troubleshooting

### **Common Issues:**

1. **Port already in use:**

   ```bash
   streamlit run app.py --server.port 8502
   ```

2. **Python path issues:**

   - Ensure Python is in system PATH
   - Use full path to python executable

3. **Missing dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Database permissions:**
   - Ensure write permissions for `db` folder
   - Check file ownership on Linux/Mac

## 📦 Distribution Package

For easy distribution, create a package with:

```
JewelryShop-v2.0/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── utils/                 # Utility modules
├── db/                    # Database (empty initially)
├── data/                  # Export folder
├── README.md             # User guide
├── DEPLOYMENT.md         # This file
├── run.bat               # Windows launcher
├── run.sh                # Linux/Mac launcher
└── sample_data.py        # Optional sample data
```

## 🚀 Quick Start for Users

1. **Download** the application package
2. **Double-click** `run.bat` (Windows) or `run.sh` (Linux/Mac)
3. **Open browser** to `http://localhost:8501`
4. **Start managing** your jewelry inventory!

## 📞 Support

For technical support:

- Check the troubleshooting section
- Verify all requirements are met
- Ensure proper file permissions
- Check firewall settings for network access
