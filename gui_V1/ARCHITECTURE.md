# 🏗️ GUI Application Architecture

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    FLET GUI APPLICATION                        │
│                   (Desktop Client Layer)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              main.py - Application Shell                │  │
│  │  ├─ Window Configuration                                │  │
│  │  ├─ Theme Setup (#2E7D32 Green)                         │  │
│  │  ├─ Navigation Rail (7 destinations)                    │  │
│  │  ├─ Header Component                                    │  │
│  │  └─ Content Area (Dynamic Page Switching)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               PAGES (7 UserControl Components)           │  │
│  │                                                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │  │
│  │  │ HomePage   │  │ AAVsPage   │  │MetricsPage │          │  │
│  │  │            │  │            │  │            │          │  │
│  │  │ • Stats    │  │ • Search   │  │ • Success  │          │  │
│  │  │ • Nav      │  │ • Filter   │  │ • Coverage │          │  │
│  │  │ • Cards    │  │ • Details  │  │ • Progress │          │  │
│  │  └────────────┘  └────────────┘  └────────────┘          │  │
│  │                                                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │  │
│  │  │AlertsPage  │  │Comparison  │  │ReportsPage │          │  │
│  │  │            │  │            │  │            │          │  │
│  │  │ • Filter   │  │ • Select   │  │ • Generate │          │  │
│  │  │ • Severity │  │ • Compare  │  │ • Download │          │  │
│  │  │ • Actions  │  │ • Diff     │  │ • Preview  │          │  │
│  │  └────────────┘  └────────────┘  └────────────┘          │  │
│  │                                                           │  │
│  │  ┌────────────────────────────────────────────┐          │  │
│  │  │        SettingsPage                        │          │  │
│  │  │  ├─ API Configuration                      │          │  │
│  │  │  ├─ Application Settings                   │          │  │
│  │  │  ├─ Display Settings                       │          │  │
│  │  │  └─ About & Links                          │          │  │
│  │  └────────────────────────────────────────────┘          │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ▼                                      │
│                   HTTP Requests/JSON                            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                             │
│                 (API Server Layer)                             │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  /aavs/      │  │  /metrics/   │  │  /alerts/    │         │
│  │  (AAV CRUD)  │  │  (Quality)   │  │  (Monitor)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                          ▼                                      │
│         ┌──────────────────────────────┐                       │
│         │    SQLAlchemy ORM Layer      │                       │
│         │  (Database Abstraction)      │                       │
│         └──────────────────────────────┘                       │
│                          ▼                                      │
└────────────────────────────────────────────────────────────────┘
                          ▼
┌────────────────────────────────────────────────────────────────┐
│                  SQLITE3 DATABASE                              │
│              (Data Persistence Layer)                          │
├────────────────────────────────────────────────────────────────┤
│  • aav (20 records)                                            │
│  • metrique_qualite_aav (7 records)                            │
│  • alerte_qualite                                              │
│  • apprenant                                                   │
│  • tentative                                                   │
│  • activite_pedagogique                                        │
│  • rapport_periodique                                          │
│  ... and more                                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Application Startup
```
main.py
  ├─ Initialize Flet Page
  ├─ Load Theme (Green #2E7D32)
  ├─ Create all 7 Pages
  ├─ Create Navigation Rail
  └─ Display Home Page (default)
      └─ HomePage loads data
          └─ GET /aavs/ → Count AAVs
          └─ GET /metrics/aav/ → Calculate average
          └─ GET /alerts/ → Get alert count
          └─ Display stats
```

### 2. User Navigation
```
User clicks navigation item
  ├─ Page identified (e.g., "aavs")
  ├─ Old page removed from view
  ├─ New page content area = pages[name]
  ├─ Page.build() called
  ├─ Components render
  ├─ Data fetched from API
  └─ UI displays results
```

### 3. Search/Filter Action
```
User types in search field
  ├─ TextField value changes
  ├─ on_change handler triggered
  ├─ Query sent to API
  └─ Results filtered locally
      └─ UI updated
```

### 4. Report Generation
```
User clicks "Generate"
  ├─ Form values collected
  ├─ POST /reports/generate sent
  ├─ Backend processes report
  ├─ JSON response received
  ├─ Report added to list
  └─ UI updated with new report
```

---

## Component Hierarchy

```
QualityMetricsApp (Main Container)
│
├─ Header (Toolbar)
│  ├─ Title Text
│  ├─ Status Indicator
│  └─ Timestamp
│
├─ NavigationRail
│  ├─ Destination[0] → home
│  ├─ Destination[1] → aavs
│  ├─ Destination[2] → metrics
│  ├─ Destination[3] → alerts
│  ├─ Destination[4] → comparison
│  ├─ Destination[5] → reports
│  └─ Destination[6] → settings
│
└─ ContentArea (Column)
    ├─ HomePage
    │  ├─ WelcomeSection
    │  ├─ StatsSection (4 Cards)
    │  ├─ NavigationCardsGrid
    │  └─ Footer
    │
    ├─ AAVsPage
    │  ├─ Header (Search, Add Button)
    │  └─ AAVsList (Column)
    │
    ├─ MetricsPage
    │  ├─ Header (Search, Calculate, Refresh)
    │  └─ MetricsList (Column)
    │
    ├─ AlertsPage
    │  ├─ Header (Filter, Analyze)
    │  └─ AlertsList (Column)
    │
    ├─ ComparisonPage
    │  ├─ Header (AAV Selection)
    │  └─ ComparisonGrid
    │
    ├─ ReportsPage
    │  ├─ GenerationForm
    │  └─ ReportsList
    │
    └─ SettingsPage
        ├─ APIConfigSection
        ├─ AppSettingsSection
        ├─ DisplaySettingsSection
        └─ AboutSection
```

---

## API Call Sequence

### Get All Metrics
```
MetricsPage.load_metrics()
  ├─ requests.get("http://localhost:8000/metrics/aav/")
  ├─ Response: 200 OK
  ├─ Body: [
  │   {
  │     "id_aav": 1,
  │     "taux_succes_moyen": 75.5,
  │     "score_covering_ressources": 85.0,
  │     "nb_tentatives_total": 145,
  │     "nb_apprenants_distincts": 42,
  │     "ecart_type_scores": 18.5
  │   },
  │   ...
  │ ]
  └─ self.metrics = response.json()
      └─ build_metrics_table() renders
```

### Calculate Metric
```
MetricsPage (Click "🔄 Calculate All")
  ├─ for each AAV:
  │  ├─ POST /metrics/aav/{id}/calculate
  │  ├─ Response: 200 OK + metric object
  │  └─ Add to metrics list
  └─ Refresh UI
```

### Generate Report
```
ReportsPage (Click "➕ Generate")
  ├─ Collect form values
  ├─ POST /reports/generate {
  │   "type_rapport": "Comprehensive",
  │   "format": "PDF",
  │   "period": "30 days"
  │ }
  ├─ Response: 201 Created + Rapport object
  ├─ Add to reports list
  └─ Refresh UI
```

---

## State Management

### Global State
```python
app = QualityMetricsApp()
├─ api_url: "http://localhost:8000"
├─ current_page: str (active page name)
├─ theme_mode: ft.ThemeMode
├─ pages: Dict[str, UserControl]
│   ├─ 'home': HomePage instance
│   ├─ 'aavs': AAVsPage instance
│   ├─ 'metrics': MetricsPage instance
│   ├─ 'alerts': AlertsPage instance
│   ├─ 'comparison': ComparisonPage instance
│   ├─ 'reports': ReportsPage instance
│   └─ 'settings': SettingsPage instance
└─ page: ft.Page (Flet page reference)
```

### Per-Page State
```python
HomePage
├─ stats: Dict
│  ├─ total_aavs: int
│  ├─ total_metrics: int
│  ├─ active_alerts: int
│  └─ avg_success_rate: float

MetricsPage
├─ metrics: List[Dict]
└─ filtered_metrics: List[Dict]

AlertsPage
├─ alerts: List[Dict]
└─ filtered_alerts: List[Dict]

ReportsPage
├─ reports: List[Dict]
└─ selected_report: Optional[Dict]
```

---

## Error Handling Flow

```
API Call
  ├─ Try:
  │  ├─ Send HTTP request
  │  ├─ Check status code
  │  ├─ Parse JSON response
  │  └─ Update UI
  └─ Except:
      ├─ Catch ConnectionError
      │  └─ Display "Connection refused"
      ├─ Catch ValueError (JSON parse)
      │  └─ Display "Invalid response"
      ├─ Catch Exception
      │  └─ Display generic error
      └─ Log error to console
```

---

## Performance Optimization

### Lazy Loading
- Pages load data only when accessed
- No background requests
- Data cached in memory per session

### Efficient Rendering
- Only visible components render
- Virtual scrolling for long lists
- Column/Row responsive layout

### Network Efficiency
- Batch operations (calculate all)
- Minimal payloads
- JSON response format

---

## Security Considerations

### Input Validation
```python
# Text fields sanitized
search_value = field.value.strip()

# Dropdown values pre-defined
options = ["PDF", "CSV", "JSON"]

# API key masked
password_field.password = True
```

### Data Protection
```python
# No sensitive data in logs
# API calls validated
# Connection checked before operations
# Error messages user-friendly
```

---

## Deployment Architecture

### Local Development
```
Machine
├─ Terminal 1: uvicorn (API)
└─ Terminal 2: flet run (GUI)
```

### Production Windows
```
flet build windows gui/main.py
→ Creates executable (.exe)
→ Can be distributed standalone
```

### Production macOS
```
flet build macos gui/main.py
→ Creates .app bundle
→ Can be signed and notarized
```

### Production Linux
```
flet build linux gui/main.py
→ Creates AppImage
→ Portable across Linux distros
```

---

## Technology Integration

```
Flet Framework
├─ UI Components (Buttons, Cards, etc.)
├─ Layout System (Column, Row, Grid)
├─ Event Handling (on_click, on_change)
├─ Theme System (Colors, Typography)
└─ Responsive Design

Python
├─ Type hints (Optional, List, Dict)
├─ Exception handling (try/except)
├─ Built-in libraries (datetime)
└─ String formatting (f-strings)

Requests Library
├─ GET requests (fetch data)
├─ POST requests (create resources)
├─ Response parsing (JSON)
└─ Error handling (HTTPError)

FastAPI Backend
├─ REST endpoints
├─ JSON serialization
├─ CORS support
└─ Status codes (200, 201, 404)

SQLite Database
├─ Data persistence
├─ ACID compliance
├─ Full-text search
└─ Relationship support
```

---

## Scalability Considerations

### Current Limitations
- Single-threaded UI
- ~1000 records max efficient
- No caching mechanism
- Real-time only (no history)

### Future Optimizations
- Background data fetching
- Local SQLite cache
- Pagination support
- WebSocket real-time updates
- Multi-threading for API calls

---

**Architecture Version**: 1.0.0  
**Last Updated**: April 12, 2026
