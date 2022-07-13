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

def getname(val,nameslookup,fulltoabbrev):
    """
    Takes in lookup table of team names and converts an abbreviated name to full or vice versa. (ex. SEN--->Sentinels)
    VLR has both types of names and uses them in different locations. 

    :param val: String of team name 
    :param nameslookup: dataframe with lookups between abbreviated and full names
    :param fulltoabbrev: boolean value, true if need to convert from full to abbreviated name, false if opposite

    :return: converted name
    """
    if fulltoabbrev:
        
        return nameslookup.loc[nameslookup["Full Name"]==val,'Abbrev Name'].iat[0]
    else:
        return nameslookup.loc[nameslookup["Abbrev Name"]==val,'Full Name'].iat[0]

seriesinfo_mapslist = []
overviewlist= []
for i in ['test.html','test2.html','test3.html']:
    #print(i)
    with open(i, "r", encoding='utf-8') as file:
        soupparser = BeautifulSoup(file,"lxml")

    # Lookup table between teams' abbreviated and full names on VLR
    nameslookup = pd.read_csv('nateamnames.txt')


    # Extract information of Bo3 from header
    # match_header_soup = soupparser.find("div",class_="wf-card match-header")
    # seriesinfo_gen=get_seriesinfo_gen(match_header_soup,nameslookup.copy())
    # matchstr=''.join(seriesinfo_gen.loc[0,'Date'][:10].split('-')) + '-'
    # matchstr += seriesinfo_gen.loc[0,'A:Name'] + '-' + seriesinfo_gen.loc[0,'B:Name']
    # seriesinfo_gen['Match'] = matchstr
    # seriesinfo_gen = seriesinfo_gen.set_index('Match')
    # print(seriesinfo_gen)


    maps_stats_soup = soupparser.find("div",class_="vm-stats")
    get_seriesinfo_maps(maps_stats_soup,nameslookup)
    #seriesinfo_maps,seriesinfo_rndhist = 
   # seriesinfo_maps = pd.concat([seriesinfo_maps],keys=[matchstr],names=['Match'])


    # overview=combine_teams_overview(maps_stats_soup,seriesinfo_maps)
    # overview = pd.concat([overview], keys=[matchstr], names=['Match'])
    # seriesinfo_mapslist.append(seriesinfo_maps)
    # overviewlist.append(overview)
    break
# print('end')
# seriesinfo_df=pd.concat(seriesinfo_mapslist)
# seriesinfo_df = seriesinfo_df.reset_index(level=1,drop=True)
# overview_df = pd.concat(overviewlist)
# print(seriesinfo_df)
# print(overview_df)