import urllib.request
import re
import os

url = "https://download.geofabrik.de/asia/india.html"
html = urllib.request.urlopen(url).read().decode('utf-8')
links = re.findall(r'href="([^"]*\.osm\.pbf)"', html)

for link in links:
    print(link)
