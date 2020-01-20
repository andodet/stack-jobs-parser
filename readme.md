# Stackoverflow remote jobs scraper

Utility to scraper remote jobs from stackoverflow.com [xml feed](""https://stackoverflowz.com/jobs/feed?"")

The script updates a Google spreadsheet with the following variables:

| Name        | Type | Description                                             |
| ------------|:----:|:--------------------------------------------------------|
|`so_id `     |int| Job id accoringn SO taxonomy                               |
|`title`      |str| Job title                                                  |
|`job_url`    |str| Job url                                                    |
|`author`     |str| Company                                                    |
|`description`|str| Job description                                            |
|`published_at`|date| Job publishing date                                      |
|`updated_at`|date| Last update time                                           |
|`imported_on`|date| Date when the job was first imported in the spreadsheet   |
|`categories`|list| List of categories related to the job (tech, stack, etc.)  |
|`id`        |str| Unique id                                                   |
|`salary_lower`|int| Min. salary                                               |
|`salary_upper`|int| Max. salary                                               |
|`salary_currency`|str| Currency denomination for salary                       |
|`company_logo`|str| Url for company logo     

## Steps

The parser will go through the following steps:

1. Grab stackoverflow [XML feed](https://stackoverflow.com/jobs/feed?r=true) for remote jobs
2. Parse it
3. Deduplicate jobs to import (vs. job list on gDrive)
4. Grab extra info (salary range, company logo, etc) from job page via `bs4` and `requests`.
5. Pushes new entries to Google Sheets

## Install

The scraper has been developed under Python 3.7.5
```
$ git clone git@github.com:andodet/stack-jobs-parser.git

$ cd stack-job-parser
$ pip3 install -r requirements.txt
```

Some env variables will need to be set up:

* `JOB_SHEET_ID`: id of the Google sheet where the script should dump the listings
* `GOOGLE_AUTH_KEY`: path for the .json file with google keys. [Here](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html)
on how to get the json key.  
In case of deployment on gcp this will be used to indentify the key file ina a storage bucket.
* `SHEET_NAME`: name of the worksheet where upload results to

Finally run the parser with:
```python
$ cd so_parser
$ python main.py

Importing jobs...
Total jobs parsed: 504
Total jobs pushed: 4
Finished!
Done in 16.586621284484863
```

## Extras

`gcloud-func` branch contains a version that can be easily deployed to [Google Cloud Function](
https://cloud.google.com/functions/) and run periodically.