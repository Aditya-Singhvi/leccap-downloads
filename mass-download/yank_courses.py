from datetime import date, datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
import subprocess
import os
import sys
import json


# Constants ------------------------------------------------------
LECCAP_BASE_URL = "https://leccap.engin.umich.edu"
CONFIG_FILE = "config.json"
FILENAME_ALLOWED_CHARS = (
    ".-_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
SCRIPT = """
        var callback = arguments[arguments.length - 1];
        var links = [];
        await Promise.all(recordings.map(async (lec) => {
            const res = await fetch(`https://leccap.engin.umich.edu/leccap/viewer/api/product/?rk=${lec.url.replace('/leccap/player/r/', '')}`, {"credentials": "include"});
            const data = await res.json();
            lec.url = `https:${data.mediaPrefix}${data.sitekey}/${data.info.movie_exported_name}.${data.info.movie_type}`;
            links.push({"title": lec.title, "url": lec.url, "section": lec.fileUnder, "date": lec.date})
        }));
        callback(links)
        """
# end CONSTANTS ------------------------------------------------------------


# Helper Functions ---------------------------------------------------------
def findStringContainedInValue(
    value: str, match_strs: list[str], case_sensitive=False
) -> bool:
    """
    Given a str value and a list match_strs, checks if any of the strings in
    match_strs are contained in value.

    Returns False if match_strs is empty or either argument is of NoneType.
    """
    if value is None or match_strs is None:
        return None

    if not case_sensitive:
        value = value.lower()
        match_strs = [match_str.lower() for match_str in match_strs]

    for match_str in match_strs:
        if match_s