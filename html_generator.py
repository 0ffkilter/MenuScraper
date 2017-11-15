from css import css
from scraper import get_options
from typing import Text
import os


dining_halls = [
    ("frank","frunk"),
    ("frary", "fraar"),
    ("oldenborg", "Borg"),
    ("cmc", "collibs"),
    ("scripps", "scrapp"),
    ("pitzer", "pitz"),
    ("mudd", "Let's go somewhere closer (Mudd)")
]


def generate_dining_hall(hall: Text, name: Text):
    meals = ["Breakfast", "Brunch", "Lunch", "Dinner"]
    options = get_options(hall)

    code_begin = """
<div>
    <h2>%s</h2>
"""
    code_end = """
</div>
"""
    html = code_begin % (name)
    for m in meals:
        try:
            foods = options[m]
            html = '%s\n<h3>%s</h3>\n\t<ul>\n' % (html, m)
            for f in foods:
                html = '%s\n\t\t<li><a href="#">%s</a></li>' % (html, f)
            html = html + "\n</ul>"
        except KeyError:
            continue
    html = '%s\n%s' % (html, code_end)
    return html


def generate_all():
    html = css + "\n"
    for k, v in dining_halls
        print(k)
        html = html + "\n" + generate_dining_hall(k, v)

    with open("index.html", "w+") as f:
        f.write(html)


if __name__ == "__main__":
    generate_all()
