import argparse, sys
import locale
import requests
import textwrap
import re
from bs4 import BeautifulSoup
from datetime import datetime, date

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

SEP_CHAR = "#"
NB_SEB = 90
COLOR_GREEN_START = "\33[32m"
COLOR_GREEN_END = "\033[0m"
COLOR_DEFAULT_START = ""
COLOR_DEFAULT_END = ""

URL = "http://www.agricas.fr/menu-au-ria"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Host": "www.agricas.fr",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

FR_DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
FR_MONTHS = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]


def get_date(string):
    string = string.title().strip()
    string_lo = string.lower()

    # Make a dummy research to extract date field.
    day = [d.title() for d in FR_DAYS if d in string_lo]
    month = [m.title() for m in FR_MONTHS if m in string_lo]
    n_day = re.findall(r"\d{1,2}", string_lo)

    # Avoid index error if nothing is found.
    if day == []:
        day.append("")

    if n_day == []:
        n_day.append("")

    if month == []:
        month.append("")

    d_str = "{} {} {}".format(day[0], n_day[0], month[0])

    return d_str


def cast_date(d_str):
    try:
        d = datetime.strptime("{} {}".format(d_str, date.today().year), "%A %d %B %Y")
        return d
    except ValueError:
        return None


def is_date_to_display(d, today, nb_days_print):
    if (
        d is not None
        and d.day >= today.day
        and d.month >= today.month
        and d.day <= today.day + nb_days_print
    ):
        return True
    # DEBUG: Malformed dates fall here.
    # elif d is None:
    #     return True
    else:
        return False


def pprint_sep():
    print("{}".format(NB_SEB * SEP_CHAR))


def get_data():
    res = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(res.content, "lxml")

    # Extract the html field containing menu data.
    blocks = soup.find_all(class_="menuCategory")

    menu_lst = []
    count = 0
    for b in blocks:
        menu = {"date": None, "prices": [], "names": [], "side_dishes": []}
        # Parse date.
        date = b.find(class_="menuCategroyTitle")
        date = date.get_text(strip=True, separator="\n")
        date = get_date(date)

        menu["date"] = date

        # Parse prices.
        prices = b.find_all(class_="menuItemPrice")
        prices = [
            p.get_text(strip=True, separator="\n").replace(" ", "") for p in prices
        ]

        # Parse names.
        names = b.find_all(class_="menuItemName")
        names = [n.get_text(strip=True, separator="\n").title() for n in names]

        # Check.
        assert len(prices) == len(names)
        menu["prices"] = prices
        menu["names"] = names

        # Parse side dishes.
        # WARNING: since side dishes look constant for all names in a same block
        # we only keep the first entry.
        side_dishes = b.find_all(class_="menuItemDesc")
        side_dishes = (
            side_dishes[0].get_text(strip=True, separator="\n").title().split(" - ")
        )

        menu["side_dishes"] = list(set(side_dishes))
        menu_lst.append(menu)

    return menu_lst


def pprint_menu(menu, nb_days_print=1):
    d = cast_date(menu["date"])
    today = date.today()

    # Default color.
    c_start = COLOR_DEFAULT_START
    c_end = COLOR_DEFAULT_END

    # Change color if the date match today
    if d is not None and d.day == today.day and d.month == today.month:
        c_start = COLOR_GREEN_START
        c_end = COLOR_GREEN_END

    if is_date_to_display(d, today, nb_days_print):
        pprint_sep()
        print("{} {} :{}".format(c_start, menu["date"], c_end))

        if menu["names"] != [""]:
            for idx in range(len(menu["names"])):
                name = textwrap.wrap(menu["names"][idx], 80)
    
                nb_line = len(name)
                if nb_line < 2:
                    print(
                        "{}   - {:<80} {:<5} {}".format(
                            c_start, name[0], menu["prices"][idx], c_end
                        )
                    )
                else:
                    print(
                        "{}   - {:<80} {}".format(
                            c_start, name[0], c_end
                        )
                    )
                    for i in range(1, nb_line - 1):
                        print("{}     {:<80} {}".format(c_start, name[i], c_end))
                    
                    print(
                        "{}     {:<80} {:<5} {}".format(c_start, name[-1], menu["prices"][idx], c_end
                        )
                    )

        if menu["side_dishes"] != [""]:
            print("{} {} :{}".format(c_start, "Accompagnements", c_end))

            for idx in range(len(menu["side_dishes"])):
                print(
                    "{}   - {:<80} {}".format(c_start, menu["side_dishes"][idx], c_end)
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--days",
        "-d",
        help="number of extra days to display (default: 1)",
        type=int,
        default=1,
    )

    args = args = parser.parse_args()

    menu_lst = get_data()

    for menu in menu_lst:
        pprint_menu(menu, args.days)
    pprint_sep()


if __name__ == "__main__":
    main()
