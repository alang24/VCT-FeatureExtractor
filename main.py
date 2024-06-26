from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import lxml
import re
import numpy as np
from extractinfo_matchheader import get_seriesinfo_gen
from extractinfo_matchoverview import get_seriesinfo_maps, combine_teams_overview
from extractinfo_matchperformance import get_performance


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


def pulldata(urldf,labelstr):
    """
    Gets information from VLR match page

    :param urldf: DF of VLR url ends to pull information from 
    :param labelstr: results identifier (year_tier_region_stage_format)
    
    tier (champions, masters, challengers)
    form (groupstage/bracket if necessary)
    """
    seriesinfo_genlist = []
    seriesinfo_mapslist = []
    seriesinfo_rndhistlist = []
    overviewlist= []
    
    # Lookup table between teams' abbreviated and full names on VLR
    nameslookup = pd.read_csv('nateamnames.txt')

    for i in ['test12.html']:
        with open('TestFiles/'+i, "r", encoding='utf-8') as file:
            soupparser = BeautifulSoup(file,"lxml")

    for ind,dfrow in urldf.iterrows():
        print("Pulling results for match")
        # url = "https://www.vlr.gg"+ dfrow['URL']

        # result = requests.get(url)
        # soupparser = BeautifulSoup(result.text,'lxml')
 
        # 1) Extract information of Bo3 from header
        match_header_soup = soupparser.find("div",class_="match-header")
        seriesinfo_gen=get_seriesinfo_gen(match_header_soup,nameslookup.copy())
        mapsplayed = int(seriesinfo_gen.loc[0,'A:Maps Won'])+int(seriesinfo_gen.loc[0,'B:Maps Won'])

        # 2) Generate unique match string to identify a BoX series
        matchstr=''.join(seriesinfo_gen.loc[0,'Date'][:10].split('-')) + '-'
        matchstr += seriesinfo_gen.loc[0,'A:Name'] + '-' + seriesinfo_gen.loc[0,'B:Name']

        # 3) Extract information of BoX about its maps and roundhistory of each map
        maps_stats_soup = soupparser.find("div",class_="vm-stats")

        if matchstr == '20220213-OPTC-Rise':
            seriesinfo_gen['BofX'] = 3

        seriesinfo_maps,seriesinfo_rndhist = get_seriesinfo_maps(maps_stats_soup,nameslookup,mapsplayed,seriesinfo_gen.at[0,'BofX'])

        # 4) Extract player statistics in each map of series for both teams
        overview = combine_teams_overview(maps_stats_soup,seriesinfo_maps)

        # 5) Attach Match string identifier to each DF
        seriesinfo_gen['Match'] = matchstr
        seriesinfo_gen = seriesinfo_gen.set_index('Match')
        
        seriesinfo_maps= seriesinfo_maps.set_index('Map')
        seriesinfo_maps = pd.concat([seriesinfo_maps],keys=[matchstr],names=['Match'])

        #seriesinfo_rndhist= seriesinfo_rndhist.set_index('Map')
        seriesinfo_rndhist = pd.concat([seriesinfo_rndhist],keys=[matchstr],names=['Match'])

        overview = pd.concat([overview], keys=[matchstr], names=['Match'])

        # 6) Append Dataframe to list containing all the matches in the pull
        seriesinfo_genlist.append(seriesinfo_gen)
        seriesinfo_mapslist.append(seriesinfo_maps)
        seriesinfo_rndhistlist.append(seriesinfo_rndhist)
        overviewlist.append(overview)
        print("Match Info Pull Complete for:")
        print(matchstr.split('-')[1],"vs.",matchstr.split('-')[2])
        print("Waiting...")
        print(matchstr)
        break
        #time.sleep(60)
        
        
    print("All Done! Combining DataFrames...")
    # 7) Convert the list of DataFrames into a DataFrame 
    seriesinfo_gen_df = pd.concat(seriesinfo_genlist)
    seriesinfo_maps_df= pd.concat(seriesinfo_mapslist)
    seriesinfo_rndhist_df = pd.concat(seriesinfo_rndhistlist)
    overview_df = pd.concat(overviewlist)


    seriesinfo_gen_df.to_csv('Results/'+labelstr+'_seriesinfogen.csv')
    seriesinfo_maps_df.to_csv('Results/'+labelstr+'_seriesinfomaps.csv')
    seriesinfo_rndhist_df.to_csv('Results/'+labelstr+'_seriesinforndhist.csv')
    overview_df.to_csv('Results/'+labelstr+'_overview.csv')
    return 


if __name__ == "__main__":
    filename = '2022_chall_na_st2_group_matchresults.csv'
    matchresults = pd.read_csv("URL/"+filename)
    pulldata(matchresults,"c9lev")


