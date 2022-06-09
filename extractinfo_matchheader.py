import pandas as pd
import numpy as np


def lookupteamname(name,namelookup):
    return namelookup.loc[namelookup["Full Name"]==name,'Abbrev Name'].iat[0]

def cleanpickbanstring(pickbanlist):
    cleaned_list = []
    for banpick in pickbanlist:
        breakdown = banpick.strip().split(' ')
        if len(breakdown) == 2:
            cleaned_list.append(breakdown[0].strip())
        elif len(breakdown) == 3:
            cleaned_list.append(breakdown[-1].strip())
    return cleaned_list


def get_seriesinfo_gen(matchheadersoup,namelookup):  
    # Store Match Date 
    matchdate = matchheadersoup.find("div",class_="moment-tz-convert")['data-utc-ts']

    # Convert Versus Header: Team1 and Team2 and respective scores
    vsstring = matchheadersoup.find("div",class_="match-header-vs")
    team1 = vsstring.find("a",class_="mod-1").find("div",class_="wf-title-med").text.strip()
    team2 = vsstring.find("a",class_="mod-2").find("div",class_="wf-title-med").text.strip()
    score = vsstring.find("div",class_="js-spoiler")
    team1score = score.find_all("span")[0].text.strip()
    team2score = score.find_all("span")[2].text.strip()
 
    gen_df = pd.DataFrame(np.array([[team1,team1score,team2,team2score]]))
    gen_df.columns = [team+":"+param for team in ['A','B'] for param in ['Name','Rnds']]
    gen_df.insert(0,"Date",matchdate)
    # Convert Map Pickban string: Team 1/2's Ban 1/2, Pick, Decider
    if matchheadersoup.find("div",class_="match-header-note") is not None:
        pickbanlist = matchheadersoup.find("div",class_="match-header-note").text.strip().split(';')
        pickban_df = pd.DataFrame([cleanpickbanstring(pickbanlist)])
        pickban_labels = [team+":"+param for param in ['Ban 1','Pick','Ban 2'] for team in ['A','B']]
        pickban_labels.append('Decider')
        pickban_df.columns = pickban_labels
        gen_df = pd.concat((gen_df,pickban_df),axis=1)
    else:
        gen_df["Pick/Ban"] = "No Pickban info"
    return gen_df
