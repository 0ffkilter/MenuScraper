import datetime
import requests
import json
from typing import Text
import demjson
import re
from bs4 import BeautifulSoup


def get_mudd_mapping(lines: Text):
    pattern = re.compile("\['([0-9]*_[0-9]*)'\]")
    sections = lines.split("\n")
    items = {}
    for l in sections:
        item_code = pattern.search(l)
        if item_code is not None:
            item_code = item_code.groups(0)[0]
            item = "".join(l.split(",")[22:])[1:]
            item = item[0:item.find("'")]
            items[item_code] = item
    return items


def mudd(url: Text):
    raw_string = requests.get(url).text
    parts = raw_string.split("aData=new Object();")
    json_part = parts[0].split("menuData = ")

    json_string = "{ \"menuData\" : " + json_part[1].strip()[0:-1] + " }"
    options = demjson.decode(json_string)
    item_mapping = get_mudd_mapping(parts[1])
    days = options['menuData'][-1]['menus'][0]["tabs"]
    meals = {}
    for d in days:
        day = d['title']
        for g in d['groups']:
            meal = g['title']
            for c in g['category']:
                for p in c['products']:
                    try:
                        food = item_mapping[p]
                        if day not in meals:
                            meals[day] = {meal: [food]}
                        else:
                            if meal not in meals[day]:
                                meals[day][meal] = [food]
                            else:
                                meals[day][meal].append(food)
                    except KeyError:
                        continue
    return meals


def sodexo():
    index_url = 'https://scrippsdining.sodexomyway.com/dining-choices/index.html'
    resp = requests.get(index_url)
    doc = BeautifulSoup(resp.text, "lxml")
    menu_url = doc.find_all('div', {'class': 'accordionBody'})[0].find_all('a')[0]['href']
    url = 'https://scrippsdining.sodexomyway.com' + menu_url
    # The href attribute is not the full URL for some reason
    resp = requests.get(url)

    text = None
    if resp.status_code == 404:
        return None
    else:
        text = BeautifulSoup(resp.text, "lxml")

    current_day = datetime.datetime.now().strftime("%A")
    day_node = text.find(id=current_day.lower())
    items = day_node.find_all('tr')
    current_meal = ""
    meals = {current_day: {}}
    for i in items:
        try:
            current_meal = i.find_all('td', {"class":'mealname'})[0].text.capitalize()
            meals[current_day][current_meal] = []
        except IndexError:
            try:
                item = i.find('div', {'class':'menuitem'}).find('span').text
                meals[current_day][current_meal].append(item)
            except AttributeError:
                continue
    return meals



def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def bonAppetit(url: Text, number:Text):
    raw_string = requests.get(url).text
    options = json.loads(raw_string)

    item_mapping = {}
    item_blacklist = set()
    for k, v in options['items'].items():
        # print(v["label"], v["tier"])
        if int(v['tier']) < 2:

            if not v['label'] in item_blacklist:
                item_mapping[k] = v['label']
        else:
            item_blacklist.add(v['label'])
            if k in item_mapping:
                item_mapping.remove(k)

    # Preserve format with Pomona formatting
    items = {}
    day = datetime.datetime.now().strftime("%A")

    for m in options['days'][0]['cafes'][number]['dayparts'][0]:
        meal = m['label']
        cur_items = []
        for s in m['stations']:
            for i in s['items']:
                if i in item_mapping:
                    cur_items.append(item_mapping[i])
        items[meal] = cur_items

    meals = {day: items}
    return meals


def map_to_meal(location: Text):
    meal_mapping = {'C': 'Breakfast', 'D': 'Lunch', 'E': 'Dinner'}
    day = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday',
           3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

    if int(location[1:]) < 4:
        raise KeyError
    return (day[(int(location[1:]) - 1) // 10],
            meal_mapping[location[0]])


def oldenborg_map(location: Text):
    day = {'B': 'Monday', 'C': 'Tuesday', 'D': 'Wednesday', 'E': 'Thursday',
           'F': 'Friday'}
    item_range = range(5, 14)
    if int(location[1:]) in item_range:
        return (day[location[0]], 'Lunch')
    else:
        raise KeyError


def pomona(url: Text, is_oldenborg: bool=False):
    raw_string = requests.get(url).text
    options = json.loads(raw_string)
    meals = {}
    for e in options['feed']['entry']:
        cell_num = e['title']['$t']
        cell_content = e['content']['$t']
        try:
            if not is_oldenborg:
                day, meal = map_to_meal(cell_num)
            else:
                day, meal = oldenborg_map(cell_num)
        except KeyError:
            continue
        if cell_content == meal:
            continue
        if day not in meals:
            meals[day] = {meal: [cell_content]}
        else:
            if meal not in meals[day]:
                meals[day][meal] = [cell_content]
            else:
                meals[day][meal].append(cell_content)
    return meals


def get_options(dining_hall: Text):
    items = []
    if dining_hall is "oldenborg":
        items = pomona('https://spreadsheets.google.com/feeds/cells/1MQJ1eySZHZ4AM77Qcsieda7uJJBZYkAWKVwvsPz9peI/ocz/public/basic?alt=json',
                  is_oldenborg=True)
    elif dining_hall is "frank":
        items = pomona('https://spreadsheets.google.com/feeds/cells/1clbmjikIr2ZEBNkWitEX7ywOAbjtCfW8hLRZf_36AGg/och/public/values?alt=json')
    elif dining_hall is "frary":
        items = pomona('https://spreadsheets.google.com/feeds/cells/10nqbUUFuBmQty49uq7vSJzplQpdL7CHkRvLLAt6klP0/o62wyvq/public/basic?alt=json')
    elif dining_hall is "cmc":
        items = bonAppetit('http://legacy.cafebonappetit.com/api/2/menus?format=json&cafe=50&date=%s' % (get_today()), '50')
    elif dining_hall is "pitzer":
        items = bonAppetit('http://legacy.cafebonappetit.com/api/2/menus?format=json&cafe=219&date=%s' % (get_today()), '219')
    elif dining_hall is "scripps":
        items = sodexo()
    elif dining_hall is "mudd":
        items = mudd('https://hmc.sodexomyway.com/smgmenu/json/harvey%20mudd%20college%20-%20resident%20dining')
    else:
        return ""
    day = datetime.datetime.now().strftime("%A")
    return items[day]
