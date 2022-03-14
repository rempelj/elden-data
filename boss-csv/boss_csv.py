import re

from bs4 import BeautifulSoup
import requests
import os
import os.path
import csv
import time

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
baseurl = "https://eldenring.wiki.fextralife.com"
max_results = 0

def writerows(rows, filename):
    rows = sorted(rows, key=lambda tup: tup[2])
    seen = []
    with open(filename, 'a', encoding='utf-8') as toWrite:
        writer = csv.writer(toWrite)
        for row in rows:
            if row in seen:
                continue
            seen.append(row)
            writer.writerow(row)


def getRows(bossurl):
    print(f"Getting boss data for {bossurl}...")
    result = []
    url = baseurl + bossurl
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    soup = BeautifulSoup(str(soup.find("div", class_="infobox")), "html.parser")
    datarows = soup.find_all("tr")

    # get boss name
    name = bossurl
    try:
        name = datarows[0].text.strip()
    except Exception as e:
        print(f"Failed to get name for {name}")
        print(e)

    # get locations
    locations = []
    try:
        locationstext = datarows[2].get_text(separator="\n")
        locations = locationstext.replace("\n", ",").split(",")
        locations = list(filter(None, locations))
        locations.remove("Location")
    except Exception as e:
        print(f"Failed to get locations for {name}")
        print(e)

    # add the first rune value found
    try:
        runeresult = re.findall("([0-9]+,?[0-9]+)", soup.text)
        runestr = runeresult[0].replace(',', '')
        runes = int(runestr)
        result.append([url, name, runes, locations[0]])
    except Exception as e:
        print(f"Failed to find runes for {name}")
        print(e)

    # try to add all locations
    for location in locations:
        try:
            runeresult = re.findall(f"{location.strip()}*.\s*([0-9]+,?[0-9]+)", datarows[3].get_text() + datarows[4].get_text())
            runestr = runeresult[0].replace(',', '')
            runes = int(runestr)
            result.append([url, name, runes, location])
        except Exception as e:
            print(f"Skipping runes for {name} in Location '{location}'")
            print(e)

    return result


def geturls():
    print("Gathering boss urls...")
    result = []
    url = baseurl + "/Bosses"
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
    soup = BeautifulSoup(response.text, "html.parser")
    soup = BeautifulSoup(str(soup.find("div", class_="tabcontent 0-tab tabcurrent")), "html.parser")
    bosses = soup.find_all("a", class_="wiki_link", href=True)
    for boss in bosses:
        result.append(boss['href'])
        print(boss['href'])
    return result


if __name__ == "__main__":
    filename = "bosses.csv"
    if os.path.exists(filename):
        os.remove(filename)
    urls = geturls()
    rows = []
    i = 0
    for url in urls:
        time.sleep(1)
        rows += getRows(url)
        i += 1
        if max_results > 0 and i >= max_results:
            break
    writerows(rows, filename)
