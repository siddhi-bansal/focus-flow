"""
FocusPulse Dashboard: Interactive Streamlit application
Visualizes focus patterns and provides insights
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import threading

# Load environment variables before importing other modules
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # python-dotenv not installed

from src.analyzer import ActivityAnalyzer
from src.gpt_enricher import GPTEnricher


# Page configuration
st.set_page_config(
    page_title="FocusPulse",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimal, clean design
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        color: #1f77b4;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)


def load_analyzer():
    """Load the analyzer (fresh data every time for real-time updates)"""
    log_path = Path(__file__).parent / "data" / "activity_log.csv"
    return ActivityAnalyzer(str(log_path))


def plot_focus_gauge(score: float) -> go.Figure:
    """Create a gauge chart for focus score"""
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Focus Score", 'font': {'size': 20}},
        number={'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1f77b4", 'thickness': 0.3},
            'steps': [
                {'range': [0, 33], 'color': "#ffcccc"},
                {'range': [33, 66], 'color': "#ffffcc"},
                {'range': [66, 100], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': 50
            }
        }
    )])
    fig.update_layout(height=400, margin=dict(l=50, r=50, t=100, b=50))
    return fig


def plot_time_breakdown(focus: int, distraction: int, neutral: int) -> go.Figure:
    """Create a pie chart for time breakdown"""
    labels = ['Focus', 'Distraction', 'Neutral']
    values = [focus, distraction, neutral]
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hovertemplate='%{label}<br>%{customdata}s<extra></extra>',
        customdata=values
    )])
    fig.update_layout(height=400)
    return fig


def plot_app_usage(app_data: dict, limit: int = 10) -> go.Figure:
    """Create a bar chart for top apps"""
    top_apps = dict(list(app_data.items())[:limit])
    apps = list(top_apps.keys())
    times_seconds = list(top_apps.values())
    
    # Color by category
    analyzer = load_analyzer()
    colors = [
        '#2ecc71' if analyzer.categorize_app(app) == 'focus'
        else '#e74c3c' if analyzer.categorize_app(app) == 'distraction'
        else '#95a5a6'
        for app in apps
    ]
    
    fig = go.Figure(data=[go.Bar(
        x=times_seconds,
        y=apps,
        orientation='h',
        marker=dict(color=colors),
        hovertemplate='%{y}<br>%{x}s<extra></extra>'
    )])
    
    fig.update_layout(
        height=400,
        xaxis_title="Time (seconds)",
        yaxis_autorange="reversed",
        hovermode='closest'
    )
    return fig


# Activity Timeline removed — replaced by Activity Log (detailed switches)


def main():
    """Main Streamlit app"""
    
    # Header
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.markdown("# 🎯 FocusPulse")
        st.markdown("*Track your focus, visualize your patterns*")
    
    # Sidebar for controls
    st.sidebar.title("⚙️ Settings")
    time_range = st.sidebar.radio(
        "Time Range",
        options=[6, 12, 24, 168],
        format_func=lambda x: f"Last {x}h" if x < 24 else "Last 7 days"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **FocusPulse** monitors your active applications to help you "
        "understand your focus patterns. Data is stored locally."
    )
    
    # Load data
    analyzer = load_analyzer()
    
    # Check if we have data
    if analyzer.df.empty or len(analyzer.df) == 0:
        st.warning(
            "📭 No activity data yet. Start the tracker to begin logging your apps.\n\n"
            "Run: `python -m src.tracker`"
        )
        return
    
    # Get analytics
    summary = analyzer.get_summary(hours=time_range)
    score = analyzer.get_focus_score(hours=time_range)
    app_breakdown = analyzer.get_app_breakdown(hours=time_range)
    
    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Focus Time",
            f"{summary['focus_time']}s",
            delta=f"{summary['focus_percentage']:.0f}%"
        )
    
    with col2:
        st.metric(
            "🔴 Distraction Time",
            f"{summary['distraction_time']}s",
            delta=f"{summary['distraction_percentage']:.0f}%"
        )
    
    with col3:
        st.metric(
            "📊 Focus Score",
            f"{score}",
            delta=f"vs. 50" if score >= 50 else f"vs. 50"
        )
    
    with col4:
        sessions = summary['session_count']
        st.metric(
            "📱 App Switches",
            sessions
        )
    
    st.markdown("---")
    
    # Main visualizations - full width
    st.markdown("### 📊 Analytics")
    
    col_gauge, col_pie = st.columns([1, 1])
    
    with col_gauge:
        st.plotly_chart(
            plot_focus_gauge(score),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    with col_pie:
        st.plotly_chart(
            plot_time_breakdown(
                summary['focus_time'],
                summary['distraction_time'],
                summary['neutral_time']
            ),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    st.markdown("---")
    
    # (Activity Timeline removed — replaced by Activity Log below)
    
    # App breakdown
    st.markdown("### 📱 Application Usage")
    col_apps = st.columns([1.5])[0]
    
    with col_apps:
        st.plotly_chart(
            plot_app_usage(app_breakdown),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    st.markdown("---")
    
    # Activity Log
    st.markdown("### 📋 Activity Log")
    activity_log = analyzer.get_activity_log(hours=time_range)
    
    if not activity_log.empty:
        # Color code the dataframe
        def style_category(val):
            if val == 'focus':
                return 'background-color: #d4edda'
            elif val == 'distraction':
                return 'background-color: #f8d7da'
            else:
                return 'background-color: #f5f5f5'
        
        styled_df = activity_log.style.map(
            style_category,
            subset=['Category']
        )
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity data available yet.")
    
    st.markdown("---")
    
    # Insights
    st.markdown("### 💡 Insights")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        if score >= 75:
            st.success("🏆 Excellent focus! Keep it up!")
        elif score >= 50:
            st.info("👍 Good focus. Room for improvement.")
        else:
            st.warning("⚠️ Low focus. Try a focus session!")
    
    with insight_col2:
        if summary['distraction_percentage'] > 30:
            seconds_distracted = summary['distraction_time']
            st.warning(
                f"⏰ Distraction time is high ({summary['distraction_percentage']:.0f}%, "
                f"{seconds_distracted}s). Consider taking breaks."
            )
        else:
            st.success(
                f"✨ Distraction well managed ({summary['distraction_percentage']:.0f}%)"
            )
    
    with insight_col3:
        if app_breakdown:
            top_app = list(app_breakdown.keys())[0]
            top_seconds = app_breakdown[top_app]
            st.info(f"📌 Top app: **{top_app}** ({top_seconds}s)")
    
    # Raw data viewer
    with st.expander("📊 View Raw Data"):
        st.dataframe(analyzer.df.sort_values('timestamp', ascending=False), use_container_width=True)
    
    st.markdown("---")
    
    # AI Classification Section
    st.markdown("### 🤖 Activity Classifications")
    st.markdown("Review and adjust how your apps and websites are categorized.")
    
    enricher = GPTEnricher()
    
    # Get unique apps from activity log
    if not analyzer.df.empty and 'display' in analyzer.df.columns:
        unique_apps = analyzer.df['display'].unique()
        
        if len(unique_apps) > 0:
            # Filter out system processes that shouldn't be classified
            system_apps = {'Login Window', 'loginwindow', 'WindowServer', 'Dock'}
            
            # Pre-load all classifications once (don't force re-classification)
            classifications = {}
            
            # Show loading indicator while classifying
            with st.spinner("🔄 Loading AI classifications..."):
                for app in sorted(unique_apps)[:30]:
                    if not app or app == '' or app in system_apps:
                        continue
                    classifications[app] = enricher.classify(app, force=False)
            
            for app in sorted(unique_apps)[:30]:  # Show first 30
                if not app or app == '' or app in system_apps:
                    continue
                
                result = classifications[app]
                category = result.get('category', 'neutral')
                is_override = result.get('user_override', False)
                original_category = None
                is_not_set = (category == 'not set')
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(f"📱 {app}")
                
                with col2:
                    # Show category with indicator if manually changed
                    if is_override and 'original_category' in result:
                        original_category = result['original_category']
                        st.caption(f"✏️ You changed from: {original_category}")
                    
                    # Highlight "not set" in red
                    if is_not_set:
                        st.markdown(f"<span style='color: red; font-weight: bold;'>⚠️ Not Set</span>", unsafe_allow_html=True)
                    
                    # Dropdown for selecting category
                    valid_categories = ["focus", "distraction", "neutral"]
                    current_index = valid_categories.index(category) if category in valid_categories else 2
                    
                    new_category = st.selectbox(
                        "Category",
                        valid_categories,
                        index=current_index,
                        key=f"cat_{app}",
                        label_visibility="collapsed"
                    )
                    
                    # If user changed it, save override (without rerun in the loop)
                    if new_category != category:
                        enricher.save_override(
                            text=app,
                            category=new_category,
                            confidence=100.0,
                            rationale=f"Manually set to {new_category}"
                        )
                        st.success(f"✓ Saved")
                        # We'll rerun at the end if any changes were made
                
                with col3:
                    if is_override:
                        col_label, col_btn = st.columns([2, 1])
                        with col_label:
                            st.caption("✏️ Manually set")
                        with col_btn:
                            if st.button("↩️", key=f"revert_{app}", help="Switch back to AI prediction"):
                                # Get fresh AI prediction
                                ai_result = enricher.classify(app, force=True)
                                # Remove from cache to go back to AI
                                import hashlib
                                import json
                                from pathlib import Path
                                cache_key = hashlib.sha256(app.encode()).hexdigest()
                                cache_file = Path("data/gpt_cache.json")
                                if cache_file.exists():
                                    cache = json.loads(cache_file.read_text())
                                    if cache_key in cache:
                                        del cache[cache_key]
                                        cache_file.write_text(json.dumps(cache, indent=2))
                                st.rerun()
                    elif is_not_set:
                        st.markdown(f"<span style='color: red;'>❌ AI failed</span>", unsafe_allow_html=True)
                    else:
                        st.caption(f"🤖 AI: {result.get('confidence', 0):.0f}%")
        else:
            st.info("No activities tracked yet. Start using your apps and they'll appear here!")
    else:
        st.info("No activity data available yet.")


if __name__ == "__main__":
    main()
