#!/usr/bin/env python

import datetime
import logging
import os

from bs4 import BeautifulSoup
from utils import utils, inspector

# http://www.sigtarp.gov
# Oldest report: 2009

# options:
#   standard since/year options for a year range to fetch from.
#
# Notes for IG's web team:
#

REPORT_URLS = [
  "http://www.sigtarp.gov/pages/quarterly.aspx",
  "http://www.sigtarp.gov/pages/audit.aspx",
  "http://www.sigtarp.gov/pages/auditrc.aspx",
  "http://www.sigtarp.gov/pages/engmem.aspx",
]

def run(options):
  year_range = inspector.year_range(options)

  # Pull the reports
  for report_url in REPORT_URLS:
    doc = BeautifulSoup(utils.download(report_url))
    results =  doc.select("td.mainInner div.ms-WPBody li")

    if not results:
      raise AssertionError("No results found for {}".format(report_url))

    for result in results:
      report = report_from(result, year_range)
      if report:
        inspector.save_report(report)

def report_from(result, year_range):
  result_link = result.find("a")
  title = result_link.text

  report_url = result_link.get('href')
  report_filename = report_url.split("/")[-1]
  report_id, extension = os.path.splitext(report_filename)

  published_on_text = result.select("div.custom_date")[0].text.lstrip("-")
  published_on = datetime.datetime.strptime(published_on_text, '%B %d, %Y')

  if published_on.year not in year_range:
    logging.debug("[%s] Skipping, not in requested range." % report_url)
    return

  report = {
    'inspector': 'sigtarp',
    'inspector_url': "http://www.sigtarp.gov",
    'agency': 'sigtarp',
    'agency_name': "Special Inspector General for the Troubled Asset Relief Program",
    'report_id': report_id,
    'url': report_url,
    'title': title,
    'published_on': datetime.datetime.strftime(published_on, "%Y-%m-%d"),
  }

  return report

utils.run(run) if (__name__ == "__main__") else None
