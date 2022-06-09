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
from extractinfo_matchperformance import get_performance

# test = matchresults.iloc[16]
# url = "https://www.vlr.gg"+test.URL
# result = requests.get(url)
# soupparser = BeautifulSoup(result.text,'lxml')
# url

# matchresults = pd.read_csv('st1_na_groupmatchresults.csv')
# print(matchresults)



seriesinfo_mapslist = []
overviewlist= []
for i in ['test.html','test2.html','test3.html']:
    with open(i, "r", encoding='utf-8') as file:
        soupparser = BeautifulSoup(file,"lxml")


    nameslookup = pd.read_csv('nateamnames.txt')
    match_header_soup = soupparser.find("div",class_="wf-card match-header")
    
    
    seriesinfo_gen=get_seriesinfo_gen(match_header_soup,nameslookup.copy())


    matchstr=''.join(seriesinfo_gen.loc[0,'Date'][:10].split('-')) + '-'
    matchstr += nameslookup.loc[nameslookup["Full Name"]==seriesinfo_gen.loc[0,'A:Name'],'Abbrev Name'].iat[0] + '-'
    matchstr += nameslookup.loc[nameslookup["Full Name"]==seriesinfo_gen.loc[0,'B:Name'],'Abbrev Name'].iat[0]

    seriesinfo_gen['Match'] = matchstr
    seriesinfo_gen = seriesinfo_gen.set_index('Match')

    # maps_stats_soup = soupparser.find("div",class_="vm-stats")
    # seriesinfo_maps = get_seriesinfo_maps(maps_stats_soup)
    # seriesinfo_maps = pd.concat([seriesinfo_maps],keys=[matchstr],names=['Match'])

    
    # overview=combine_teams_overview(maps_stats_soup,seriesinfo_maps)
    # overview = pd.concat([overview], keys=[matchstr], names=['Match'])
    # seriesinfo_mapslist.append(seriesinfo_maps)
    # overviewlist.append(overview)
    break

# seriesinfo_df=pd.concat(seriesinfo_mapslist)
# seriesinfo_df = seriesinfo_df.reset_index(level=1,drop=True)
# overview_df = pd.concat(overviewlist)
# print(seriesinfo_df)
