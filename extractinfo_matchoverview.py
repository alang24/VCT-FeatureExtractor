import pandas as pd
import re
import numpy as np

def getrounds(row,statscontainer):
    gamesoup = statscontainer.find("div",attrs={"class":"vm-stats-game","data-game-id":row["Map ID"]})
    gameheader = gamesoup.find("div",class_="vm-stats-game-header")
    namerounds = []
    for team in (gameheader.find_all("div",class_="team")):
        namerounds.append(team.find("div",class_="team-name").text.strip())
        namerounds.append(team.find("div",class_="score").text.strip())
    return namerounds

def findwinner(row):
    return row["Team A"] if int(row["Team A Rnds"]) > int(row["Team B Rnds"]) else row["Team B"]
   
def get_seriesinfo_maps(mapsstats_soup):
    # Soup that contains row of maps
    maps_header =mapsstats_soup.find("div",class_="vm-stats-gamesnav noselect")

    # Gets Map name, number, and VLR ID and converts to DataFrame
    series_list = []
    for map_name in maps_header.contents[3:9:2]:
        eachmap_dict = {"Map No.":map_name.text.strip().split()[0],"Map Name":map_name.text.strip().split()[1],
                   "Map ID":map_name["data-game-id"]}
        series_list.append(eachmap_dict) 
    df = pd.DataFrame(series_list)

    # Soup that contains the Overview stats tables
    statscontainer = mapsstats_soup.find("div",class_="vm-stats-container")

    # Get number of rounds won by each team and figure out the winner of map
    col = ["Team A","Team A Rnds","Team B","Team B Rnds"]
    df[col] = df.apply(getrounds,axis=1,result_type='expand',args=(statscontainer,))
    df["Winner"] = df.apply(findwinner,axis=1)
    return df

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
    teamlist = list(final_df.loc[:,"Team"].drop_duplicates())
    final_df = final_df.set_index(["Side","Map","Team"])
    return final_df,teamlist

