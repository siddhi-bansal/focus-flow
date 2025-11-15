# Windows Support for FocusPulse

## Current Status

FocusPulse is currently **macOS-only** due to platform-specific app tracking. To support Windows, we need to replace:
1. **Active app detection** (currently uses macOS AppKit)
2. **Chrome tab tracking** (currently uses macOS AppleScript)

## What Needs to Change

### 1. Active App Detection (Required for Windows)

**Current (macOS):**
```python
from AppKit import NSWorkspace
workspace = NSWorkspace.sharedWorkspace()
active_app = workspace.activeApplication()
```

**Windows Alternative:**
Use `pygetwindow` (cross-platform) or `win32gui` (Windows-specific).

**Recommended approach:** Add conditional imports in `src/tracker.py`:

```python
import sys

if sys.platform == 'darwin':
    from AppKit import NSWorkspace
    # macOS implementation
    class AppTracker:
        def __init__(self):
            self.workspace = NSWorkspace.sharedWorkspace()
        def get_active_app(self):
            app = self.workspace.activeApplication()
            return app.get('NSApplicationName', 'Unknown')
            
elif sys.platform == 'win32':
    import win32gui
    # Windows implementation
    class AppTracker:
        def get_active_app(self):
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
```

This uses:
- `pywin32` (Windows, part of `win32gui`)
- `pygetwindow` (cross-platform fallback)

**Dependency:** Add to `requirements.txt`:
```
pywin32; sys_platform == 'win32'
```

### 2. Chrome Tab Tracking (Optional for Windows)

**Current (macOS):**
```python
subprocess.check_output(["osascript", "-e", "tell application \"Google Chrome\" ..."])
```

**Windows Alternative:**
Use Chrome's DevTools Protocol (more reliable) or UIA (UI Automation):

**Option A: Chrome Remote Debugging Protocol (Recommended)**
- Requires Chrome to be started with `--remote-debugging-port=9222`
- Query active tab via HTTP API
- Works reliably and doesn't require UI automation hacks

```python
import requests
def _get_chrome_active_tab_title_windows(self):
    try:
        resp = requests.get('http://localhost:9222/json/list')
        tabs = resp.json()
        if tabs:
            return tabs[0].get('title', 'Chrome')
    except:
        return None
```

**Option B: pyautogui + OCR (Fragile)**
- Screenshot the title bar and OCR it — not recommended, slow and unreliable.

**Option C: Win32 UI Automation (WinAppDriver)**
- Complex, requires Windows SDK.

**Recommendation:** Stick with Option A (Chrome DevTools Protocol). It's:
- Fast and reliable
- Works cross-platform (macOS Chrome also supports it)
- Doesn't require AppleScript or system automation
- User has to opt-in (start Chrome with flag)

If you do this, the code becomes:
```python
if self.enable_chrome_tab_tracking:
    # macOS uses AppleScript
    # Windows uses DevTools Protocol
    # Both set app_name to "Google Chrome: <title>"
```

### 3. CSV & Data Model (No Changes)

The CSV format stays the same:
```
timestamp,app_name
2025-11-14T10:00:00.000000,Visual Studio Code
2025-11-14T10:00:05.000000,Chrome: GitHub
```

The analyzer, sanitizer, and dashboard are **platform-agnostic** and require zero changes.

## Implementation Roadmap for Windows

**Phase 1 (Minimal):** Active app tracking only
- Add `pywin32` dependency
- Create `src/tracker_windows.py` with Windows-specific logic
- Use platform detection in `src/tracker.py` to import the right implementation
- No Chrome tab tracking initially

**Phase 2 (Nice-to-have):** Chrome tab tracking
- Add Chrome DevTools Protocol support
- User documentation on starting Chrome with `--remote-debugging-port=9222`

## Estimated Effort

- Phase 1: ~2–4 hours (basic app tracking, conditional imports, testing)
- Phase 2: ~1–2 hours (Chrome tab support)
- Total: ~3–6 hours for full Windows parity

## Testing on Windows

1. Use a Windows VM or native machine
2. Run the tracker and verify CSV logs appear
3. Check Streamlit dashboard displays data correctly
4. Test Chrome tab tracking if Phase 2 is implemented

## Files to Modify/Create

| File | Change | Difficulty |
|------|--------|------------|
| `src/tracker.py` | Add platform detection & conditional imports | Low |
| `src/tracker_windows.py` | New file with Windows-specific tracking | Medium |
| `requirements.txt` | Add `pywin32` with platform condition | Low |
| `README.md` | Document Windows support & setup | Low |

## Known Limitations on Windows

1. **UAC (User Account Control):** Some apps may be hidden from tracking if UAC blocks access.
2. **Chrome tab titles:** Requires DevTools Protocol (user must start Chrome with flag, or we auto-launch).
3. **Virtual desktops:** Windows virtual desktops might hide some apps; similar to macOS Spaces.

## Recommendation

I recommend **deferring Windows support** to v2 unless:
- You have a specific Windows user asking for it
- You want to use FocusPulse on Windows yourself

For now, the macOS implementation is solid and feature-complete. Windows can follow once we stabilize the core.

---

**To implement Windows support, let me know and I'll:**
1. Add the platform detection and import logic
2. Create the Windows tracker module
3. Update requirements.txt
4. Provide setup docs for Windows users
