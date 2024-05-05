'''
Author: Aditya Singhvi
Date: May 04, 2024
'''

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
        if match_str in value:
            return match_str
    return None


def sanitize_filename(orig_filename: str) -> str:
    """
    Given a filename, sanitizes it to only allow POSIX-approved characters.

    POSIX-approved characters are the English letters (upper and lower), digits,
    the underscore (_), dash (-), and period (.).
    """
    if orig_filename is None:
        return ""

    def sanitize_char(c: chr) -> chr:
        if c in FILENAME_ALLOWED_CHARS:
            return c
        elif c == " ":
            return "_"
        elif c == "/":
            return "-"
        else:
            return "."

    return "".join(sanitize_char(c) for c in orig_filename)


def isAnyTimeClose(time: str, match_times: str, delta: int = 10) -> bool:
    """
    Given a time and a list of matchTimes as strs in the format '10:30 AM',
    checks whether the first time is within delta minutes of any of the
    matchTimes.
    """
    if time is None or match_times is None:
        return False

    t1 = datetime.strptime(time, "%H:%M %p")
    for match in match_times:
        try:
            t2 = datetime.strptime(match, "%H:%M %p")
            if abs(t2 - t1).seconds <= delta * 60:
                return True
        except ValueError:
            print(f"\tERROR: Time {match} formatted improperly. Ignoring.")

    return False

# End Helper Functions ------------------------------------------------------


# Primary Functions --------------------------------------------------------
def startSession() -> webdriver.Chrome:
    """
    Opens a Selenium Chrome WebDriver at leccap.engin.umich.edu/leccap and 
    prompts user to log in manually. Once login is complete, minimizes the
    window and returns the webdriver. 
    """
    chrome_options = Options()
    chrome_options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get(f"{LECCAP_BASE_URL}/leccap")

    try:
        wait = WebDriverWait(driver, timeout=180)
        wait.until(EC.title_contains("Lecture Recordings"))
    except TimeoutException:
        print("ERROR: Login timeout occured. Please restart script.")
        driver.quit()
        exit(0)

    driver.minimize_window()
    return driver


def getCourseToURLMap(driver: webdriver.Chrome, year: int, course_names: list[str]) -> dict[str, str]:
    """
    Given a Selenium Chrome webdriver, a year, and a list of course names, 
    navigates to that year of courses in the Lecture Capture system and finds
    the course page URLs for any available course that appears in course_names.

    The current session in the webdriver should be logged into Lecture Capture. 
    A course is defined as appearing in the list course_names if any of the 
    strings in course_names appear as contiguous substrings of the course's
    name (case-insensitive).
    """
    course_to_url = dict()
    try:
        driver.get(f"{LECCAP_BASE_URL}/leccap/{year}")
        WebDriverWait(driver, timeout=30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-group"))
        )
        course_list = driver.execute_script(
            "return document.getElementsByClassName('list-group')[0].children"
        )
        for course in course_list:
            course_title = course.text
            common_course_name = findStringContainedInValue(
                course_title, course_names)
            if (
                common_course_name is not None
                and common_course_name not in course_to_url
            ):
                print(
                    f"\tFound course {common_course_name} under name {course_title}.")
                course_to_url[common_course_name] = course.get_dom_attribute(
                    "href")
    except JavascriptException:
        print(f"\tNo courses found for year {year}.")

    return course_to_url


def saveLinks(
    driver: webdriver.Chrome,
    course_url: str,
    save_path: str,
    title_filters: list[str] = [],
    section_filters: list[str] = [],
    time_filters: list[str] = [],
):
    """
    Given the URL to a Lecture Capture course page, a webdriver, and sets of
    filters, saves links to all recordings that match the filters. 
    """
    course_url = f"{LECCAP_BASE_URL}{course_url}"
    print(f"\tCourse URL: {course_url}")
    print(f"\tSave Path: {save_path}")
    os.makedirs(save_path, exist_ok=True)
    driver.get(course_url)
    try:
        driver.set_script_timeout(60)
        recordings = driver.execute_async_script(SCRIPT)

        with open(f"{save_path}/links.txt", "w") as file:
            for recording in recordings:
                title = recording["title"]
                section = recording["section"]
                time = recording["date"][recording["date"].index("•") + 2:]

                if (
                    (
                        len(title_filters) == 0
                        and len(section_filters) == 0
                        and len(time_filters) == 0
                    )
                    or findStringContainedInValue(title, title_filters) is not None
                    or findStringContainedInValue(section, section_filters) is not None
                    or isAnyTimeClose(time, time_filters)
                ):
                    title = sanitize_filename(title)
                    section = sanitize_filename(section)
                    time = sanitize_filename(time)
                    url = recording["url"]
                    print(f"{section}_{title}_{time}.mp4 {url}", file=file)

        print(f"\tLinks saved for {save_path}")
    except TimeoutException:
        print(
            f"\tScript timed out trying to get links for {course_url}. Ignoring.")


def downloadVideos(save_path: str):
    """
    Given a directory save_path with a links.txt file inside, downloads
    content from all the contained URLs.

    links.txt should be created using saveLinks(), with the format as
        [name (no spaces)] [url] \n
        [name (no spaces)] [url] \n
        ...
    """
    with open(f"{save_path}/download_output.txt", "w") as file:
        process = subprocess.Popen(
            "exec xargs < links.txt -P 0 -L 1 wget -O",
            shell=True,
            cwd=save_path,
            stdout=file,
            stderr=file,
            start_new_session=True
        )
        print(
            f"\tDownloading videos at {save_path}. To kill this process, simply run:\n\t\tkill -9 -{os.getpgid(process.pid)}"
        )

# End Primary Functions ----------------------------------------------------


def main():
    driver = startSession()

    with open(f"{CONFIG_FILE}", 'r') as file:
        config = json.loads(file.read())
    start_year = config["start_year"]
    output_path = config["directory_path"]
    courses_to_yank = {k.lower(): v for k, v in config["courses"].items()}
    print(courses_to_yank)

    for year in range(start_year, date.today().year + 1):
        print(f"\n\nWorking on {year}...")
        course_to_url = getCourseToURLMap(driver, year, courses_to_yank.keys())
        for course, url in course_to_url.items():
            print(f"\nWorking on {course}...")
            path = f'{output_path}/{course.replace(" ", "")}'
            saveLinks(
                driver,
                url,
                path,
                courses_to_yank[course].get("title_filters", []),
                courses_to_yank[course].get("section_filters", []),
                courses_to_yank[course].get("time_filters", [])
            )
            downloadVideos(path)

    print("Saved links to all course recordings!\n")


if __name__ == "__main__":
    main()
