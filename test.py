#!/usr/bin/env python3
"""Tests for thermo.py"""

import subprocess
import sys
import pytest

PYTHON = sys.executable

def run(args):
    result = subprocess.run([PYTHON, 'thermo.py'] + args, capture_output=True, text=True)
    return result.stdout + result.stderr

def test_status():
    output = run(['status'])
    assert 'WiFi Smart Thermostat Status' in output
    assert 'State:' in output
    assert 'Target Temp:' in output

def test_help():
    output = run([])
    assert 'Usage:' in output
    assert 'set-temp' in output

def test_unknown_command():
    output = run(['invalid-command'])
    assert 'Unknown command' in output

def test_set_temp_invalid_range():
    output = run(['set-temp', '50'])
    assert 'Error' in output or 'between' in output.lower()

def test_mode_invalid():
    output = run(['mode', 'invalid'])
    assert 'Unknown command' in output

def test_system_mode_invalid():
    output = run(['system-mode', 'invalid'])
    assert 'Unknown command' in output

