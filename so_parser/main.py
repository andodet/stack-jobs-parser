# Revise import order
import os
import time
import utils

import feed_parse

from google.oauth2 import service_account


# Get gAuth credentials
credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_AUTH_KEY"]
)

scoped_credentials = credentials.with_scopes(["https://spreadsheets.google.com/feeds"])


def main():

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
        job["company_listing"] = extras["company_listing"]

    # Push jobs to gDrive
    utils.push_to_gdrive(feed_deduped, job_gsheet)

    print("Finished!")
    print("Done in {} secs.".format(round(time.time() - t1, 2)))


if __name__ == "__main__":

    main()
