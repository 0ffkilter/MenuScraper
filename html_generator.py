from css import css
from scraper import get_options
from typing import Text
import os

print(os.getcwd())

dining_halls = {
    "frank": "frunk",
    "frary": "fraar",
    "oldenborg": "Borg",
    "cmc": "collibs",
    "scripps": "scrapp",
    "pitzer": "pitz",
    "mudd": "Let's go somewhere closer (Mudd)"
}


def generate_dining_hall(hall: Text):
    meals = ["Breakfast", "Brunch", "Lunch", "Dinner"]
    options = get_options(hall)

    code_begin = """
<div>
    <h2>%s</h2>
"""
    code_end = """
</div>
"""
    html = code_begin % (dining_halls[hall])
    for m in meals:
        try:
            foods = options[m]
            html = f'{html}\n<h3>{m}</h3>\n\t<ul>\n'
            for f in foods:
                html = f'{html}\n\t\t<li><a href="#">{f}</a></li>'
            html = html + "\n</ul>"
        except KeyError:
            continue
    html = f'{html}\n{code_end}'
    return html


def generate_all():
    html = css + "\n"
    for k, v in dining_halls.items():
        print(k)
        html = html + "\n" + generate_dining_hall(k)

    with open("index.html", "w+") as f:
        f.write(html)

if __name__ == "__main__":
    generate_all()