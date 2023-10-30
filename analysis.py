import logging
from dags.deals_data.modules.collect_data import get_data_rate_limited
from collections import Counter

"""analysis.py
This script checks what are the keys from the data and how many times they appear.
"""

def main():

    response = get_data_rate_limited()
    
    counter = Counter()

    for data in response:
        # Count keys in data
        counter.update(data.keys())

    # Log all keys below max
    idx = 0
    max_val = max(counter.values())

    for key, value in counter.items():
        if value < max_val:
            idx += 1
            logging.info(f"{idx}. {key}: {value}")


    logging.info(counter)

if __name__  == "__main__":
    main()
