"""
For Hamr
"""
# avoid conflict between CGI and print
import sys
sys.stdout = sys.stderr

from app import app
