import time
import logging
import requests
from deals_data.modules.config import config

logger = logging.getLogger(__name__)
API_URL = "https://api.dealapp.sa/production/ad"

def get_data(limit=1, page=1) -> requests.Response:
    response = requests.get(
        API_URL, 
        headers={"Authorization": config["TOKEN"]},
        params={
            "limit": limit,
            "page": page
        }
    )
    return response

def get_data_rate_limited():
    LIMIT = 10
    SLEEP_TIME = 60

    # Determine how many pages to get
    has_next_page = True
    page = 1
    data = []

    # Get data from each page
    while has_next_page:

        response = get_data(limit=LIMIT, page=page)
        has_next_page = response.json()["hasNextPage"]
        total_pages = response.json()["totalPage"]
        calls_left = int(response.headers["X-RateLimit-Remaining"])

        logger.info(f"Retrieving page {page} of {total_pages} pages. Calls left: {calls_left}")

        data += response.json()["data"]

        if calls_left <= 1:
            logger.info(f"Ran out of calls, sleeping for {SLEEP_TIME} seconds...")
            time.sleep(SLEEP_TIME)

        time.sleep(1)

        page += 1

    return data
