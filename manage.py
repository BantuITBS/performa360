#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    # Add the parent directory to the system path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perf_mgmt.settings')
    
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
