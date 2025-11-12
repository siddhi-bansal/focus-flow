# 🎯 FocusPulse: Track Your Focus Patterns

An elegant, minimal Python + Streamlit app that monitors your active applications on macOS to visualize your focus patterns and productivity insights.

## 📁 Project Structure

```
focuspulse/
├── data/
│   └── activity_log.csv          # Your activity history
├── src/
│   ├── tracker.py                # App detection & logging
│   └── analyzer.py               # Data analysis & categorization
├── app.py                        # Streamlit dashboard
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Tracker

Run the tracker in the background to start logging your app activity:

```bash
python -m src.tracker
```

The tracker will:
- Detect your active app every 10 seconds
- Log app switches with timestamps to `data/activity_log.csv`
- Continue running until you press `Ctrl+C`

**💡 Tip:** Keep this running in a separate terminal window while you work.

### 3. View the Dashboard

In another terminal, start the Streamlit app:

```bash
streamlit run app.py
```

This will open a dashboard at `http://localhost:8501` showing:
- 📊 Your focus score (0-100)
- ⏱️ Time spent on focus vs distraction apps
- 📱 Breakdown by application
- 📈 Hourly activity timeline
- 💡 Personalized insights

## 📖 How It Works

### Part 1: The Tracker (`src/tracker.py`)

**Purpose:** Continuously monitor and log active applications

**Key Features:**
- Uses macOS native API (`AppKit`) to detect active app
- Logs app name + duration to CSV with ISO timestamps
- Runs in an infinite loop (can be stopped with `Ctrl+C`)
- Tracks app switches automatically

**Example Output:**
```
timestamp,app_name,duration_seconds
2024-11-11T09:15:30.123456,VSCode,300
2024-11-11T09:20:30.123456,Slack,45
2024-11-11T09:21:15.123456,VSCode,120
```

### Part 2: The Analyzer (`src/analyzer.py`)

**Purpose:** Process logs and categorize focus patterns

**Key Features:**
- Categorizes apps as: focus, distraction, or neutral
- Calculates focus score (0-100)
- Generates hourly/daily breakdowns
- Provides app-by-app usage stats

**Categories:**
- 🟢 **Focus:** VSCode, PyCharm, Notion, Gmail, etc.
- 🔴 **Distraction:** YouTube, TikTok, Twitter, Discord, etc.
- ⚪ **Neutral:** Everything else

**Customize these lists in `analyzer.py` to match YOUR apps!**

### Part 3: The Dashboard (`app.py`)

**Purpose:** Beautiful, interactive visualization of your data

**Features:**
- 🎯 Focus score gauge
- 📊 Time breakdown pie chart
- 📱 Top apps bar chart
- 📈 Hourly activity timeline
- 💡 AI-like insights
- 📅 Adjustable time range (6h, 12h, 24h, 7d)

## ⚙️ Customization

### Add Your Apps

Edit the `FOCUS_APPS` and `DISTRACTION_APPS` sets in `src/analyzer.py`:

```python
FOCUS_APPS = {
    'VSCode', 'PyCharm', 'Notion',
    # Add YOUR focus apps here
    'MyCustomApp'
}

DISTRACTION_APPS = {
    'YouTube', 'Twitter', 'Discord',
    # Add YOUR distraction apps here
    'MyGameApp'
}
```

### Change Tracking Interval

In `src/tracker.py`, modify the `start_tracking()` call:

```python
tracker.start_tracking(interval=5)  # Check every 5 seconds (default: 10)
```

### Adjust Dashboard Theme

Modify the custom CSS in `app.py`:

```python
st.markdown("""
    <style>
        /* Your custom CSS here */
    </style>
    """, unsafe_allow_html=True)
```

## 📊 Example Workflow

**Day 1:**
1. Start the tracker: `python -m src.tracker`
2. Work normally for a few hours
3. Stop the tracker
4. View the dashboard: `streamlit run app.py`

**Day 2+:**
1. Run tracker continuously
2. Check dashboard multiple times per day
3. Adjust your focus apps list based on insights

## 🎯 Tips for Best Results

1. **Be consistent:** Keep the tracker running throughout your workday
2. **Customize categories:** The default app lists may not match your workflow
3. **Take breaks:** Use the insights to identify when to take focus breaks
4. **Review regularly:** Check your dashboard weekly to spot patterns
5. **Export data:** Use the raw data viewer to analyze specific sessions

## 🛠️ Troubleshooting

**"Import AppKit failed"**
- Make sure you installed `pyobjc`: `pip install pyobjc`
- This only works on macOS!

**"No activity data yet"**
- Run the tracker first and let it log for a few minutes
- Check that `data/activity_log.csv` is being created

**Dashboard not updating**
- Streamlit caches the data. Hard refresh the browser (Cmd+Shift+R)
- Or restart: `streamlit run app.py`

**"localhost:8501 refused to connect"**
- Wait a moment for Streamlit to start
- Check the terminal for errors

## 📝 Next Steps & Ideas

- [ ] Add Pomodoro timer integration
- [ ] Push notifications for long distraction sessions
- [ ] Weekly email reports
- [ ] Goal-setting and streak tracking
- [ ] Export weekly/monthly reports as PDF
- [ ] Dark mode dashboard
- [ ] ML-based focus recommendations
- [ ] Integration with calendar events

## 📄 License

This project is open source. Use it, modify it, improve it!

---

**Happy tracking! 🚀 Turn your data into focus.** ✨
