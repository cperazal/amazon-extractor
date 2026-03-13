# Amazon Extractor

A desktop GUI application for scraping Amazon product data with filtering options. Built with PyQt5, Selenium, and BeautifulSoup.

## Features

- 🔍 Search Amazon products by name
- 📊 Filter by price range, star rating, seller (Amazon-only)
- 📄 Export results to CSV
- 🎨 User-friendly GUI with progress tracking
- 🔗 Direct file explorer integration to view results

## System Requirements

### Python Version
- **Python 3.10.x** (official installer from python.org)
- ⚠️ **CRITICAL:** DO NOT use Microsoft Store Python — it causes PyQt5 DLL errors. Download and install from [python.org](https://www.python.org/downloads/)

### Operating System
- Windows 10 or later (64-bit)

### Browsers
- Google Chrome (required for web scraping via Selenium)

## Installation

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd amazon-extractor
```

### 2. Create a Virtual Environment
```powershell
# Use official Python 3.10+ (NOT Microsoft Store Python)
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

**Important:** If you see an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies
```powershell
# Upgrade pip, setuptools, and wheel first
python -m pip install --upgrade pip setuptools wheel

# Install all required packages
python -m pip install -r requirements.txt
```

**Dependencies include:**
- **PyQt5** (5.15.9) — GUI framework
- **PyQt5-sip** (12.11.1) — PyQt5 dependencies
- **Selenium** (≥4.15.0) — Web scraping & browser automation
- **BeautifulSoup4** (≥4.9.0) — HTML/XML parsing
- **Pandas** (≥1.3.0) — Data handling and CSV export
- **webdriver-manager** (≥4.0.0) — Automatic ChromeDriver management

## Running the Application

### From PowerShell
```powershell
# Ensure your virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Run the application
python .\gui_main.py
```

### Expected Output
The GUI window should open without any errors.

## Usage

1. **Enter a Product Name** — Type the product you want to search (e.g., "dell laptop")
2. **Select Pages** — Choose how many pages to scrape (1, 5, 10, 15, 20, or All)
3. **Apply Filters (Optional)**
   - ✓ Only ships from Amazon
   - ✓ Only sold by Amazon
   - Star rating minimum (1-4 stars or all)
   - Price range (min-max)
4. **Click Extract** — The scraper will run and show progress
5. **Open File** — Click "Open file" to view the generated CSV in File Explorer

## Output

Results are saved to: `data_output/data_csv.csv`

CSV includes:
- Product title
- Price
- Rating
- Number of reviews
- Seller information
- Shipping details

## Troubleshooting

### PyQt5 DLL Load Error
If you get: `ImportError: DLL load failed while importing QtCore: The specified procedure could not be found.`

**Solution:**
1. **Use Official Python Only** — Uninstall Microsoft Store Python if you have it
   - Download Python 3.10 from [python.org](https://www.python.org/downloads/)
   - Install with "Add Python to PATH" checked
   
2. **Rebuild Virtual Environment:**
   ```powershell
   # Remove old environment
   Remove-Item -Recurse .venv
   
   # Create fresh environment with official Python
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   
   # Reinstall with force-reinstall
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install -r requirements.txt --force-reinstall
   ```

3. **If still failing:**
   - Try downgrading PyQt5: `pip install PyQt5==5.15.7`
   - Check Windows Visual C++ Runtime is installed

### Selenium ChromeDriver Issues
If the scraper can't find Chrome:
- Ensure Google Chrome is installed
- The `webdriver-manager` package will automatically download the correct ChromeDriver
- No manual setup needed

### Virtual Environment Won't Activate
If `.\.venv\Scripts\Activate.ps1` fails:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

## Troubleshooting

### ImportError: DLL load failed while importing QtCore

**Cause:** Your virtual environment was created with Microsoft Store Python, which doesn't properly export symbols needed by PyQt5.

**Solution:**
```powershell
# 1. Backup the broken venv
Rename-Item -Path .\.venv -NewName .venv_broken

# 2. Create a new venv using OFFICIAL Python (from python.org)
# First, ensure you have official Python 3.9+ installed
C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python39\python.exe -m venv .venv

# 3. Activate and reinstall dependencies
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# 4. Test the import
python -c "from PyQt5 import QtCore; print('OK')"

# 5. Run the application
python .\gui_main.py
```

### ChromeDriver Not Found
- The app uses **webdriver-manager** to auto-download the correct ChromeDriver
- If issues persist, ensure Google Chrome is installed
- Reinstall selenium and webdriver-manager:
  ```powershell
  python -m pip install --upgrade --force-reinstall selenium webdriver-manager
  ```

### No Data Exported / Empty CSV
- Check internet connection
- Amazon may block repeated requests — add delays between searches
- Verify the product name is valid

## Development

### Convert UI File to Python Code
If you modify the UI design in Qt Designer:
```powershell
pyuic5 -x .\qt-designer\gui_extractor.ui -o .\qt-designer\gui_extractor.py
```

### Build Executable

To create a standalone `.exe` file:
```powershell
# Install PyInstaller
python -m pip install pyinstaller

# Build the executable
pyinstaller --name "AmazonExtractor" ^
  --onefile ^
  --noconsole ^
  --icon="icons/app.ico" ^
  --add-data="icons;icons" ^
  --add-data="images;images" ^
  .\gui_main.py
```

The executable will be in the `dist/` folder.

## Project Structure

```
amazon-extractor/
├── gui_main.py              # Main GUI application
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── scraper/
│   └── scrape_amazon.py    # Web scraping logic
├── models/
│   └── productAmazon.py    # Product data model
├── utils/
│   └── logging.py          # Logging utility
├── qt-designer/
│   ├── gui_extractor.ui    # Qt Designer UI file
│   └── gui_extractor.py    # Generated UI code
├── icons/
│   ├── app.ico
│   ├── open.ico
│   ├── extract.ico
│   ├── excel.ico
│   └── help.ico
├── images/
│   └── data_entry_example.png
└── data_output/            # CSV export directory (auto-created)
```

## Notes

- **Web scraping**: Uses Selenium with headless Chrome for reliable data extraction
- **Data processing**: Pandas for clean CSV export with UTF-8 encoding
- **UI**: PyQt5 with custom styling and progress tracking
- **Cross-platform**: Code is platform-agnostic, but currently tested on Windows

## Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Ensure you have Python 3.9+ from python.org (NOT Microsoft Store)
3. Verify all dependencies are installed: `python -m pip list`
4. Check internet connection and that Amazon is accessible

## License

MIT License

Contact: info@carlosperaza.dev

