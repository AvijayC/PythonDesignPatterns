#!/usr/bin/env python3
"""
Basic Logging in Python - Understanding Log Levels
"""

import logging

# By default, Python only shows WARNING and above
print("=== Default Behavior (no configuration) ===")
logging.debug("This is a debug message")      # Won't show
logging.info("This is an info message")       # Won't show  
logging.warning("This is a warning message")  # Will show
logging.error("This is an error message")     # Will show
logging.critical("This is a critical message") # Will show

print("\n=== After Basic Configuration ===")
# Configure logging to show ALL messages
logging.basicConfig(
    level=logging.DEBUG,  # Minimum level to display
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Now all messages will show
logging.debug("Debug: Detailed diagnostic info")
logging.info("Info: General informational messages")
logging.warning("Warning: Something unexpected happened")
logging.error("Error: A serious problem occurred")
logging.critical("Critical: The program may not be able to continue")

# Log levels as numbers (useful to know)
print("\n=== Log Level Values ===")
print(f"DEBUG: {logging.DEBUG}")       # 10
print(f"INFO: {logging.INFO}")         # 20
print(f"WARNING: {logging.WARNING}")   # 30
print(f"ERROR: {logging.ERROR}")       # 40
print(f"CRITICAL: {logging.CRITICAL}") # 50

# You can also use custom levels
VERBOSE = 15  # Between DEBUG and INFO
logging.addLevelName(VERBOSE, "VERBOSE")
logging.log(VERBOSE, "This is a verbose message")