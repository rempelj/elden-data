import re
import sys

from bs4 import BeautifulSoup
import requests
import os
import os.path
import csv
import time

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
baseurl = "https://eldenring.wiki.fextralife.com"

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
    souptext = soup.get_text(separator="\n")
    souptext = re.sub(r'\n\s*\n', '\n', souptext)

    # get boss name
    name = bossurl
    try:
        name = datarows[0].text.strip()
    except Exception as e:
        print(f"Failed to get name for {name}")
        print(e)

    fallbacklocation = ""
    try:
        fallbacklocation = re.findall("Location\s{0,}([a-zA-Z \-'()]+)", souptext)[0]
    except Exception as e:
        print(f"Failed to get fallback location for {name}")
        print(e)

    # get runes for each location
    print(souptext)
    matches = re.findall("([a-zA-Z \-'()]+).{0,}?\s{0,}?[^0-9,]([0-9]+,?[0-9 ]+).{0,}?\s{0,}?Runes", souptext)
    for match in matches:
        try:
            locationstr = match[0].replace("Drops", "").replace("(", "").replace(")", "").strip()
            runesstr = match[1].replace(' ', '').replace(',', '').strip()
            runes = int(runesstr)
            row = [url, name, runes, fallbacklocation if locationstr == "" else locationstr]
            result.append(row)
            print("Added " + str(row))
        except Exception as e:
            print(f"Failed to find location runes for {name} with {match}")
            print(e)

    if len(matches) == 0:
        print(f"No runes found for {name}")

    print("\n")
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
    max_results = 0
    if len(sys.argv) > 1:
        max_results = int(sys.argv[1]) # first arg is max results

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
