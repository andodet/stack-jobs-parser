# Revise import order
import os
import utils
import time
import json

import feed_parse

from google.oauth2 import service_account
from google.cloud import storage


def main(request):

    creds_blob = storage.Client().get_bucket("jobs-gsheet").get_blob(os.environ["GOOGLE_AUTH_KEY"])\
        .download_as_string()
    parsed_creds = json.loads(creds_blob)

    # Get gAuth credentials
    credentials = service_account.Credentials.from_service_account_info(
        parsed_creds
    )

    scoped_credentials = credentials.with_scopes(["https://spreadsheets.google.com/feeds"])

    print("Importing jobs...")
    t1 = time.time()

    # Get gsheet client
    job_gsheet = utils.init_sheet_client(
        scoped_credentials, os.environ["JOB_SHEET_ID"], os.environ["SHEET_NAME"]
    )

    so_feed = feed_parse.get_so_feed(
        "https://stackoverflow.com/jobs/feed?", payload={"r": "true"}
    )

    # Parse XML feed
    so_feed_parsed = feed_parse.parse_xml_feed(so_feed)

    # Exclude jobs already imported
    feed_deduped = feed_parse.dedupe_jobs(so_feed_parsed, job_gsheet)

    # Scrape extra items from job page
    # @TODO: bit verbose but it does the job
    for job in feed_deduped:

        extras = utils.get_so_extras(job["job_url"])

        job["company_logo"] = extras["company_logo"]
        job["salary_lower"] = extras["salary_lower"]
        job["salary_upper"] = extras["salary_upper"]
        job["salary_currency"] = extras["salary_currency"]

    # Push jobs to gDrive
    utils.push_to_gdrive(feed_deduped, job_gsheet)

    print("Finished!")
    print("Done in {}".format(time.time() - t1))
