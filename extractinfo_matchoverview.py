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

def getrounds(row,statscontainer,namelookup):
    """
    Apply function, gets the number of rounds in each map (row)

    :param row: row that contains info of map
    :param statscontainer: Soup object containing the HTML page of the match's overview page
    :param namelookup: dataframe with lookups between abbreviated and full names
    :return namerounds: list of total round, half round counts for each team
    """
    # Soup of individual game and its header that displays round information 
    gamesoup = statscontainer.find("div",attrs={"class":"vm-stats-game","data-game-id":row["Map"].split('-')[-1]})
    gameheader = gamesoup.find("div",class_="vm-stats-game-header")

    namerounds = []
    # Gets round totals for both teams in a map, and round counts per half and OT if applicable 
    for team in (gameheader.find_all("div",class_="team")):
        # Get teamname and total rounds in map 
        fullname = team.find("div",class_="team-name").text.strip()
        namerounds.append(getname(fullname,namelookup,True))
        namerounds.append(team.find("div",class_="score").text.strip())

        # Finds out how many rounds each half (attack or defense). Gets OT rounds if applicable 
        for half in team.find_all("span"):
            side = half.get('class')[0].split('-')[1].strip()
            if side == 't':
                namerounds.append("Atk")
            elif side == "ct":
                namerounds.append("Def")
            else:
                namerounds.append("OT")
            namerounds.append(half.text.strip())

    # If no OT occured, then create OT entry with dummy values
    if len(namerounds) != 16:
        namerounds = namerounds[:6] + ['OT','-1'] + namerounds[6:] + ['OT','-1']
    return namerounds

def findwinner(row):
    """
    Apply function, finds winner based off round total

    :param row: row that contains info of map
    :return namerounds: string of team that won map 
    """
    return row["A:Name"] if int(row["A:Rnds"]) > int(row["B:Rnds"]) else row["B:Name"]

def get_roundhistory(soup,sidelookup,OT):
    """
    Function that produces round history for either OT or regulation

    :param soup: object of regulation or OT round history 
    :param sidelookup: Dictionary with sides in which teams started and which half
    :param OT: boolean if OT or not
    :return roundhistory
    """
    # Get round history in list (excludes linebreak in middle)
    roundhistory_list = []
    regulation_rounds=soup.find_all("div",class_="vlr-rounds-row-col")[1:13] + soup.find_all("div",class_="vlr-rounds-row-col")[14:]

    # Makes round counter
    if OT:
        count = 25
    else:
        count = 1

    # Goes through list and stores outcome for each round 
    for round in regulation_rounds:
        outcome_str = ''
        # Defense won 
        if len(round.find_all("div",class_="rnd-sq mod-win mod-t")) == 0 and len(round.find_all("img")) >0:

            outcome = round.find("div",class_="rnd-sq mod-win mod-ct")
            # If round <=12 (aka first half), add first half def team's name
            if count <= 12:
                outcome_str += sidelookup['First Half Def'] + ':'
            # If 12< round <=24 (aka second half), add second half def team's name
            elif 12 < count <= 24:
                outcome_str += sidelookup['Second Half Def'] + ':'    
            # If round >24, then OT
            else:
                # If even OT round, then second half of OT set, so add second half def team's name
                if count % 2 == 0:
                    outcome_str += sidelookup['Second Half Def'] + ':' 
                # If odd OT round, then first half of OT set, so add first half def team's name
                else:
                    outcome_str += sidelookup['First Half Def'] + ':'
            # Add def label 
            outcome_str += 'Def:'

            # Interpret VLR image of round outcome (elim, defuse, timeout, detonation)
            outcome_str += outcome.find("img").get('src').split('/')[-1].split('.')[0] if outcome is not None else 'N/A'

        # Attack won
        elif len(round.find_all("div",class_="rnd-sq mod-win mod-ct")) == 0 and len(round.find_all("img")) >0:
            outcome = round.find("div",class_="rnd-sq mod-win mod-t")
            # If round <=12 (aka first half), add first half attk team's name
            if count <= 12:
                outcome_str += sidelookup['First Half Atk'] + ':'
            # If 12< round <=24 (aka second half), add second half attk team's name
            elif 12 < count <= 24:
                outcome_str += sidelookup['Second Half Atk'] + ':' 
                # If round >24, then OT
            else:
                # If even OT round, then second half of OT set, so add second half attk team's name
                if count % 2 == 0:
                    outcome_str += sidelookup['Second Half Atk'] + ':' 
                # If odd OT round, then first half of OT set, so add first half attk team's name
                else:
                    outcome_str += sidelookup['First Half Atk'] + ':' 
            outcome_str += 'Atk:'
            # Interpret VLR image of round outcome (elim, defuse, timeout, detonation)
            outcome_str += outcome.find("img").get('src').split('/')[-1].split('.')[0] if outcome is not None else 'N/A'
        else:
            outcome_str += 'N/A'


        # Add outcome string, increment round counter
        roundhistory_list.append(outcome_str)
        count+=1

        # else:
        # # Attack won
        #     outcome = round.find("div",class_="rnd-sq mod-win mod-t")
        #     # If round <=12 (aka first half), add first half attk team's name
        #     if count <= 12:
        #         outcome_str += sidelookup['First Half Atk'] + ':'
        #     # If 12< round <=24 (aka second half), add second half attk team's name
        #     elif 12 < count <= 24:
        #         outcome_str += sidelookup['Second Half Atk'] + ':' 
        #         # If round >24, then OT
        #     else:
        #         # If even OT round, then second half of OT set, so add second half attk team's name
        #         if count % 2 == 0:
        #             outcome_str += sidelookup['Second Half Atk'] + ':' 
        #         # If odd OT round, then first half of OT set, so add first half attk team's name
        #         else:
        #             outcome_str += sidelookup['First Half Atk'] + ':' 
        #     outcome_str += 'Atk:'


    return pd.DataFrame([roundhistory_list])

def combine_roundhistory(maprow,statscontainer):
    """
    Middleman function that produces objects necessary to produce round history. A sidelookup easily tells
    which team started on which side on which half. Soup object of round history also taken. If necessary, 
    produces round history for OT and combines with regulation, otherwise just return regulation match history.

    :param maprow: Dataframe row that contains info of map
    :param statscontainer: Soup object containing the HTML page of the match's overview page
    :return roundhistory
    """
    # Stores which team started first half on defense and which on attack, vice versa for second half
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

    # Get the soup object containing the round history of a map (OT will be a second element in list, otherwise regulation stored all in one element)
    mapid = maprow['Map'].split('-')[-1]
    gamesoup = statscontainer.find("div",attrs={"class":"vm-stats-game","data-game-id":mapid})
    gamehistory = gamesoup.find("div",class_="vlr-rounds")
    gamehistory_list = gamehistory.find_all("div",class_="vlr-rounds-row")
    
    # Store Regulation match history 
    regulation = gamehistory_list[0]

    # If OT also happened in the map, find regulation and OT round history and combine
    if len(gamehistory_list) > 1:
        overtime = gamehistory_list[1]
        combo = pd.concat([get_roundhistory(regulation,sidelookup,False),get_roundhistory(overtime,sidelookup,True)],axis=1)
        combo.columns = range(combo.shape[1])
        return combo
    # Otherwise, find regulation history and return 
    else:
        return get_roundhistory(regulation,sidelookup,False)


def get_seriesinfo_maps(mapsstats_soup,namelookup,mapsplayed,bofx):
    """
    Gets information about each map of the best of X series from VLR match page overview section 
    1) Each map's: name, number, VLR ID
    2) Number of rounds won by each team and winner of map
    3) Round history: who won each round and how

    :param mapsstats_soup: Soup object containing the HTML page of the match's stat page
    :param namelookup: dataframe with lookups between abbreviated and full names
    :param mapsplayed: int showing how many maps played in series
    :param bofx: int showing best of X
    :return df: DataFrame with information on each map of the best of X series
    :return roundhist_df: DataFrame with the round history of each map
    """
    # Soup that contains row of maps
    if bofx == 3:
        maps_header = mapsstats_soup.find("div",class_="vm-stats-gamesnav noselect").contents[3:9:2]
    elif bofx == 5:
        maps_header = mapsstats_soup.find("div",class_="vm-stats-gamesnav noselect mod-long").contents[3:13:2]
        
    # 1) Gets Map name, number, and VLR ID and converts to DataFrame
    series_list = []

    for map_name in maps_header:
        eachmap_dict = [map_name.text.strip().split()[0]+'-'+map_name.text.strip().split()[1]+'-'+map_name["data-game-id"]]
        series_list.append(eachmap_dict) 

    df = pd.DataFrame(series_list,columns=['Map']).iloc[:mapsplayed]

    # Soup that contains the Overview stats tables
    statscontainer = mapsstats_soup.find("div",class_="vm-stats-container")

    # 2) Get number of rounds won by each team and figure out the winner of map
    col = [team+':'+param for team in ['A','B'] for param in ["Name","Rnds","First Half Side", "First Half Rnds","Second Half Side", "Second Half Rnds", "Overtime", "Overtime Rnds"]]
    df[col] = df.apply(getrounds,axis=1,result_type='expand',args=(statscontainer,namelookup,))
    df["Winner"] = df.apply(findwinner,axis=1)

    # 3) Get round history (who won each round and how)
    roundhist_list = []
    for ind,maprow in df.iterrows():
        roundhist = combine_roundhistory(maprow,statscontainer)
        roundhist["Map"] = maprow["Map"]
        roundhist.set_index('Map',inplace=True)
        roundhist_list.append(roundhist)

    roundhist_df = pd.concat(roundhist_list)
    roundhist_df.columns = range(1,roundhist_df.shape[1]+1)

    return df,roundhist_df




def get_team_overview(overview_oneteam_soup):
    """
    Gets information about player statistics for one team of a map in a BoX series. 

    Info: Player name, team name, agent name, acs, kills, deaths, assists, k-d, kast, adr, hs%, first kill, first death, first k-d

    Three types are stored: all (whole map), attack (player only on attack half), defense (player only on defense half)

    :param overview_oneteam_soup: Soup object containing the HTML page of the one team's overview table
    :return: DataFrame player stats for one team
    """

    # Extract header and stats table body
    oneteam_header = overview_oneteam_soup.find("thead")
    oneteam_body = overview_oneteam_soup.find("tbody").find_all("tr")
    
    # Iterates through single team and gets stats for each player
    oneteam_list= []
    for player in oneteam_body:
        player_stat_list = []
        # Get all the stats in a player row
        for stat in player.find_all("td"):
            if 'mod-stat' in stat.get('class'):
                triplet= []
                for s in stat.find("span",class_='stats-sq').find_all("span"):
                    stattext = s.text.strip()
                    if len(triplet) == 3:
                        break
                    if 'mod-vlr-deaths' in stat.get('class'):
                        if stattext.isnumeric():
                            triplet.append(stattext)
                    elif stattext != "" and stattext != '/':
                        triplet.append(stattext)
                    else:
                        triplet.append("N/A")
                player_stat_list.append(triplet)
            else:
                stattext = stat.text.strip()
                if stattext != "":
                    player_stat_list.append((stattext))

        # Regex to nicely format team name and player name
        findteamname = re.compile("[A-Za-z0-9 ]+")
        playerandteam =  re.findall(findteamname, player_stat_list[0]) 

        # Gets Agent Name
        playerandteam.append(player.find("img")['title'])

        # Combines player and team list with the rest
        player_stat_list = playerandteam + player_stat_list[1:]
        # player_stat_list[5] = player_stat_list[5][2:5]
        oneteam_list.append(player_stat_list)


    # Formats Column names
    colnames = ["Player","Team","Agent"]+[colname.text.strip() for colname in oneteam_header.find_all("th") if colname.text.strip()!=""]
    colnames[-1] = "FK +/-"
    
    # Turns list into DataFrame 
    df = pd.DataFrame(oneteam_list)
    df.columns = colnames

    # Cleans the part with numerical quantities 
    statsonly_df = df.iloc[:,3:]

    # Removes spaces
    #statsonly_df = statsonly_df.applymap(lambda row:row.strip().split('\n'))
    #statsonly_df.loc[:,"D"] = statsonly_df.apply(lambda row:row["D"][2:5],axis=1)

    # Converts each stat which is a list of 3 (whole map, attack, defense)
    all3 = []
    sides_list = ["All","Atk","Def"]

    for side_ind in np.arange(len(sides_list)):
        # Indexes into list to get respective quantity for side
        side_statsonly_df = statsonly_df.map(lambda cell: cell[side_ind])
        side_statsonly_df["Side"] = sides_list[side_ind]
        side_statsonly_df = pd.concat([df.iloc[:,:3],side_statsonly_df],axis=1)
        all3.append(side_statsonly_df)

    # Return dataframe
    return pd.concat(all3,ignore_index=True) 


def combine_teams_overview(mapsstats_soup,seriesinfo):
    """
    Gets information about player statistics of a map in a BoX series. 
    1) Uses get_team_overview() to get stats for each team.
    2) Combines the two into one dataframe for the whole map. 
    3) Iterates through rest of series until all maps have been collected and combines
    3) Creates a multiindex and outputs

    :param mapsstats_soup: Soup object containing the HTML page of the match's stat page
    :param seriesinfo: dataframe with information about each map
    :return final_df: DataFrame player stats for both teams
    """
    # Soup that contains the Overview stats tables
    statscontainer = mapsstats_soup.find("div",class_="vm-stats-container")
    
    # Iterate through series, making DF for each map 
    bo3 = []
    for ind, mapinfo in seriesinfo.iterrows():
        # Get map ID to obtain soup object of a map
        mapid = mapinfo['Map'].split('-')[-1]
        gamesoup = statscontainer.find("div",attrs={"class":"vm-stats-game","data-game-id":mapid})
        bothteams_soup  = gamesoup.find_all("table",class_="wf-table-inset mod-overview")

        # 1) Obtain stats of both teams
        team1 = get_team_overview(bothteams_soup[0])
        team2 = get_team_overview(bothteams_soup[1])

        # 2) Combine two DF into one
        bothteams_df = pd.concat([team1,team2],ignore_index=True)
        bothteams_df["Map"] = mapinfo['Map']
        bo3.append(bothteams_df)

    # 3) Combines all maps together
    final_df = pd.concat(bo3,ignore_index=True)

    # 4) Multiindex and output
    final_df = final_df.set_index(["Map","Side","Team"])
    return final_df

