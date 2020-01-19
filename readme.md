# Stackoverflow remote jobs scraper

Utility to scraper remote jobs from stackoverflow.com [xml feed](""https://stackoverflowz.com/jobs/feed?"")

The script updates a Google spreadsheet with the following variables:

**TODO**: describe the variables

## Install

The scraper has been developed under Python 3.7.5
```sh
pip3 install -r requirements.txt
```

Some env variables will need to be set up:

* `JOB_SHEET_ID`: id of the Google sheet where the script should dump the listings
* `GOOGLE_AUTH_KEY`: path for the .json file with google keys.  
[Here](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html)
 info on how to get the key
* `SHEET_NAME`: name of the worksheet where upload results to

Finally run the scraper with
```python
cd stack-jobs-parser

python so_parser/__main__.py
Importing jobs...
Total jobs parsed: 504
Total jobs pushed: 4
Finished!
Done in 16.586621284484863
```