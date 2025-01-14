#!/usr/bin/env python

import datetime
import logging
import os
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from utils import utils, inspector

# http://www.eeoc.gov/eeoc/oig/index.cfm
# Oldest report: 2003

# options:
#   standard since/year options for a year range to fetch from.
#
# Notes for IG's web team:
#

REPORTS_URL = "http://www.eeoc.gov/eeoc/oig/"

REPORT_PUBLISHED_MAP = {
  '2005-02-amr': datetime.datetime(2005, 1, 1),
  '2005-03-prop': datetime.datetime(2005, 9, 1),
  '2005-08-mgt': datetime.datetime(2005, 10, 27),
  'nccrep': datetime.datetime(2006, 6, 29),
}

def run(options):
  year_range = inspector.year_range(options)

  # Pull the reports
  doc = BeautifulSoup(utils.download(REPORTS_URL))
  semiannual_report_results, other_results = doc.select("table tr")[1].select("td")

  for result in semiannual_report_results.select("li"):
    report = semiannual_report_from(result, year_range, title_prefix="Semiannual Report - ")
    if report:
      inspector.save_report(report)

  for result in other_results.select("li"):
    report = report_from(result, year_range)
    if report:
      inspector.save_report(report)

def semiannual_report_from(result, year_range, title_prefix=None):
  link = result.find("a")
  report_url = urljoin(REPORTS_URL, link.get('href'))
  report_filename = report_url.split("/")[-1]
  report_id, _ = os.path.splitext(report_filename)

  published_on_text = link.text.split("-")[-1].strip()
  published_on = datetime.datetime.strptime(published_on_text, '%B %d, %Y')

  title = link.text
  if title_prefix:
    title = "{}{}".format(title_prefix, title)

  if published_on.year not in year_range:
    logging.debug("[%s] Skipping, not in requested range." % report_url)
    return

  report = {
    'inspector': "eeoc",
    'inspector_url': "http://www.eeoc.gov/eeoc/oig/",
    'agency': "eeoc",
    'agency_name': "Equal Employment Opportunity Commission",
    'report_id': report_id,
    'url': report_url,
    'title': title,
    'published_on': datetime.datetime.strftime(published_on, "%Y-%m-%d"),
  }

  return report

def report_from(result, year_range):
  link = result.find("a")
  report_url = urljoin(REPORTS_URL, link.get('href'))
  report_filename = report_url.split("/")[-1]
  report_id, _ = os.path.splitext(report_filename)

  if report_id in REPORT_PUBLISHED_MAP:
    published_on = REPORT_PUBLISHED_MAP[report_id]
  else:
    try:
      published_on_text = "-".join(re.search('\((\w+) (\d+),?\s(\d{4})\)', result.text).groups())
      published_on = datetime.datetime.strptime(published_on_text, '%B-%d-%Y')
    except AttributeError:
      try:
        published_on_text = "-".join(re.search('\((\w+)\s(\d{4})\)', result.text).groups())
        published_on = datetime.datetime.strptime(published_on_text, '%B-%Y')
      except AttributeError:
        published_on_text = "-".join(re.search('(\w+) (\d+),?\s(\d{4})', result.text).groups())
        published_on = datetime.datetime.strptime(published_on_text, '%B-%d-%Y')

  title = link.text

  if published_on.year not in year_range:
    logging.debug("[%s] Skipping, not in requested range." % report_url)
    return

  report = {
    'inspector': "eeoc",
    'inspector_url': "http://www.eeoc.gov/eeoc/oig/",
    'agency': "eeoc",
    'agency_name': "Equal Employment Opportunity Commission",
    'report_id': report_id,
    'url': report_url,
    'title': title,
    'published_on': datetime.datetime.strftime(published_on, "%Y-%m-%d"),
  }
  return report

utils.run(run) if (__name__ == "__main__") else None
