from bs4 import BeautifulSoup
import hashlib
import requests
import json
import re
import os
import time
from random import uniform

import gspread
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession


# Authenthicate to gDrive
credentials = service_account.Credentials.from_service_account_file(
    os.environ["GOOGLE_AUTH_KEY"]
)
scoped_credentials = credentials.with_scopes(["https://spreadsheets.google.com/feeds"])

ua = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
         (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


def init_sheet_client(scoped_creds, sheet_id, sheet_name):
    try:
        client = gspread.Client(auth=scoped_creds)
        client.session = AuthorizedSession(scoped_creds)
        job_sheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    except gspread.exceptions.SpreadsheetNotFound as e:
        print(e)

    return job_sheet


def get_so_extras(job_url):
    """
    Get additional information from stackoverflow.com job listing page.
    Args:
        job_url (str): url pointing at job listing's page
    Returns:
        dict: a dict containing additional info about the job
        listing and company.
    """
    # @TODO: add user-agent to better avoid traffic throttling

    extra_info = {
        "company_logo": None,
        "salary_lower": None,
        "salary_upper": None,
        "salary_currency": None,
    }

    try:
        page = requests.get(job_url, headers=ua)
        soup = BeautifulSoup(page.text, "html.parser")
    except requests.HTTPError as e:
        print(e)

    try:
        logo = soup.find("div", attrs={"class": "grid--cell bg-white fl-shrink0"}).img[
            "src"
        ]
        extra_info["company_logo"] = logo

        # Salary information
        salary = soup.find("div", attrs={"class": "mt12"}).span["title"]
        extra_info["salary_currency"] = re.match("[^\d\.\,\s]+", salary)[0]
        extra_info["salary_lower"] = re.findall("(\d+)(|\s-\s)", salary)[0][0]
        extra_info["salary_upper"] = re.findall("(\d+)(|\s-\s)", salary)[1][0]

    except Exception as e:
        pass

    time.sleep(3 * uniform(0, 1.5))  # be kind
    return extra_info


def get_job_id(job_dict):
    """
    Produce a unique id for a job entry.

    Args:
        job_dict(dict): a dict containing basic info about the job listing.
            {
                'job_id': source id definition,
                'author': company,
                'published_at': date publishing,
                'updated_at': date when the listing was updated
            }

    Returns:
    str: a unique id based on sha1 value hashing
    """

    tmp = [
        job_dict["job_id"],
        job_dict["author"],
        job_dict["published_at"],
        job_dict["updated_at"],
    ]

    job_id = hashlib.sha1(
        json.dumps(tmp, sort_keys=True, ensure_ascii=False).encode("utf8")
    ).hexdigest()

    return job_id


def push_to_gdrive(job_list, sheet):
    """
    Push list of dicts containing job listing to gSheets

    Args:
        job_list(list): a list containing dict for each job
        sheet: a gspread client connection to a Google Sheet

    Returns:
        Pushes entries to gSheet
    """
    if job_list:
        try:
            nrows_pre = len(sheet.col_values(1))
            nrows_post = nrows_pre + len(job_list)

            # Get A1:B1 format coordiantes for range
            cell_list = sheet.range(
                "{}:{}".format(
                    gspread.utils.rowcol_to_a1(nrows_pre + 1, 1),
                    gspread.utils.rowcol_to_a1(nrows_post, sheet.col_count),
                )
            )

            # Get list of elements to push
            to_push = []
            [[to_push.append(v) for k, v in d.items()] for d in job_list]

            for i, val in enumerate(to_push):
                cell_list[i].value = val

            sheet.update_cells(cell_list)
            print("Total jobs pushed: {}".format(len(job_list)))

        except gspread.GSpreadException as e:
            print(e)

    else:
        print("No record got pushed - `job_list` is empty")
        pass
