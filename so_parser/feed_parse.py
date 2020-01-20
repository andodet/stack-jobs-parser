from datetime import datetime as dt
from xml.etree import ElementTree as etree
import requests
import sys

import utils


def get_so_feed(url, payload):
    """
    Download XML for stackoverflow.com remote jobs

    Args:
        url (str): url for XML feed
        payload (dict): payload with additional request arguments

    Returns:
        XML object
    """
    try:
        so_feed = requests.get(url, params=payload).text
    except requests.exceptions as e:
        print(e)
        sys.exit()

    return so_feed


def parse_xml_feed(xml_feed):
    """
    Parses XML feed into a list of dictionaries

    Args:
        xml_feed (str): xml_feed blob

    Returns:
        list: a list of dicts (one dict each job listing)
    """

    root = etree.fromstring(xml_feed)
    items = root.findall("channel/item")

    so_listings = []
    for i, e in enumerate(items):
        job_dict = {
            "job_id": e.findtext("guid"),
            "title": e.findtext("title"),
            "job_url": e.findtext("link"),
            "author": e.findtext(
                """{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name"""
            ),
            "description": e.findtext("description"),
            "published_at": str(
                dt.strptime(e.findtext("pubDate").strip(), "%a, %d %b %Y %H:%M:%S Z")
            ),
            "updated_at": str(
                dt.strptime(
                    e.findtext("{http://www.w3.org/2005/Atom}updated").strip(),
                    "%Y-%m-%dT%H:%M:%SZ",
                )
            ),
            "imported_on": str(dt.today().strftime("%Y-%m-%d %H:%M:%S")),
            "categories": str([c.text for c in e.findall("category")]),
            "id": None,
            "salary_lower": None,
            "salary_upper": None,
            "salary_currency": None,
            "company_logo": None,
        }

        job_dict["id"] = utils.get_job_id(job_dict)  # generate unique ID
        so_listings.append(job_dict)

    print("Total jobs parsed: {}".format(len(so_listings)))
    return so_listings


def dedupe_jobs(job_list, job_sheet):
    """
    Removes jobs already imported from job_list

    Args:
        job_list (list): a list containing job entry dicts as returned by
            `parse_xml_feed`.
        job_sheet: google sheet client session

    Returns:
        list: a list containing new jobs.
    """

    db_jobs = job_sheet.col_values(10)

    deduped_jobs = []

    for job in job_list:
        if job.get("id") not in db_jobs:
            deduped_jobs.append(job)

    return deduped_jobs
