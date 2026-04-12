# 🎨 Quality Metrics GUI - Design Document

## Visual Design System

### Color Palette
```
Primary Green     #2E7D32  - Main actions, success indicators
Secondary Blue    #1976D2  - Information, secondary actions
Accent Orange     #F57C00  - Warnings, alerts
Error Red         #D32F2F  - Critical issues
Success Green     #4CAF50  - Positive outcomes
Warning Yellow    #FFC107  - Caution indicators

Light Backgrounds #F5F5F5  - Main background
White             #FFFFFF  - Cards, surfaces
Text Dark         #1F1F1F  - Primary text
Text Gray         #666666  - Secondary text
Border Gray       #E0E0E0  - Borders
```

### Typography
```
Headers: 20-24px, Bold
Titles: 14-18px, Bold
Body: 11-14px, Regular
Captions: 9-11px, Regular
```

---

## 📐 UI Layouts

### 1️⃣ HOME DASHBOARD (Full Page View)

```
┌────────────────────────────────────────────────────────────────┐
│  📊 Quality Metrics & Analytics Platform      ✅ Connected      │
├─── ─────────────────────────────────────────────────────────────┤
│  📊 Quick Statistics                                             │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐│
│  │ 🎓 Total AAVs   │ │ 📈 Metrics      │ │ 🚨 Alerts      ││
│  │ 20              │ │ 7                │ │ 3                ││
│  │ Learning Goals  │ │ Calculated       │ │ Active           ││
│  └──────────────────┘ └──────────────────┘ └──────────────────┘│
│  ┌──────────────────┐                                           │
│  │ 📊 Success Rate │                                           │
│  │ 68.4%          │                                           │
│  │ Average         │                                           │
│  └──────────────────┘                                           │
│                                                                  │
│  🧭 Quick Navigation                                            │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐│
│  │ 🎓 Browse AAVs  │ │ 📈 View Metrics │ │ 🚨 Monitor Alerts││
│  │ View and manage │ │ Quality scores  │ │ Problematic AAVs ││
│  │ all learning    │ │ per AAV         │ │ requiring action ││
│  │ outcomes        │ │                 │ │                 ││
│  └──────────────────┘ └──────────────────┘ └──────────────────┘│
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐│
│  │ 🔄 Compare AAVs │ │ 📄 Reports      │ │ ⚙️ Settings     ││
│  │ Compare metrics │ │ Create & download│ │ Configure app   ││
│  │ between AAVs    │ │ detailed reports │ │ preferences     ││
│  └──────────────────┘ └──────────────────┘ └──────────────────┘│
│                                                                  │
│  Quality Metrics v1.0.0        Last updated: 12/04/2026 14:30  │
└────────────────────────────────────────────────────────────────┘
```

### 2️⃣ AAVS PAGE

```
┌────────────────────────────────────────────────────────────────┐
│ 🔍 Search AAVs    [300px]              ➕ Add AAV [Button]     │
├─────────────────────────────────────────────────────────────────┤
│ 📚 All Learning Outcomes (AAVs)                                 │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Types entiers                     [Discipline] [Teaching]  ││
│ │ les types entiers (int, short,                             ││
│ │ long)                                                       ││
│ │ [📊 View Metrics] [📈 History] [✏️ Edit]                  ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Arrays and Lists                  [Discipline] [Teaching]  ││
│ │ Collection types and manipulation                           ││
│ │ [📊 View Metrics] [📈 History] [✏️ Edit]                  ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                  (20 AAVs total) │
└────────────────────────────────────────────────────────────────┘
```

### 3️⃣ METRICS PAGE

```
┌────────────────────────────────────────────────────────────────┐
│ 🔍 Search metrics [300px]  🔄 Calculate All [Button]  🔃      │
├─────────────────────────────────────────────────────────────────┤
│ 📊 Quality Metrics                                              │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ AAV #1                              Success: 75.5% ▲        ││
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            ││
│ │ │ Coverage    │ │ Attempts    │ │ Learners    │            ││
│ │ │ 85.0%       │ │ 145         │ │ 42          │            ││
│ │ └─────────────┘ └─────────────┘ └─────────────┘            ││
│ │ ┌─────────────────────────────────────────┐                ││
│ │ │ Success Rate                             │ 75.5%         ││
│ │ │ [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░] │                ││
│ │ └─────────────────────────────────────────┘                ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ AAV #2                              Success: 68.3% ▼        ││
│ │ [Similar structure]                                         ││
│ └─────────────────────────────────────────────────────────────┘│
│                                          (7 metrics calculated) │
└────────────────────────────────────────────────────────────────┘
```

### 4️⃣ ALERTS PAGE

```
┌────────────────────────────────────────────────────────────────┐
│ [Filter by type ▼]                    📊 Analyze [Button]     │
├─────────────────────────────────────────────────────────────────┤
│ 🚨 Quality Alerts                                               │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 📉 AAV #5           [Difficult] Difficult 50% Success Rate ││
│ │ AAV with low success rate - Consider reviewing content     ││
│ │ [📊 View Details] [✓ Dismiss]                             ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ ⚠️ AAV #12          [Fragile] Fragile - Regression Detected ││
│ │ Learners progressing then regressing on mastery level      ││
│ │ [📊 View Details] [✓ Dismiss]                             ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ ❌ AAV #8           [Unused] No Activity (30+ days)         ││
│ │ No recent learner attempts recorded                        ││
│ │ [📊 View Details] [✓ Dismiss]                             ││
│ └─────────────────────────────────────────────────────────────┘│
│                                              (3 alerts active) │
└────────────────────────────────────────────────────────────────┘
```

### 5️⃣ COMPARISON PAGE

```
┌────────────────────────────────────────────────────────────────┐
│ [AAV Selection ▼]  VS  [AAV Selection ▼]      🔍 Compare [Btn] │
├─────────────────────────────────────────────────────────────────┤
│ 🔄 AAV Comparison                                               │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Success Rate                        ▲ 7.2%                 ││
│ │ AAV 1: 75.5% ▼ ▼ AAV 2: 68.3%                            ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Coverage                             ▼ 7.0%                 ││
│ │ AAV 1: 85.0% ▼ ▼ AAV 2: 92.0%                            ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Total Attempts                      ▲ 22                    ││
│ │ AAV 1: 145 ▼ ▼ AAV 2: 123                                ││
│ └─────────────────────────────────────────────────────────────┘│
│                                          (5 metrics compared) │
└────────────────────────────────────────────────────────────────┘
```

### 6️⃣ REPORTS PAGE

```
┌────────────────────────────────────────────────────────────────┐
│ Generate New Report                                ➕ Generate │
│ [Report Type ▼] [Format ▼] [Period ▼]                         │
├─────────────────────────────────────────────────────────────────┤
│ 📄 Generated Reports                                            │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 📄 Report #1 - Comprehensive       [PDF] [Size: 245KB]    ││
│ │ Generated: 12/04/2026 10:30:00                             ││
│ │ [📥 Download] [👁️ Preview] [🔗 Share] [🗑️ Delete]       ││
│ └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 📄 Report #2 - Quality Summary       [PDF] [Size: 125KB]   ││
│ │ Generated: 11/04/2026 15:45:00                             ││
│ │ [📥 Download] [👁️ Preview] [🔗 Share] [🗑️ Delete]       ││
│ └─────────────────────────────────────────────────────────────┘│
│                                       (6 reports generated) │
└────────────────────────────────────────────────────────────────┘
```

### 7️⃣ SETTINGS PAGE

```
┌────────────────────────────────────────────────────────────────┐
│ ⚙️ Settings                                                     │
├─────────────────────────────────────────────────────────────────┤
│ 🔌 API Configuration                                            │
│ ┌──────────────────────────────────┐                           │
│ │ API URL: [http://localhost:8000] │                          │
│ │ API Key: [••••••••••••••••••••] │                          │
│ │ [🔍 Test Connection]             │ Status: Connected ✅    │
│ └──────────────────────────────────┘                           │
│                                                                  │
│ 📱 Application Settings                                         │
│ ┌──────────────────────────────────┐                           │
│ │ Auto-refresh metrics             │ [Toggle ON]              │
│ │ Refresh interval (minutes)       │ [10 ▼]                  │
│ │ Enable notifications             │ [Toggle ON]              │
│ │ Show alerts on startup           │ [Toggle ON]              │
│ └──────────────────────────────────┘                           │
│                                                                  │
│ 🎨 Display Settings                                             │
│ ┌──────────────────────────────────┐                           │
│ │ Theme                            │ [Light ▼]               │
│ │ Font size                        │ [Normal ▼]              │
│ │ Show tooltips                    │ [Toggle ON]              │
│ └──────────────────────────────────┘                           │
└────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Component Design Details

### Stat Card
```
┌─────────────────────┐
│ 🎓  Total AAVs      │
│     20              │
│     Learning Goals  │
└─────────────────────┘
Size: Flexible (Responsive)
Bg: Light green (#E8F5E9)
Border: Subtle shadow
```

### Metric Details Card
```
┌─────────────────────────────────────┐
│ Coverage    │ 85.0% │ Attempts │ 145 │
│ Learners    │ 42    │ Deviation│18.5 │
└─────────────────────────────────────┘
```

### Alert Card
```
┌──────────────────────────────────────┐
│ 📉 AAV #5  [Difficult]  Red Border   │
│ AAV with low success rate            │
│ [Details] [Dismiss]                  │
└──────────────────────────────────────┘
```

### Progress Bar
```
Success Rate: 75.5%
[████████░░░░░░░░░░░░] 75%
Green (#2E7D32)
```

---

## 🖱️ Interaction Design

### Navigation
- **Left Sidebar**: 7 destinations with icons + labels
- **Hover State**: Subtle highlight
- **Active State**: Bold label + colored indicator
- **Responsive**: Collapses on small screens

### Form Inputs
```
Text Fields:
├─ Label (above)
├─ Placeholder text
├─ Prefix icon
└─ Border radius: 8px

Dropdowns:
├─ Label above
├─ Current value visible
└─ List on click

Switches:
├─ Blue when ON
└─ Gray when OFF
```

### Button States
```
Elevated Button:
├─ Normal: Full color + shadow
├─ Hover: Elevated shadow
└─ Disabled: Gray

Text Button:
├─ Normal: Text only
├─ Hover: Background highlight
└─ Icon: Left-aligned
```

---

## 📱 Responsive Behavior

### Desktop (1400x900)
```
[Nav | Header + Content]
Full navigation rail visible
All columns show (3-column layout)
```

### Tablet (1000x700)
```
[Nav | Header + Content]
Navigation rail visible but compact
2-column layout for cards
```

### Minimum Size
```
1000x700 (enforced)
Scrollable content
Single column adaptation
```

---

## 🎬 Animation & Transitions

- **Page Transitions**: Fade in/out (200ms)
- **Button Hover**: Color transition (100ms)
- **Progress Bars**: Smooth fill animation (500ms)
- **Alerts**: Slide in from top (300ms)

---

## ♿ Accessibility

- **Color Contrast**: WCAG AA compliant
- **Font Sizes**: Minimum 11px for readability
- **Icons + Labels**: Always paired
- **Focus States**: Clear visual indicators
- **Keyboard Navigation**: Tab through all elements

---

## 🎨 Theme Customization

### Light Theme (Default)
```
Background: #F5F5F5
Cards: #FFFFFF
Text: #1F1F1F
Accents: #2E7D32 (Green)
```

### Dark Theme (Optional)
```
Background: #121212
Cards: #1E1E1E
Text: #E0E0E0
Accents: #66BB6A (Lighter Green)
```

---

## 📊 Data Visualization

### Success Rate Colors
```
✅ >= 80%: Green (#4CAF50)
⚠️  60-79%: Orange (#FFC107)
❌ < 60%: Red (#F44336)
```

### Trend Indicators
```
▲ Higher/Better
▼ Lower/Worse
= Equal/No change
```

---

**Version**: 1.0.0  
**Last Updated**: April 2026
