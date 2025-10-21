# Jewelry Shop Stock Management System

A modern, web-based inventory management system specifically designed for jewelry shops, built with Streamlit for an intuitive user experience.

## ✨ Features

### 📊 **Interactive Dashboard**

- Real-time category overview with statistics
- Visual charts showing inventory distribution
- Quick access to all major functions
- Low stock alerts and warnings

### 💍 **Category-Specific Management**

- **Rings**: Size, band material, setting details
- **Necklaces**: Length, clasp type, chain style
- **Earrings**: Type (stud, drop, hoop), backing material
- **Bracelets**: Closure type, adjustable sizing
- **Brooches**: Pin type, vintage classification
- **Pendants**: Bail type, chain compatibility

### 🎯 **Advanced Product Features**

- Melting percentage calculations
- Gross/net weight tracking
- Multiple pricing tiers
- Supplier management
- Purchase/sale history
- Barcode integration
- Photo attachments (planned)

### 📈 **Analytics & Reporting**

- Interactive charts and graphs
- Value analysis by category
- Weight distribution insights
- Sales performance tracking
- Inventory turnover rates
- Export capabilities (CSV, PDF)

### 🔧 **System Features**

- SQLite database (portable, no server required)
- Responsive web interface
- Real-time data validation
- Backup and restore functionality
- Offline capability
- Multi-platform support

## 🚀 Quick Start

### **Prerequisites**

- Python 3.7 or higher
- Web browser (Chrome, Firefox, Safari, Edge)

### **Installation**

1. **Clone or download** this repository
2. **Install dependencies:**
   ```bash
   pip install streamlit pandas plotly
   ```
3. **Run the application:**
   ```bash
   streamlit run app.py
   ```
4. **Open your browser** to `http://localhost:8501`

That's it! 🎉

## 📱 Using the Application

### **Navigation**

- Use the **sidebar** to switch between different pages
- The **Dashboard** provides an overview of your inventory
- Each category has its own **dedicated management page**

### **Adding Products**

1. Navigate to the desired category (e.g., "Rings")
2. Fill out the product form with details
3. Click "Add Product" to save
4. View the product in the table below

### **Managing Inventory**

- **View**: All products displayed in interactive tables
- **Search**: Use the search box to find specific items
- **Edit**: Select products and modify details
- **Delete**: Remove unwanted entries
- **Export**: Download data as CSV

### **Analytics**

- Visit the **Analytics** page for insights
- Interactive charts show inventory distribution
- Filter by date ranges and categories
- Export reports for external use

## 🏗️ Architecture

### **Frontend**

- **Streamlit**: Modern web-based UI framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis

### **Backend**

- **SQLite**: Lightweight, portable database
- **Python**: Core business logic and validation
- **Modular design**: Separated utilities for maintainability

### **File Structure**

```
StockApp/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── db_manager.py      # Database operations
│   ├── validators.py      # Data validation
│   └── logger.py          # Logging system
├── db/                    # Database storage
│   └── jewelry_shop.db    # SQLite database
├── data/                  # Export/import folder
├── README.md              # This file
└── DEPLOYMENT.md          # Deployment guide
```

## 🌐 Deployment Options

### **Local Use (Development)**

Perfect for single-user, local inventory management:

```bash
streamlit run app.py
```

### **Network Access**

Share across your local network:

```bash
streamlit run app.py --server.address 0.0.0.0
```

### **Offline Distribution**

Create standalone executables for offline use:

- See `DEPLOYMENT.md` for detailed instructions
- Package with PyInstaller or Docker
- No internet connection required

### **Cloud Deployment**

Deploy to cloud platforms:

- Heroku, AWS, Google Cloud
- Azure, DigitalOcean, etc.
- Streamlit Cloud (streamlit.io)

## 📊 Sample Data

The application includes sample data to help you get started:

- **10+ sample products** across all categories
- **Realistic jewelry data** with proper weights and pricing
- **Supplier information** for testing workflows
- **Transaction history** for analytics testing

## 🔒 Data Security

### **Local Storage**

- All data stored in local SQLite database
- No cloud dependencies by default
- Complete control over your data

### **Backup Features**

- Manual database backup/restore
- CSV export capabilities
- Portable database files

### **Privacy**

- No telemetry or tracking
- No external API calls (unless configured)
- Self-contained application

## 🛠️ Customization

### **Adding New Categories**

1. Modify the category definitions in `app.py`
2. Update database schema if needed
3. Add category-specific fields

### **Custom Fields**

- Easy to add new product attributes
- Modify forms in the Streamlit interface
- Update database operations accordingly

### **Styling**

- Customize colors and themes
- Modify CSS in Streamlit configuration
- Add company branding

## 📈 Roadmap

### **Planned Features**

- [ ] Photo upload and gallery
- [ ] Barcode scanning integration
- [ ] Advanced reporting dashboard
- [ ] Multi-store support
- [ ] Customer management
- [ ] Sales order processing
- [ ] Automated reorder points
- [ ] Mobile app companion

### **Technical Improvements**

- [ ] Performance optimization
- [ ] Advanced caching
- [ ] Real-time synchronization
- [ ] API endpoints
- [ ] Plugin system
- [ ] Advanced authentication

## 🐛 Troubleshooting

### **Common Issues**

**Application won't start:**

- Check Python version (3.7+)
- Verify all dependencies installed
- Ensure port 8501 is available

**Database errors:**

- Check file permissions in `db/` folder
- Verify SQLite installation
- Try deleting and recreating database

**Performance issues:**

- Clear browser cache
- Restart the application
- Check available memory

**Network access problems:**

- Verify firewall settings
- Check IP address configuration
- Ensure correct port forwarding

### **Getting Help**

1. Check the `DEPLOYMENT.md` file
2. Review error messages in terminal
3. Verify system requirements
4. Check file permissions

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Areas where help is needed:

- **UI/UX improvements**
- **Additional jewelry categories**
- **Export format support**
- **Mobile optimization**
- **Performance enhancements**
- **Documentation improvements**

## 📞 Support

For technical support:

- Review the troubleshooting section
- Check deployment documentation
- Verify system requirements
- Test with sample data

## 🎉 Acknowledgments

Built with modern Python technologies:

- **Streamlit** for the amazing web framework
- **Plotly** for interactive visualizations
- **Pandas** for data manipulation
- **SQLite** for reliable data storage

---

**Transform your jewelry business with modern inventory management!** 💎
