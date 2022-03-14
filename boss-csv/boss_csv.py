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
    seen = set()
    with open(filename, 'a', encoding='utf-8') as toWrite:
        writer = csv.writer(toWrite)
        for row in rows:
            if row[0] in seen:
                continue
            seen.add(row[0])
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
    name = bossurl
    try:
        name = datarows[0].text.strip()
    except Exception as e:
        print(f"Failed to get name for {name}")
        print(e)
    try:
        name = datarows[0].text.strip()
        runeresult = re.findall("([0-9]+,?[0-9]+)", soup.text)
        runestr = runeresult[0].replace(',', '')
        runes = int(runestr)
    except Exception as e:
        runes = 0
        print(f"Failed to get runes for {name}")
        print(e)
    result.append([url, name, runes])
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
        if max_results > 0 and i > max_results:
            break
    writerows(rows, filename)
