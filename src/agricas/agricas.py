from __future__ import annotations

import argparse
import locale
import re
from datetime import date, datetime, timedelta
from typing import Any

import requests
from bs4 import BeautifulSoup

# Set French locale
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

_URL = "http://www.agricas.fr/menu-au-ria"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Host": "www.agricas.fr",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

_PRINT_BASE_WIDTH = 100
_COLOR_START = "\33[32m"
_COLOR_END = "\033[0m"


class AgricasMenuPrinter:
    def __init__(self, url: str, headers: dict[str], print_base_width: int):
        """
        Initialize AgricasMenuPrinter.

        Parameters:
        - url (str): The URL to fetch the menu.
        - headers (dict): Headers for the HTTP request.
        - print_base_width (int): Width for printing menu items.
        """
        self.url = url
        self.headers = headers
        self.print_base_width = print_base_width

    def get_html(self) -> bytes | None:
        """
        Fetch HTML content from the specified URL.

        Returns:
        - bytes: HTML content.
        """
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching HTML: {e}")
            return None

    def parse_date(self, date_str: str, year: str) -> datetime:
        """
        Parse a date string and replace the year.

        Parameters:
        - date_str (str): The date string to parse.
        - year (int): The year to replace in the parsed date.

        Returns:
        - datetime: Parsed and formatted date.
        """
        return datetime.strptime(date_str, "%A %d %B").replace(year=year)

    def extract_menu_info(self, item) -> tuple[str, str, str]:
        """
        Extract menu information from a BeautifulSoup menu item.

        Parameters:
        - item (bs4.element.Tag): Menu item.

        Returns:
        - tuple: Menu, side, and cost information.
        """
        menu = item.find("div", class_="menuItemName").text.strip().title()
        side = item.find("div", class_="menuItemDesc").text.strip()
        cost = item.find("div", class_="menuItemPrice").text.strip()
        return menu, side, cost

    def process_menu_category(self, cat, year) -> tuple[str, dict[str, Any]] | None:
        """
        Process a menu category and extract relevant information.

        Parameters:
        - cat (bs4.element.Tag): Menu category.
        - year (int): The year to replace in the parsed date.

        Returns:
        - tuple or None: Day and menu data if successful, None otherwise.
        """
        match = re.match(
            r"(\w+)\s+(\d+\s+\w+)",
            cat.find("h3", class_="menuCategroyTitle").text.strip(),
        )

        if match:
            day_name, day_date = match.groups()
            date_obj = self.parse_date(f"{day_name} {day_date}", year)

            menus = []
            sides = set()

            for item in cat.find_all("div", class_="menuItemBox"):
                menu, side, cost = self.extract_menu_info(item)

                if menu and side and cost:
                    menus.append({"menu": menu, "cost": cost})

                if side:
                    sides.update(val.strip().lower() for val in side.split("-"))

            return date_obj.strftime("%A_%d"), {
                "date": date_obj,
                "menus": menus,
                "sides": sides,
            }
        return None

    def get_menus(self) -> dict:
        """
        Get menus from the HTML content.

        Returns:
        - dict: Menu data.
        """
        html_content = self.get_html()
        if not html_content:
            return {}

        soup = BeautifulSoup(html_content, "html.parser")
        year = datetime.now().year

        menu_per_day = {}

        for cat in soup.find_all("div", class_="menuCategory"):
            result = self.process_menu_category(
                cat,
                year,
            )

            if result:
                day, data = result
                menu_per_day[day] = data

        return menu_per_day

    def filter_menu(self, menu_per_day: dict[str], days: int) -> dict | Any:
        """
        Filter menus based on the specified number of days.

        Parameters:
        - menu_per_day (dict): Menu data.
        - days (int): Number of days to display menus for from today.

        Returns:
        - dict: Filtered menu data.
        """
        if days is not None:
            today = date.today()

            end_date = max(today, today + timedelta(days=days))

            # Check if we fall in a week-end
            if end_date.strftime("%A").lower() in ["samedi", "dimanche"]:
                end_date = max(today, today + timedelta(days=days + 2))

            menu_per_day = {
                day: data
                for day, data in menu_per_day.items()
                if today <= data["date"].date() <= end_date
            }

        return menu_per_day

    def print_menus(self, menu_per_day: dict[str]) -> None:
        """
        Print menus in a formatted way.

        Parameters:
        - menu_per_day (dict): Menu data.
        """
        for _, data in menu_per_day.items():
            is_today = date.today() == data["date"].date()
            c_s = _COLOR_START if is_today else ""
            c_e = _COLOR_END if is_today else ""

            print(f"+{'-' * self.print_base_width}+")
            print(f"{c_s} {data['date'].strftime('%a %d %B %Y').title()}{c_e}")

            for item in data["menus"]:
                menu_line = f"  - {c_s}{item['menu']:<{self.print_base_width-9}} {item['cost']}{c_e}"
                print(menu_line)

            if data["sides"]:
                print(f"{c_s} Accompagnements:{c_e}")
                for d in data["sides"]:
                    print(f"{c_s}  - {d.title()}{c_e}")

        print(f"+{'-' * self.print_base_width}+")


def main() -> None:
    parser = argparse.ArgumentParser(description="AGRICAS RIA - Menu Printer")
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        help="Number of days to display menus for from today.",
        default=0,
    )
    args = parser.parse_args()

    agricas_printer = AgricasMenuPrinter(
        url=_URL, headers=_HEADERS, print_base_width=_PRINT_BASE_WIDTH
    )

    menus = agricas_printer.get_menus()

    filtered_menus = agricas_printer.filter_menu(
        menus,
        days=max(
            0,
            args.days,
        ),
    )

    agricas_printer.print_menus(filtered_menus)


if __name__ == "__main__":
    main()
