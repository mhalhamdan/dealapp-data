import logging
from data_collector import get_data_rate_limited
from collections import Counter

"""analysis.py
This script checks what are the keys from the data and how many times they appear.
"""

def main():

    response, total = get_data_rate_limited()
    
    counter = Counter()

    for data in response:
        # Count keys in data
        counter.update(data.keys())

    # Log all keys below limit
    idx = 0
    for key, value in counter.items():
        if value < total:
            idx += 1
            logging.info(f"{idx}. {key}: {value}")


    logging.info(counter)

if __name__  == "__main__":
    main()


    