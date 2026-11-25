from jinja2 import Environment, FileSystemLoader, select_autoescape
from requests import post

from string import ascii_lowercase, ascii_uppercase
from random import randint
from pathlib import Path


JINJA_ENV = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())

HTMLIFY_API_BASE = "https://api.htmlify.me/v1"

MONTH_MAP = {
    # 0: (shortname, fullname, maxdaycount)
    1:  ("jan", "january",   31),
    2:  ("feb", "february",  29),
    3:  ("mar", "march",     31),
    4:  ("apr", "april",     30),
    5:  ("may", "may",       31),
    6:  ("jun", "june",      30),
    7:  ("jul", "july",      31),
    8:  ("aug", "august",    31),
    9:  ("sep", "september", 30),
    10: ("oct", "october",   31),
    11: ("nov", "november",  30),
    12: ("dec", "december",  31),
}

def get_month_index_by_name(month: str) -> int: # 1 based index
    month = month.casefold()
    for key in MONTH_MAP.keys():
        if month in MONTH_MAP[key]:
            return key
    return 0

def get_month_maxdays_by_index(index: int) -> int:
    if not 12 >= index >= 1:
        return 0
    return MONTH_MAP[index][2]


def sanitize_date(date_input: str) -> str | None:
    """
    Sanatize date in `MM-DD` format
    accepts:
        day with or without ziro prefix
        month with or without ziro prefix
        mmm format months, case insansitive
        full name of months, case insansitive
    """

    if "-" not in date_input:
        return None

    if len(date_input) < 3:
        return None

    month, day = date_input.split("-")

    try:
        day = int(day)
    except:
        return None

    if month.isnumeric():
        month = int(month)
    else:
        month = get_month_index_by_name(month)
    
    if not 12 >= month >= 1:
        return None

    max_month_days = get_month_maxdays_by_index(month)
    if not max_month_days >= day >= 1:
        return None

    return f"{str(month).zfill(2)}-{str(day).zfill(2)}"


def sanitize_name(name_input: str) -> str | None:
    """
    Validate and Sanatize name
    name should be:
        1 to 4 word long
        word can only contents alphabates
        word can't be shorten then 3 letters
        at most 255 characters
    """

    name_input = name_input.replace("\'", "")
    name_input = name_input.replace("\"", "")
    name_input = name_input.strip()
    while "  " in name_input:
        name_input = name_input.replace("  ", " ")

    words = name_input.split(" ")
    if not 4 >= len(words) >= 1:
        return None

    allowed_ascii = set(ascii_lowercase + ascii_uppercase)
    for word in words:
        if len(word) < 3:
            return None
        if not set(word) <= allowed_ascii:
            return None

    name = " ".join(words)
    if len(name) > 255:
        return None

    return name


def sanitize_id(id_input: str) -> int | None:
    if not id_input.isnumeric():
        return None
    return int(id_input)


def render_template(template_name: str, **kwargs) -> str:
    """Render template, return rendered template as string"""
    template = JINJA_ENV.get_template(template_name)
    return template.render(**kwargs)


def generate_template(template_name: str, **kwargs) -> Path:
    """Generate template in a file and return file's path"""
    rendered_template = render_template(template_name, **kwargs)
    rfile_path = Path("generated").joinpath(str(randint(10**9,10**10-1))+"."+template_name)
    with open(rfile_path, "w") as f:
        f.write(rendered_template)
    return rfile_path


def htmlify_tmpfile(filepath: str | Path) -> str:
    """Uploads file on `filepath` to HTMLify as temp file, returns public url"""

    tmpfile_api_endpoint = HTMLIFY_API_BASE + "/tmpfiles"

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError()

    file = open(filepath, "rb")
    payload = {
        'name': file.name,
    }
    files = {"file": (file.name, file)}

    try:
        r = post(tmpfile_api_endpoint, data=payload, files=files)
        return r.json()["url"]
    except:
        return ""

