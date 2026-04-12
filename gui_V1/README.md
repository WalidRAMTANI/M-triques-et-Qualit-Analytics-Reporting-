# 📊 Quality Metrics GUI Application

A modern, responsive Flet-based desktop application for monitoring and analyzing AAV (Learning Outcomes) quality metrics.

## 🎨 Design Features

### Visual Design
- **Modern Material Design** with clean UI components
- **Color-coded metrics** for quick status recognition
- **Responsive layouts** that work on different screen sizes
- **Professional color scheme**:
  - Primary: Green (#2E7D32) - Success/Main actions
  - Secondary: Blue (#1976D2) - Information
  - Accent: Orange (#F57C00) - Alerts
  - Error: Red (#D32F2F) - Critical issues

### Pages (7 Total)

#### 1. 🏠 **Home Dashboard**
- Quick statistics overview (4 key metrics)
- Welcome banner
- Navigation cards to all major features
- Real-time API status indicator
- Footer with last update timestamp

#### 2. 🎓 **AAVs Explorer**
- Browse all learning outcomes
- Search and filter capabilities
- Display AAV details (name, description, discipline, teaching method)
- Quick action buttons (View Metrics, History, Edit)
- Responsive list view

#### 3. 📈 **Metrics Viewer**
- Visual quality metrics display
- Success rate indicators with color coding
- Metric cards showing:
  - Coverage percentage
  - Total attempts
  - Active learners
  - Score deviation
- Progress bars for visual representation
- Search and refresh capabilities

#### 4. 🚨 **Alerts Monitor**
- Real-time alert display
- Color-coded by alert type:
  - 📉 Difficult (Red) - Low success rate
  - ⚠️ Fragile (Orange) - Regression detected
  - ❌ Unused (Gray) - No recent activity
  - 🚫 Blocking (Dark Red) - Critical prerequisite issue
- Chip-based alert categorization
- Dismiss and view details actions

#### 5. 🔄 **Comparison Tool**
- Compare metrics between two AAVs
- Side-by-side metric display
- Difference indicators (▲ higher, ▼ lower, = equal)
- 5 key comparison metrics
- Color-coded differences for quick insight

#### 6. 📄 **Reports Page**
- Report generation interface with options:
  - Report type (Comprehensive, Quality Summary, Alerts, Learner Progress)
  - Export formats (PDF, CSV, JSON)
  - Time periods (7 days, 30 days, 90 days, All time)
- Generated reports list
- Download, preview, share, and delete actions
- Report metadata (size, creation date)

#### 7. ⚙️ **Settings**
- **API Configuration**: URL, API key, connection testing
- **Application Settings**: Auto-refresh, notifications, startup alerts
- **Display Settings**: Theme (Light/Dark), font size, tooltips
- **About**: Version info, links to docs and GitHub

## 📦 Installation

### Prerequisites
- Python 3.9+
- Flet framework
- Requests library

### Setup

1. **Install Flet and dependencies:**
```bash
pip install flet requests
```

2. **Or use the requirements file:**
```bash
pip install -r gui_requirements.txt
```

### Running the Application

```bash
# Make sure the API server is running first
python3 -m uvicorn app.main:app --reload

# In another terminal, run the GUI
python3 gui/main.py

# Or use flet directly
flet run gui/main.py
```

## 🎯 Architecture

```
gui/
├── main.py                 # Main application entry point
├── pages/
│   ├── __init__.py        # Package init
│   ├── home.py            # Home/Dashboard page
│   ├── aavs.py            # AAVs browser page
│   ├── metrics.py         # Metrics viewer page
│   ├── alerts.py          # Alerts monitor page
│   ├── comparison.py      # Comparison tool page
│   ├── reports.py         # Reports page
│   └── settings.py        # Settings page
└── README.md              # This file
```

## 🔌 API Integration

The application connects to the FastAPI backend at `http://localhost:8000` by default.

### API Endpoints Used

- `GET /aavs/` - List all AAVs
- `GET /metrics/aav/` - Get all metrics
- `POST /metrics/aav/{id}/calculate` - Calculate metric
- `GET /metrics/aav/{id}` - Get specific metric
- `GET /alerts/` - Get active alerts
- `GET /reports/global` - Get report data

## 🎨 UI Components

- **Navigation Rail**: Left sidebar with 7 navigation destinations
- **Header**: Top bar with title and connection status
- **Cards**: Reusable container components for data display
- **Chips**: Tag-like components for categorization
- **Progress Bars**: Visual metric indicators
- **Buttons**: Elevated, text, and icon buttons for actions
- **Fields**: Text inputs, dropdowns, switches
- **Dividers**: Visual separators

## 🚀 Features

✅ Real-time data fetching from API
✅ Responsive design (1000x700 minimum window size)
✅ Color-coded status indicators
✅ Search and filter capabilities
✅ Export options (PDF, CSV, JSON)
✅ Theme customization (Light/Dark)
✅ Connection status monitoring
✅ Tooltip support
✅ Notification system
✅ Auto-refresh mechanism

## 📊 Display Examples

### Home Dashboard
```
┌─────────────────────────────────────┐
│ 📊 Quality Metrics Dashboard        │
│ Monitor your AAV quality metrics    │
├─────────────────────────────────────┤
│ Quick Statistics                     │
│ ┌──────────┐ ┌──────────┐           │
│ │ AAVs: 20 │ │Metrics: 7│           │
│ └──────────┘ └──────────┘           │
├─────────────────────────────────────┤
│ Quick Navigation                     │
│ [Browse AAVs] [View Metrics]        │
│ [Monitor Alerts] [Compare AAVs]     │
│ [Reports] [Settings]                │
└─────────────────────────────────────┘
```

### Metrics Page
```
Metric #1
├─ Success Rate: 75.5% ▲
├─ Coverage: 85.0%
├─ Attempts: 145
├─ Learners: 42
├─ Deviation: 18.5
└─ Progress: [████████░░] 75%
```

## 🔐 Security

- API key support for authentication
- Connection validation before operations
- Local data caching to reduce API calls
- Error handling with user-friendly messages

## 📝 Customization

### Colors
Edit the theme in `main.py`:
```python
page.theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary="#2E7D32",    # Main color
        secondary="#1976D2",  # Secondary color
        error="#D32F2F"       # Error color
    )
)
```

### API URL
Update in each page's `__init__`:
```python
self.api_url = "http://your-api-url:8000"
```

## 🐛 Troubleshooting

### "Connection refused" error
- Ensure API server is running on port 8000
- Check API URL in settings
- Click "Test Connection" button

### No data displayed
- Verify API has data (check `/aavs/` endpoint)
- Click refresh buttons on each page
- Check browser at `http://localhost:8000/docs`

### Theme not applying
- Restart the application
- Check color scheme values are valid hex codes

## 📚 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flet | 0.23+ | GUI framework |
| requests | 2.28+ | HTTP client for API calls |
| python | 3.9+ | Runtime |

## 🎓 Learning Resources

- [Flet Documentation](https://flet.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Material Design Guidelines](https://material.io/design)

## 📄 License

MIT License - See main repository

## 👥 Contributors

Built as part of Group 7 Quality Metrics Analytics Platform

---

**Version**: 1.0.0  
**Last Updated**: April 2026
