__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from paks.logger import logger
import requests
import os


API_VERSION = "v3"
BASE = "https://api.github.com"

# URLs
# REPO_URL = "%s/repos/%s" % (BASE, PR_REPO)
# ISSUE_URL = "%s/issues" % REPO_URL
# PULLS_URL = "%s/pulls" % REPO_URL

class GitHub:
    def __init__(self, token=None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.init_headers()

    def init_headers(self):
        self.headers = {"Accept": "application/vnd.github.%s+json;application/vnd.github.antiope-preview+json;application/vnd.github.shadow-cat-preview+json" % API_VERSION}
        if self.token:
            self.headers["Authorization"] = "token %s" % self.token
        
    def get_org_packages(self, org):
        return self.get("/orgs/%s/packages" % org) 

    def get(self, url):
        response = requests.get(BASE + url, headers=headers)
        if response.status_code != 200:
            logger.exit("Failed request to %s: %s" %(url, response.json()))
