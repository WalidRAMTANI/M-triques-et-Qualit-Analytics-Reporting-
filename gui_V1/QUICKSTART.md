# 🚀 Quick Start Guide - Flet GUI Application

## Installation & Setup (5 minutes)

### 1. Install Dependencies

```bash
# Navigate to project directory
cd /Users/ramtani/Desktop/projet_python

# Install GUI dependencies
pip install -r gui/gui_requirements.txt

# Or install manually
pip install flet==0.23.1 requests==2.31.0
```

### 2. Start the API Server

```bash
# Terminal 1: Start the FastAPI backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

### 3. Launch the GUI Application

```bash
# Terminal 2: Run the Flet GUI
python3 gui/main.py

# Or using flet directly
flet run gui/main.py
```

**That's it!** The application should open in a new window.

---

## 🎯 First Steps

### Initial Setup
1. **Check Connection** - You should see "✅ Connected" in the header
2. **View Dashboard** - Home page shows statistics automatically
3. **Explore Data** - Click on navigation cards to browse AAVs, metrics, and alerts

### Common Tasks

#### View All AAVs
1. Click "🎓 AAVs" in sidebar
2. Browse the list or search for specific AAVs
3. Click "📊 View Metrics" to see quality metrics

#### Check Quality Metrics
1. Click "📈 Metrics" in sidebar
2. View all calculated metrics or click "🔄 Calculate All" to compute new ones
3. Hover over metric cards to see detailed information

#### Monitor Alerts
1. Click "🚨 Alerts" in sidebar
2. View problematic AAVs by category:
   - 📉 Difficult (low success rate)
   - ⚠️ Fragile (regression detected)
   - ❌ Unused (no recent activity)
   - 🚫 Blocking (critical issues)
3. Click "📊 View Details" to get more info

#### Compare AAVs
1. Click "🔄 Compare" in sidebar
2. Select two AAVs from the dropdowns
3. Click "🔍 Compare"
4. View side-by-side metrics with differences highlighted

#### Generate Reports
1. Click "📄 Reports" in sidebar
2. Select report type, format, and time period
3. Click "➕ Generate"
4. Download or preview generated reports

#### Customize Settings
1. Click "⚙️ Settings" in sidebar
2. Configure API connection, appearance, and behavior
3. Changes apply immediately

---

## 🛠️ Configuration

### Change API URL

**Method 1: GUI Settings**
1. Open Settings page (⚙️ icon)
2. Update "API URL" field in API Configuration section
3. Click "🔍 Test Connection" to verify
4. Connection status shows immediately

**Method 2: Edit Code**
Edit `gui/main.py` line 17:
```python
API_URL = "http://your-api-url:8000"
```

---

## 📊 Understanding the Dashboard

### Statistics Cards
- **Total AAVs**: Number of learning outcomes in system
- **Calculated Metrics**: Metrics that have been computed
- **Active Alerts**: Issues requiring attention
- **Avg Success Rate**: Average learner success percentage

### Navigation Cards
Each card links to a major feature:
- 🎓 Browse AAVs
- 📈 View Metrics
- 🚨 Monitor Alerts
- 🔄 Compare AAVs
- 📄 Generate Reports
- ⚙️ Configure Settings

---

## 🎨 UI Features

### Color Coding
- 🟢 **Green** (#2E7D32): Success, primary actions
- 🔵 **Blue** (#1976D2): Information, secondary actions
- 🟠 **Orange** (#F57C00): Warnings, be careful
- 🔴 **Red** (#D32F2F): Critical issues, errors

### Metric Indicators
- **Progress Bars**: Visual representation of percentages
- **Trend Arrows**: 
  - ▲ Higher/Better
  - ▼ Lower/Worse
  - = No change

### Status Badges
- ✅ Connected: API is reachable
- ❌ Disconnected: Cannot reach API
- ⚠️ Warning: Potential issues detected

---

## 🔧 Troubleshooting

### Issue: "Connection refused"
**Solution:**
1. Verify API server is running on port 8000
2. Check with: `curl http://localhost:8000/aavs/`
3. Go to Settings → API Configuration
4. Click "🔍 Test Connection"
5. If still failing, check API logs

### Issue: No data showing
**Solution:**
1. Check if database has data: `sqlite3 platonAAV.db "SELECT COUNT(*) FROM aav;"`
2. Should show: `20` (if test data loaded)
3. If empty, load test data:
   ```bash
   sqlite3 platonAAV.db < app/donnees_test.sql
   ```
4. Refresh page (click 🔃 icon)

### Issue: GUI window won't open
**Solution:**
1. Check Python version: `python3 --version` (needs 3.9+)
2. Verify Flet installed: `python3 -m flet --version`
3. Try running with: `flet run gui/main.py --verbose`
4. Check error messages in terminal

### Issue: Metrics show no data
**Solution:**
1. Open Metrics page (📈 icon)
2. Click "🔄 Calculate All" button
3. Wait for calculation to complete (1-2 seconds)
4. Metrics should appear

### Issue: API connection status shows offline
**Solution:**
1. Open Settings (⚙️ icon)
2. Verify API URL is correct
3. Click "🔍 Test Connection" button
4. Check if server is running in other terminal
5. Restart server if needed

---

## 📈 Example Workflow

### Complete Analytics Review (15 minutes)

```
1. Open Application
   └─ Dashboard appears with quick stats (10 seconds)

2. Review Alerts
   └─ Click 🚨 Alerts (2 minutes)
   └─ Check problematic AAVs
   └─ Note any critical issues

3. Analyze Metrics
   └─ Click 📈 Metrics (3 minutes)
   └─ Review success rates
   └─ Look for low-performing AAVs

4. Compare Performance
   └─ Click 🔄 Compare (3 minutes)
   └─ Select two AAVs
   └─ Review differences

5. Generate Report
   └─ Click 📄 Reports (5 minutes)
   └─ Select report options
   └─ Download PDF
   └─ Share with team
```

---

## 💡 Tips & Tricks

### Search & Filter
- **AAVs Page**: Type in search box to filter by name
- **Metrics Page**: Search by AAV ID or name
- **Alerts Page**: Use dropdown to filter by alert type

### Quick Actions
- **Right-click cards**: Access additional options (future feature)
- **Keyboard shortcuts**: Use Tab to navigate between elements
- **Hover tooltips**: Hover over icons for descriptions

### Performance
- **Auto-refresh**: Enabled by default (refresh every 10 min)
- **Manual refresh**: Click 🔃 icon for immediate update
- **Batch operations**: Calculate multiple metrics at once

---

## 📱 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Tab | Navigate to next element |
| Shift+Tab | Navigate to previous element |
| Enter | Activate button/submit form |
| Escape | Close dialog (future feature) |
| Ctrl+R | Refresh current page |
| Ctrl+Q | Quit application |

---

## 🔒 Security Notes

- **API Key**: Stored locally in settings (not transmitted over HTTP)
- **Connection**: Use HTTPS in production
- **Data**: No data stored after application closes
- **Credentials**: Never commit API keys to git

---

## 📚 Further Reading

- [Flet Documentation](https://flet.dev)
- [FastAPI Docs](http://localhost:8000/docs) - Interactive API docs
- [Project README](../README.md) - Project overview
- [Design Document](DESIGN.md) - Detailed UI design

---

## 🆘 Getting Help

1. **Check Troubleshooting** section above
2. **Review error messages** in terminal
3. **Check application logs** for details
4. **Visit GitHub issues** for known problems

---

## 📝 System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.9 or higher
- **RAM**: 512MB minimum
- **Storage**: 100MB available
- **Network**: Access to localhost:8000

---

**Version**: 1.0.0  
**Last Updated**: April 12, 2026

Happy analyzing! 📊✨
