import pytest
from src.analyzer import ActivityAnalyzer


def test_extract_base_app_colon():
    a = ActivityAnalyzer.__new__(ActivityAnalyzer)
    assert a._extract_base_app('Google Chrome: FocusPulse') == 'Google Chrome'


def test_extract_base_app_dash():
    a = ActivityAnalyzer.__new__(ActivityAnalyzer)
    raw = 'Google Chrome - Inbox (9,848) - Gmail'
    assert a._extract_base_app(raw) == 'Google Chrome'


def test_derive_display_title_chrome():
    a = ActivityAnalyzer.__new__(ActivityAnalyzer)
    base = a._extract_base_app('Google Chrome: FocusPulse')
    display = a._derive_display_title('Google Chrome: FocusPulse', base)
    assert 'Chrome' in display and 'FocusPulse' in display


def test_sanitize_masks_email():
    a = ActivityAnalyzer.__new__(ActivityAnalyzer)
    s = a._sanitize_text('Contact me at alice@example.com for details')
    assert '[redacted email]' in s


def test_sanitize_truncates_long():
    a = ActivityAnalyzer.__new__(ActivityAnalyzer)
    long = 'A' * 200
    s = a._sanitize_text(long, max_length=50)
    assert len(s) <= 50 and s.endswith('...')
