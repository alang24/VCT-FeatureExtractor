#import requests
from bs4 import BeautifulSoup
import csv
import time
import pandas as pd
import lxml
import re
import numpy as np
from extractinfo_matchheader import get_seriesinfo_gen
from extractinfo_matchoverview import get_seriesinfo_maps, combine_teams_overview


# test = matchresults.iloc[16]
# url = "https://www.vlr.gg"+test.URL
# result = requests.get(url)
# soupparser = BeautifulSoup(result.text,'lxml')
# url
with open("test.html", "r", encoding='utf-8') as file:
    soupparser = BeautifulSoup(file,"lxml")


nameslookup = pd.read_csv('nateamnames.txt')
match_header_soup = soupparser.find("div",class_="wf-card match-header")
seriesinfo_gen=get_seriesinfo_gen(match_header_soup,nameslookup.copy())


# Portion of website with only map/stats
maps_stats_soup = soupparser.find("div",class_="vm-stats")
seriesinfo = get_seriesinfo_maps(maps_stats_soup)
print(seriesinfo)


a,b=combine_teams_overview(maps_stats_soup,seriesinfo)
