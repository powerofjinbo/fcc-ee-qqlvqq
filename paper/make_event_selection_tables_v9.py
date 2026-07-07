#!/usr/bin/env python3
"""v9 entry point for the paper-style event-selection table figure."""

from make_event_selection_tables_v8 import main
import sys


if __name__ == "__main__":
    main([*sys.argv[1:], "--version", "v9"])
