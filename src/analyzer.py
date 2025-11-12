"""
FocusPulse Analyzer: Processes activity logs and categorizes focus patterns
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class ActivityAnalyzer:
    """Analyzes activity log data and categorizes focus vs distraction"""
    
    # Apps considered as "focus" work
    FOCUS_APPS = {
        'VSCode', 'PyCharm', 'Xcode', 'Sublime Text',
        'Notion', 'Obsidian', 'Microsoft Word', 'Pages',
        'Terminal', 'iTerm2', 'Slack', 'Gmail',
        'Google Chrome', 'Safari', 'Firefox'
    }
    
    # Apps considered as "distraction"
    DISTRACTION_APPS = {
        'Instagram', 'TikTok', 'Twitter', 'X', 'YouTube',
        'Reddit', 'Discord', 'Telegram', 'Messages',
        'Spotify', 'Music', 'Netflix', 'Prime Video'
    }
    
    def __init__(self, log_file_path: str):
        """
        Initialize the analyzer.
        
        Args:
            log_file_path: Path to the activity_log.csv file
        """
        self.log_file = Path(log_file_path)
        self.df = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load and parse the activity log CSV"""
        if not self.log_file.exists():
            print(f"Warning: {self.log_file} not found. Creating empty dataframe.")
            self.df = pd.DataFrame(columns=['timestamp', 'app_name'])
            return

        self.df = pd.read_csv(self.log_file)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])

        # Calculate duration for each row as time until next row (or now for last)
        self.df['duration_seconds'] = 0
        for i in range(len(self.df) - 1):
            duration = (self.df.iloc[i + 1]['timestamp'] -
                        self.df.iloc[i]['timestamp']).total_seconds()
            self.df.loc[i, 'duration_seconds'] = int(duration)

        # For the last (current) app, calculate from its timestamp to now
        if len(self.df) > 0:
            last_duration = (datetime.now() -
                             self.df.iloc[-1]['timestamp']).total_seconds()
            self.df.loc[len(self.df) - 1, 'duration_seconds'] = int(last_duration)
    
    def categorize_app(self, app_name: str) -> str:
        """
        Categorize an app as focus, distraction, or neutral.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Category: 'focus', 'distraction', or 'neutral'
        """
        if app_name in self.FOCUS_APPS:
            return 'focus'
        elif app_name in self.DISTRACTION_APPS:
            return 'distraction'
        return 'neutral'
    
    def get_summary(self, hours: int = 24) -> dict:
        """
        Get a summary of focus vs distraction time.
        
        Args:
            hours: Look back this many hours (default: 24)
            
        Returns:
            Dictionary with focus, distraction, and neutral statistics
        """
        if self.df.empty:
            return {
                'focus_time': 0, 'distraction_time': 0, 'neutral_time': 0,
                'focus_percentage': 0, 'distraction_percentage': 0,
                'total_tracked': 0, 'session_count': 0
            }
        
        # Filter by time range
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_df = self.df[self.df['timestamp'] >= cutoff_time]
        
        if recent_df.empty:
            return {
                'focus_time': 0, 'distraction_time': 0, 'neutral_time': 0,
                'focus_percentage': 0, 'distraction_percentage': 0,
                'total_tracked': 0, 'session_count': 0
            }
        
        # Categorize each entry
        recent_df = recent_df.copy()
        recent_df['category'] = recent_df['app_name'].apply(self.categorize_app)
        
        # Calculate totals
        focus_time = recent_df[recent_df['category'] == 'focus']['duration_seconds'].sum()
        distraction_time = recent_df[
            recent_df['category'] == 'distraction'
        ]['duration_seconds'].sum()
        neutral_time = recent_df[recent_df['category'] == 'neutral']['duration_seconds'].sum()
        total_time = focus_time + distraction_time + neutral_time
        
        # Calculate percentages
        if total_time > 0:
            focus_pct = (focus_time / total_time) * 100
            distraction_pct = (distraction_time / total_time) * 100
        else:
            focus_pct = distraction_pct = 0
        
        return {
            'focus_time': focus_time,
            'distraction_time': distraction_time,
            'neutral_time': neutral_time,
            'focus_percentage': round(focus_pct, 1),
            'distraction_percentage': round(distraction_pct, 1),
            'total_tracked': total_time,
            'session_count': len(recent_df)
        }
    
    def get_app_breakdown(self, hours: int = 24) -> dict:
        """
        Get time spent on each application.
        
        Args:
            hours: Look back this many hours
            
        Returns:
            Dictionary with app names and their usage time
        """
        if self.df.empty:
            return {}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_df = self.df[self.df['timestamp'] >= cutoff_time]
        
        app_time = recent_df.groupby('app_name')['duration_seconds'].sum().sort_values(
            ascending=False
        )
        
        return app_time.to_dict()
    
    def get_focus_score(self, hours: int = 24) -> float:
        """
        Calculate a focus score (0-100).
        
        Args:
            hours: Look back this many hours
            
        Returns:
            Focus score where 100 = all focus time, 0 = no focus time
        """
        summary = self.get_summary(hours)
        if summary['total_tracked'] == 0:
            return 0.0
        
        focus_ratio = summary['focus_time'] / summary['total_tracked']
        score = focus_ratio * 100
        return round(score, 1)
    
    def get_activity_log(self, hours: int = 24) -> pd.DataFrame:
        """
        Get detailed activity log with category and formatted time.
        
        Args:
            hours: Look back this many hours
            
        Returns:
            DataFrame with app, duration, category, and formatted time
        """
        if self.df.empty:
            return pd.DataFrame()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_df = self.df[self.df['timestamp'] >= cutoff_time].copy()
        
        # Add category
        recent_df['category'] = recent_df['app_name'].apply(self.categorize_app)
        
        # Format time column for display
        recent_df['time'] = recent_df['timestamp'].dt.strftime('%H:%M:%S')
        
        # Select columns for display and reverse order (most recent first)
        display_df = recent_df[['time', 'app_name', 'category', 'duration_seconds']].copy()
        display_df.columns = ['Time', 'App', 'Category', 'Duration (s)']
        display_df = display_df.iloc[::-1].reset_index(drop=True)
        
        return display_df

    def get_timeline(self, hours: int = 24) -> pd.DataFrame:
        """
        Get hourly breakdown of focus vs distraction.

        Args:
            hours: Look back this many hours

        Returns:
            DataFrame with hourly statistics
        """
        if self.df.empty:
            return pd.DataFrame()

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_df = self.df[self.df['timestamp'] >= cutoff_time].copy()

        # Categorize
        recent_df['category'] = recent_df['app_name'].apply(self.categorize_app)

        # Extract hour
        recent_df['hour'] = recent_df['timestamp'].dt.floor('h')

        # Group by hour and category
        timeline = recent_df.groupby(['hour', 'category'])['duration_seconds'].sum().unstack(
            fill_value=0
        )

        return timeline


def print_summary(analyzer: ActivityAnalyzer) -> None:
    """Pretty print the activity summary"""
    summary = analyzer.get_summary(hours=24)
    score = analyzer.get_focus_score(hours=24)
    
    print("\n" + "=" * 50)
    print("📊 FocusPulse Daily Summary")
    print("=" * 50)
    
    print(f"\n🎯 Focus Score: {score}/100")
    
    hours_focused = summary['focus_time'] / 3600
    hours_distracted = summary['distraction_time'] / 3600
    hours_neutral = summary['neutral_time'] / 3600
    
    print(f"\n⏱️  Time Breakdown (24h):")
    print(f"  • 🟢 Focus: {hours_focused:.1f}h ({summary['focus_percentage']}%)")
    print(f"  • 🔴 Distraction: {hours_distracted:.1f}h ({summary['distraction_percentage']}%)")
    print(f"  • ⚪ Neutral: {hours_neutral:.1f}h")
    
    print(f"\n📱 Top Apps:")
    app_breakdown = analyzer.get_app_breakdown(hours=24)
    for i, (app, seconds) in enumerate(list(app_breakdown.items())[:5], 1):
        category = analyzer.categorize_app(app)
        emoji = '🟢' if category == 'focus' else '🔴' if category == 'distraction' else '⚪'
        minutes = seconds / 60
        print(f"  {i}. {emoji} {app}: {minutes:.0f}m")
    
    print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    # Example usage
    log_path = Path(__file__).parent.parent / "data" / "activity_log.csv"
    analyzer = ActivityAnalyzer(str(log_path))
    print_summary(analyzer)
