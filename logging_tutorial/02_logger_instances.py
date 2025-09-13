#!/usr/bin/env python3
"""
Using Logger Instances - The Right Way to Log
"""

import logging
import sys

# Create a custom logger (better than using root logger)
logger = logging.getLogger(__name__)  # __name__ gives you module path
logger.setLevel(logging.DEBUG)  # Logger's minimum level

# Create handlers - where logs go
console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler('app.log')

# Set levels for each handler (can be different!)
console_handler.setLevel(logging.INFO)   # Console only shows INFO+
file_handler.setLevel(logging.DEBUG)     # File gets everything

# Create formatters - how logs look
console_format = logging.Formatter('%(levelname)s: %(message)s')
detailed_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)

# Attach formatters to handlers
console_handler.setFormatter(console_format)
file_handler.setFormatter(detailed_format)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Now let's test it
def process_data(data):
    """Example function showing logging in context"""
    logger.debug(f"Starting to process: {data}")
    
    if not data:
        logger.warning("Empty data received")
        return None
    
    try:
        result = len(data) * 2
        logger.info(f"Successfully processed data, result: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to process data: {e}", exc_info=True)
        return None

def main():
    logger.info("Application started")
    
    # Test different scenarios
    process_data("hello")
    process_data("")
    process_data(None)  # This will cause an error
    
    logger.info("Application finished")

if __name__ == "__main__":
    main()
    print("\nCheck 'app.log' file for detailed logs!")