import datetime
import glob
import os
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

RELATIVE_DAYS = ["Today", "Yesterday"]


def has_relative_day(time_string: str) -> bool:
    for relative_term in RELATIVE_DAYS:
        if time_string.startswith(relative_term):
            return True
    return False


def has_weekday(time_string: str) -> bool:
    for relative_term in WEEKDAYS:
        if time_string.startswith(relative_term):
            return True
    return False


def has_no_year(time_string: str) -> bool:
    return True if re.search(r"^[A-Z][a-z]+ (\d{1,2})$", time_string) else False


def is_relative_time_string(time_string: str) -> bool:
    if has_weekday(time_string):
        return True
    if has_relative_day(time_string):
        return True
    if has_no_year(time_string):
        return True
    return False


def get_weekday_diff(time_string: str, reference_timestamp: datetime.date) -> datetime.timedelta:
    for relative_term in WEEKDAYS:
        if time_string.startswith(relative_term):
            return datetime.timedelta(days=reference_timestamp.weekday() - WEEKDAYS.index(relative_term))
    raise IndexError(f"time_string '{time_string}' is not in {WEEKDAYS}")


def get_relative_day_diff(time_string: str) -> datetime.timedelta:
    for relative_term in RELATIVE_DAYS:
        if time_string.startswith(relative_term):
            return datetime.timedelta(days=RELATIVE_DAYS.index(relative_term))
    raise IndexError(f"time_string '{time_string}' is not in {RELATIVE_DAYS}")


def parse_time_string(time_string: str, topic_file: str):
    if is_relative_time_string(time_string):
        reference_timestamp = parser.parse(time.ctime(os.stat(topic_file).st_ctime))
        if has_weekday(time_string):
            return reference_timestamp - get_weekday_diff(time_string, reference_timestamp)
        elif has_relative_day(time_string):
            return reference_timestamp - get_relative_day_diff(time_string)
        elif has_no_year(time_string):
            full_time_string = f"{time_string} {reference_timestamp.year}"
            return parser.parse(full_time_string)
        else:
            print(f'Unknown time_string format: "{time}"')

        return time_string
    else:
        return parser.parse(time_string)


def extract_user_time(user_time_td, topic_file: str):
    user_time_strings = [string for string in user_time_td.stripped_strings]
    assert len(user_time_strings) == 3, f"unexpected number of strings: {user_time_strings}"
    user, _, time_string = user_time_strings

    timestamp = parse_time_string(time_string, topic_file)
    # timestamp = time_string
    return user, timestamp


def extract_topic_number(tr):
    onclick = tr.attrs["onclick"]
    if "lt.talktopic_go" in onclick:
        if m := re.match(r"lt.talktopic_go\(event, '/topic/(\d+)(#n\d+)?'\)", onclick):
            topic_number = m.group(1)
        else:
            print("no topic number in talktopic_go:", onclick)
    else:
        print("no lt.talktopic_go")
    return topic_number


def parse_num_posts(num_posts_td):
    # format: 2 unread / 2
    if m := re.match(r"^(\d+)$", num_posts_td.text):
        unread, num_posts = 0, int(m.group(1))
    elif m := re.match(r"(\d+) unread / (\d+)", num_posts_td.text):
        unread, num_posts = int(m.group(1)), int(m.group(2))
    elif m := re.match(r"unread / (\d+)", num_posts_td.text):
        unread, num_posts = int(m.group(1)), int(m.group(2))
    else:
        print("num_posts_td.text:", num_posts_td.text)
    return unread, num_posts


def parse_topic_title(topic_title_td):
    return topic_title_td.text


def parse_found(topic_title):
    return True if re.search(r"\bfound\b", topic_title, re.IGNORECASE) else False


def parse_row(tr, topic_file):
    topic_number = extract_topic_number(tr)
    tds = tr.find_all("td")
    # if len(tds) != 4:
    #     for td in tds:
    #         print(td)
    #     for td in tds:
    #         print('td.text:', td.text)
    if len(tds) == 5 and "ignore" in tds[4].attrs["class"]:
        tds = tds[1:]
    topic_title_td, num_posts_td, user_time_td, _ = tds
    topic_title = parse_topic_title(topic_title_td)
    user, timestamp = extract_user_time(user_time_td, topic_file)
    unread, num_posts = parse_num_posts(num_posts_td)
    found = parse_found(topic_title)
    return {
        "topic_number": topic_number,
        "topic_title": topic_title,
        "user": user,
        "last_post_timestamp": timestamp,
        "crawl_timestamp": datetime.datetime.now().isoformat(),
        "num_posts": num_posts,
        "found": found,
    }


def read_topic_file(topic_file):
    with open(topic_file) as fh:
        soup = BeautifulSoup(fh, "lxml")
        return soup


def parse_topic_page(topic_file: str):
    soup = read_topic_file(topic_file)

    # structure of the HTML
    # body
    #   div topictable
    #     div talktabcontent
    #       table talktable
    talk_table = soup.find(id="talktable")

    thread_rows = talk_table.find_all("tr")
    # URL, timestamp, user, found, num_posts
    threads = []
    for tr in thread_rows:
        if "onclick" not in tr.attrs:
            continue
        if "pinnedtopic" in tr.attrs["class"]:
            continue
        thread_info = parse_row(tr, topic_file)
        threads.append(thread_info)
    return threads
