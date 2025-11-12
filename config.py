"""
FocusPulse Configuration
======================

Customize these settings to match YOUR focus patterns and apps.
"""

# ============================================================================
# APP CATEGORIZATION
# ============================================================================
# Update these to match YOUR actual apps and workflow!

FOCUS_APPS = {
    # Development
    'VSCode',
    'PyCharm',
    'Xcode',
    'Sublime Text',
    'IntelliJ IDEA',
    
    # Documentation & Writing
    'Notion',
    'Obsidian',
    'Microsoft Word',
    'Pages',
    'Google Docs',
    
    # Communication (work)
    'Gmail',
    'Slack',
    'Zoom',
    'Microsoft Teams',
    
    # Terminals & CLIs
    'Terminal',
    'iTerm2',
    'iTerm',
    
    # Browsers (with exceptions)
    'Google Chrome',
    'Safari',
    'Firefox',
}

DISTRACTION_APPS = {
    # Video & Entertainment
    'YouTube',
    'Netflix',
    'Prime Video',
    'TikTok',
    'Twitch',
    
    # Social Media
    'Twitter',
    'X',
    'Reddit',
    'Instagram',
    'Facebook',
    
    # Communication (personal)
    'Discord',
    'Telegram',
    'WhatsApp',
    'Messages',
    
    # Games & Time-wasters
    'Steam',
    'Epic Games',
    'App Store',
    
    # Music & Podcasts (when procrastinating)
    'Spotify',
    'Apple Music',
    'Podcast Addict',
}

# ============================================================================
# TRACKER SETTINGS
# ============================================================================

# How often to check for app changes (in seconds)
# Lower = more accurate but uses more CPU
# Higher = less accurate but lighter on system
TRACKER_INTERVAL = 10  # Default: 10 seconds

# How long to run tracker for testing (None = infinite)
TRACKER_TEST_DURATION = None  # Set to 60 for 60-second test

# ============================================================================
# DASHBOARD SETTINGS
# ============================================================================

# Default time range for dashboard (in hours)
DEFAULT_TIME_RANGE = 24  # Last 24 hours

# Available time ranges users can select
AVAILABLE_RANGES = [6, 12, 24, 168]  # 6h, 12h, 24h, 7d

# Focus score thresholds (for insights)
SCORE_EXCELLENT = 75
SCORE_GOOD = 50
SCORE_LOW = 30

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

# Color scheme for charts
COLORS = {
    'focus': '#2ecc71',        # Green
    'distraction': '#e74c3c',  # Red
    'neutral': '#95a5a6',      # Gray
    'secondary': '#3498db',    # Blue
    'success': '#27ae60',       # Dark green
    'warning': '#f39c12',       # Orange
    'danger': '#c0392b',        # Dark red
}

# Dashboard title and emoji
APP_TITLE = "🎯 FocusPulse"
APP_SUBTITLE = "Track your focus, visualize your patterns"
APP_ICON = "🎯"

# ============================================================================
# INSIGHTS SETTINGS
# ============================================================================

# High distraction threshold (%)
HIGH_DISTRACTION_THRESHOLD = 30

# Default number of apps to show in breakdown
TOP_APPS_LIMIT = 10

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# CSV encoding
CSV_ENCODING = 'utf-8'

# CSV delimiter
CSV_DELIMITER = ','

# Timestamp format (ISO 8601)
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

# ============================================================================
# NOTES FOR CUSTOMIZATION
# ============================================================================
"""
IMPORTANT: Update FOCUS_APPS and DISTRACTION_APPS to match YOUR workflow!

Examples of customization:

1. If you use VS Code but often work in terminals:
   - Add 'Terminal' or 'iTerm2' to FOCUS_APPS
   
2. If you use Slack for personal chat:
   - Move 'Slack' from FOCUS_APPS to DISTRACTION_APPS
   
3. If you watch educational videos:
   - Remove 'YouTube' from DISTRACTION_APPS
   
4. If you code in PyCharm:
   - Already included! But add others you use
   
5. If you use a specific design tool:
   - Add it! Examples: 'Figma', 'Sketch', 'Adobe XD'

The goal is to make the categorization match YOUR definition of
"focus work" vs "distraction", not what's common for others!
"""
