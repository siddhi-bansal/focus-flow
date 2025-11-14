"""
FocusPulse Tracker: Monitors active application on macOS
Logs app activity with timestamps to CSV for analysis
"""

import csv
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from AppKit import NSWorkspace
except ImportError:
    print("Error: pyobjc is required for macOS app tracking.")
    print("Install with: pip install pyobjc")
    raise


class AppTracker:
    """Tracks active applications and logs them to CSV"""
    
    def __init__(self, log_file_path: str, enable_chrome_tab_tracking: bool = False):
        """
        Initialize the tracker.
        
        Args:
            log_file_path: Path to CSV file where activity will be logged
            enable_chrome_tab_tracking: If True, when Chrome is active record the active tab title
        """
        self.log_file = Path(log_file_path)
        self.workspace = NSWorkspace.sharedWorkspace()
        self.enable_chrome_tab_tracking = enable_chrome_tab_tracking
        
        # Initialize CSV file if it doesn't exist
        self._init_csv()
    
    def _init_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist"""
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=['timestamp', 'app_name'])
                writer.writeheader()
    
    def _get_chrome_active_tab_title(self) -> Optional[str]:
        """Return the title of the active tab in Google Chrome using AppleScript.

        Returns None if Chrome isn't running or AppleScript fails.
        """
        # AppleScript to get the title of the active tab of the front window
        script = 'tell application "Google Chrome" to get title of active tab of front window'
        try:
            output = subprocess.check_output(["osascript", "-e", script], stderr=subprocess.DEVNULL)
            title = output.decode('utf-8').strip()
            if title:
                return title
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            # osascript not available
            return None
        return None
    
    def get_active_app(self) -> str:
        """
        Get the currently active application name. If Chrome tab tracking is enabled
        and the active app is Google Chrome, return "Google Chrome - <tab title>".

        Returns:
            Name of the active application
        """
        active_app = self.workspace.activeApplication()
        app_name = active_app.get('NSApplicationName', 'Unknown')

        if self.enable_chrome_tab_tracking and app_name in ("Google Chrome", "Chrome"):
            tab_title = self._get_chrome_active_tab_title()
            if tab_title:
                return f"Google Chrome: {tab_title}"

        return app_name
    
    def log_activity(self, app_name: str) -> None:
        """
        Log app activity to CSV with timestamp.
        
        Args:
            app_name: Name of the active application
        """
        with open(self.log_file, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['timestamp', 'app_name'])
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'app_name': app_name
            })
    
    def start_tracking(self, interval: int = 10, test_duration: int = None) -> None:
        """
        Start tracking active applications.
        
        Args:
            interval: Seconds between app checks (default: 10)
            test_duration: Optional - run for N seconds for testing (None = infinite)
        """
        print(f"🎯 Starting FocusPulse tracker (logging every {interval}s)")
        print(f"📁 Logging to: {self.log_file}")
        
        current_app = None
        start_time = time.time()
        
        try:
            while True:
                active_app = self.get_active_app()
                
                # If app changed, log the new one
                if active_app != current_app:
                    self.log_activity(active_app)
                    print(f"  ✓ Switched to: {active_app}")
                    current_app = active_app
                
                # Check if test duration exceeded
                if test_duration and (time.time() - start_time) >= test_duration:
                    print("⏱️  Test duration reached. Stopping tracker.")
                    break
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n⏹️  Tracker stopped by user")


if __name__ == "__main__":
    # Example usage
    log_path = Path(__file__).parent.parent / "data" / "activity_log.csv"
    # Enable Chrome tab tracking here if you want tab-level names recorded
    tracker = AppTracker(str(log_path), enable_chrome_tab_tracking=True)
    
    # For testing: track with 1-second interval (fast for testing)
    # Run indefinitely - press Ctrl+C to stop
    tracker.start_tracking(interval=1)
