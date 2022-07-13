import pandas as pd
import re
import numpy as np


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

def getrounds(row,statscontainer,nameslookup):
    gamesoup = statscontainer.find("div",attrs={"class":"vm-stats-game","data-game-id":row["Map"].split('-')[-1]})
    gameheader = gamesoup.find("div",class_="vm-stats-game-header")
    namerounds = []
    for team in (gameheader.find_all("div",class_="team")):
        fullname = team.find("div",class_="team-name").text.strip()
        namerounds.append(getname(fullname,nameslookup,True))
        namerounds.append(team.find("div",class_="score").text.strip())
        for half in team.find_all("span"):
            #print(half)
            side = half.get('class')[0].split('-')[1].strip()
            #print(side)
            if side == 't':
                namerounds.append("Atk")
            elif side == "ct":
                namerounds.append("Def")
            else:
                namerounds.append("OT")
            namerounds.append(half.text.strip())
    if len(namerounds) != 16:
        namerounds = namerounds[:6] + ['OT','-1'] + namerounds[6:] + ['OT','-1']

    return namerounds

def findwinner(row):
    return row["A:Name"] if int(row["A:Rnds"]) > int(row["B:Rnds"]) else row["B:Name"]

def get_roundhistory(soup,sidelookup,OT):
    roundhistory_list = []
    regulation_rounds=soup.find_all("div",class_="vlr-rounds-row-col")[1:13] + soup.find_all("div",class_="vlr-rounds-row-col")[14:]
    if OT:
        count = 25
    else:
        count = 1
    for round in regulation_rounds:
        outcome_str = ''
        # Defense won 
        if len(round.find_all("div",class_="rnd-sq mod-win mod-t")) == 0:

            outcome = round.find("div",class_="rnd-sq mod-win mod-ct")
            if count <= 12:
                outcome_str += sidelookup['First Half Def'] + ':'
            elif 12 < count <= 24:
                outcome_str += sidelookup['Second Half Def'] + ':'    
            else:

                if count % 2 == 0:
                    outcome_str += sidelookup['Second Half Def'] + ':' 
                else:
                    outcome_str += sidelookup['First Half Def'] + ':'
            outcome_str += 'Def:'
        else:
        # Attack won
            outcome = round.find("div",class_="rnd-sq mod-win mod-t")
            if count <= 12:
                outcome_str += sidelookup['First Half Atk'] + ':'
            elif 12 < count <= 24:
                outcome_str += sidelookup['Second Half Atk'] + ':' 
            else:

                if count % 2 == 0:
                    outcome_str += sidelookup['Second Half Atk'] + ':' 
                else:
                    outcome_str += sidelookup['First Half Atk'] + ':' 
            outcome_str += 'Atk:'

        outcome_str += outcome.find("img").get('src').split('/')[-1].split('.')[0] if outcome is not None else 'N/A'
        roundhistory_list.append(outcome_str)
        count+=1
    return pd.DataFrame([roundhistory_list])

def combine_roundhistory(maprow,statscontainer):
    sidelookup= {}
    if maprow["A:First Half Side"] == "Def":
        sidelookup['First Half Def'] = maprow["A:Name"]
        sidelookup['First Half Atk'] = maprow["B:Name"]
        sidelookup['Second Half Def'] = maprow["B:Name"]
        sidelookup['Second Half Atk'] = maprow["A:Name"]
    else:
        sidelookup['First Half Def'] = maprow["B:Name"]
        sidelookup['First Half Atk'] = maprow["A:Name"]
        sidelookup['Second Half Def'] = maprow["A:Name"]
        sidelookup['Second Half Atk'] = maprow["B:Name"]   

    mapid = maprow['Map'].split('-')[-1],
    gamesoup = statscontainer.find("div",attrs={"class":"vm-stats-game","data-game-id":mapid})
    gamehistory = gamesoup.find("div",class_="vlr-rounds")
    gamehistory_list = gamehistory.find_all("div",class_="vlr-rounds-row")
    
    regulation = gamehistory_list[0]

    if len(gamehistory_list) > 1:
        overtime = gamehistory_list[1]
        combo = pd.concat([get_roundhistory(regulation,sidelookup,False),get_roundhistory(overtime,sidelookup,True)],axis=1)
        print(combo)
        combo.columns = range(combo.shape[1])
        return combo
    return get_roundhistory(regulation,sidelookup,False)


def get_seriesinfo_maps(mapsstats_soup,nameslookup):
    # Soup that contains row of maps
    maps_header =mapsstats_soup.find("div",class_="vm-stats-gamesnav noselect")

    # Gets Map name, number, and VLR ID and converts to DataFrame
    series_list = []
    for map_name in maps_header.contents[3:9:2]:
        eachmap_dict = [map_name.text.strip().split()[0]+'-'+map_name.text.strip().split()[1]+'-'+map_name["data-game-id"]]
        series_list.append(eachmap_dict) 
    df = pd.DataFrame(series_list,columns=['Map'])

    # Soup that contains the Overview stats tables
    statscontainer = mapsstats_soup.find("div",class_="vm-stats-container")

    # Get number of rounds won by each team and figure out the winner of map
    col = [team+':'+param for team in ['A','B'] for param in ["Name","Rnds","First Half Side", "First Half Rnds","Second Half Side", "Second Half Rnds", "Overtime", "Overtime Rnds"]]

    df[col] = df.apply(getrounds,axis=1,result_type='expand',args=(statscontainer,nameslookup,))
    df["Winner"] = df.apply(findwinner,axis=1)


    roundhist_list = []
    for ind,maprow in df.iterrows():
        roundhist = combine_roundhistory(maprow,statscontainer)
        roundhist["Map"] = maprow["Map"]
        roundhist.set_index('Map',inplace=True)
        roundhist_list.append(roundhist)

        
    roundhist_df = pd.concat(roundhist_list)
    roundhist_df.columns = range(1,roundhist_df.shape[1]+1)

    #return df,roundhist_df




def extract_team_overview(overview_oneteam_soup):
    # Extract header and stats table body
    oneteam_header = overview_oneteam_soup.find("thead")
    oneteam_body = overview_oneteam_soup.find("tbody").find_all("tr")
    
    oneteam_list= []
    for player in oneteam_body:
        player_stat_list = []
        # Get all the stats in a player row
        for stat in player.find_all("td"):
            stattext = stat.text.strip()
            if stattext != "":
                player_stat_list.append((stattext))
                
        # Regex to nicely format team name and player name
        findteamname = re.compile("[A-Za-z0-9 ]+")
        playerandteam =  re.findall(findteamname, player_stat_list[0]) 
        playerandteam.append(player.find("img")['title'])
        player_stat_list = playerandteam + player_stat_list[1:]
        oneteam_list.append(player_stat_list)

    colnames = ["Player","Team","Agent"]+[colname.text.strip() for colname in oneteam_header.find_all("th") if colname.text.strip()!=""]
    colnames[-1] = "FK +/-"
    
    df = pd.DataFrame(oneteam_list)
    df.columns =  colnames

    statsonly_df = df.iloc[:,3:]
    statsonly_df = statsonly_df.applymap(lambda row:row.strip().split('\n'))
    statsonly_df.loc[:,"D"] = statsonly_df.apply(lambda row:row["D"][2:5],axis=1)
    
    all3 = []
    sides_list = ["All","Atk","Def"]
    for side_ind in np.arange(len(sides_list)):
        side_statsonly_df = statsonly_df.applymap(lambda cell: cell[side_ind])
        side_statsonly_df["Side"] = sides_list[side_ind]
        side_statsonly_df = pd.concat([df.iloc[:,:3],side_statsonly_df],axis=1)
        all3.append(side_statsonly_df)
    
    return pd.concat(all3,ignore_index=True) 


def combine_teams_overview(mapsstats_soup,seriesinfo):
    statscontainer = mapsstats_soup.find("div",class_="vm-stats-container")
    bo3 = []

    for ind, mapinfo in seriesinfo.iterrows():
        gamesoup = statscontainer.find("div",attrs={"class":"vm-stats-game","data-game-id":mapinfo["Map ID"]})
        bothteams_soup  = gamesoup.find_all("table",class_="wf-table-inset mod-overview")
        team1 = extract_team_overview(bothteams_soup[0])
        team2 = extract_team_overview(bothteams_soup[1])
        bothteams_df = pd.concat([team1,team2],ignore_index=True)
        bothteams_df["Map"] = "-".join(mapinfo.iloc[:3].values)
        bo3.append(bothteams_df)
        
    final_df = pd.concat(bo3,ignore_index=True)
    #teamlist = list(final_df.loc[:,"Team"].drop_duplicates())
    final_df = final_df.set_index(["Map","Side","Team"])
    return final_df#,teamlist

