# TAPIK - Test API Keys

<p align="center">
  <img src="https://img.shields.io/badge/version-v0.8.3-blue.svg" alt="Version"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
</p>

```
 _              _ _    
| | @thezakman (_) |   
| |_ __ _ _ __  _| | __
| __/ _` | '_ \| | |/ /
| || (_| | |_) | |   < 
 \__\__,_| .__/|_|_|\_\
         | |           
         |_|  Version: v0.8.3
```

## 📋 Description

TAPIK is a powerful tool for testing and validating API keys from various Google services. It allows you to quickly check if your API keys are functional, expired, or invalid across multiple Google APIs.

## ✨ Features

- Test up to 43 different Google APIs with a single key
- Validate multiple API keys in one execution
- Detailed status reports showing which services work with each key
- Color-coded output for easy readability
- Rate limiting to avoid API throttling
- Export results in multiple formats

## 🌐 Supported APIs

TAPIK can test keys against these API categories:

- **Google Maps & Location**: Geocode, Places, StaticMap, StreetView, Directions and more
- **Google Roads APIs**: Nearest Roads, Snap To Roads, Speed Limits
- **Google Cloud AI & ML**: Natural Language, Vision, Text-to-Speech, Speech-to-Text
- **Google Translation**: Translate API, Cloud Translation API
- **Google Search & Content**: Custom Search, Books, YouTube, PageSpeed
- **Google Cloud Storage**: Cloud Storage, BigQuery, Datastore
- **Google Productivity**: Drive, Sheets, Calendar, Tasks
- **Google Social & User**: People API, Blogger API, Civic API
- **Google Design**: WebFonts API

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/thezakman/tapik.git
cd tapik

# Install dependencies
pip install -r requirements.txt
```

## 💻 Usage

```bash
# Basic syntax
python tapik.py [options] 

# Test a single API key
python tapik.py --key YOUR_API_KEY

# Test multiple API keys from a file
python tapik.py --file keys.txt

# Test specific APIs (by number)
python tapik.py --key YOUR_API_KEY --api 1,5,9

# Test a range of APIs
python tapik.py --key YOUR_API_KEY --api 1-10

# Test with verbose output
python tapik.py --key YOUR_API_KEY --verbose
```

### Available Options

- `--key KEY, -k KEY`: Test a single API key
- `--list FILE, -l FILE`: Test multiple API keys from a file
- `--verbose, -v`: Show detailed information during execution
- `--output FILE, -o FILE`: Save results to specified file
- `--api SELECTION, -a SELECTION`: Select specific APIs to test (e.g., "1,2,3" or "1-5")

## 🚦 API Status Indicators

- ✅ **WORKED**: The API key is valid and has access to this service
- ❌ **Error Messages**:
  - UNAUTHENTICATED: Valid key but not authenticated
  - PERMISSION_DENIED: Valid key but lacks permissions
  - INVALID_ARGUMENT: Request has invalid parameters
  - REQUEST_DENIED: Key is invalid or API is disabled
  - BLOCKED: API key has been blocked
  - BAD REQUEST: Malformed request

## 🛠️ In Development

- [ ] Add more API validations
- [ ] Add provider selector (--provider 1,2,3,4)
- [ ] Optimize code and add comments
- [ ] Add support for new providers
- [ ] Simple graphical interface

## 👨‍💻 Contribution

Contributions are welcome! Feel free to:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

[@thezakman](https://github.com/thezakman)
