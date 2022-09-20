import pandas as pd
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


def addpickbanstring(pickbanlist,gendf):
    """
    Convert pickban string on page header and concatenate to DF. Format: 
    1) Teams 1/2 first ban
    2) Teams 1/2 pick
    3) Teams 1/2 second ban
    4) Decider is leftover map

    :param pickbanlist: List from the Soup object of pickban string split, each element is the 7 p/b outcomes
    :param gendf: Dataframe with names,date, score
    :return: DataFarme with added p/b outcomes
    """
    cleaned_list = []
    cleaned_dict = {}
    count = 0 
    for banpick in pickbanlist[:7]:
        # Each list element formatted as follows: "Teamname ban/pick Mapname", except for decider: "Map remains"
        breakdown = banpick.strip().split(' ')

        # Get team name and map it to Team A or Team B
        teamname = breakdown[0]
        teamletter = "A" if teamname == gendf.at[0,'A:Name'] else "B"

        if len(breakdown) == 2:
            # Handles the decider map since formatted differently
            cleaned_list.append(breakdown[0].strip())
            cleaned_dict['Decider'] = breakdown[0].strip()
        else:
            if gendf.at[0,'BofX'] == 3:
                if breakdown[1] == 'pick':
                    cleaned_list.append(breakdown[-1].strip())
                    cleaned_dict[teamletter+':Pick'] = breakdown[-1].strip()
                else:
                    if count <= 1:
                        cleaned_dict[teamletter+':Ban 1'] = breakdown[-1].strip()
                    else:
                        cleaned_dict[teamletter+':Ban 2'] = breakdown[-1].strip()
            elif gendf.at[0,'BofX'] == 5:
                #print(count)
                if breakdown[1] == 'ban':
                    cleaned_list.append(breakdown[-1].strip())
                    cleaned_dict[teamletter+':Ban'] = breakdown[-1].strip()
                else:
                    if count <= 3:
                        cleaned_dict[teamletter+':Pick 1'] = breakdown[-1].strip()
                    else:
                        cleaned_dict[teamletter+':Pick 2'] = breakdown[-1].strip()
        count += 1

    # Convert dictionary into dataframe and concatenate to DF
    pickban_df = pd.DataFrame([cleaned_dict])
    return pd.concat((gendf,pickban_df),axis=1)


def get_seriesinfo_gen(matchheadersoup,namelookup): 
    """
    Gets information about best of X series from VLR match page header
    1) Match Date
    2) Team names 
    3) Maps won by each team
    4) Pick ban result (two bans, two picks, two bans, leftover)

    :param matchheadersoup: Soup object containing the HTML page of the match's header
    :param namelookup: dataframe with lookups between abbreviated and full names
    :return: DataFrame with information of best of X series
    """
    # 1) Get Match Date 
    matchdate = matchheadersoup.find("div",class_="moment-tz-convert")['data-utc-ts']

    # 2) Convert Versus Header: Team1 and Team2 names
    vsstring = matchheadersoup.find("div",class_="match-header-vs")

    # Header shows team names in full, converting to abbreviated 
    team1 = getname(vsstring.find("a",class_="mod-1").find("div",class_="wf-title-med").text.strip(),namelookup,True)
    team2 = getname(vsstring.find("a",class_="mod-2").find("div",class_="wf-title-med").text.strip(),namelookup,True)

    # 3) Convert Versus Header: Team1 and Team2 scores
    score = vsstring.find("div",class_="js-spoiler")
    team1score = score.find_all("span")[0].text.strip()
    team2score = score.find_all("span")[2].text.strip()
 
    # Creating Dataframe with matchdate, team1/2, team1/2 scores
    gen_df = pd.DataFrame(np.array([[team1,team1score,team2,team2score]]))
    gen_df.columns = [team+":"+param for team in ['A','B'] for param in ['Name','Maps Won']]
    gen_df.insert(0,"Date",matchdate)

    # 4) Convert Map Pickban string: Team 1/2's Ban 1/2, Pick, Decider
    if matchheadersoup.find("div",class_="match-header-note") is not None:
        pickbanlist = matchheadersoup.find("div",class_="match-header-note").text.strip().split(';')
        bancount = 0 
        for banpick in pickbanlist[:7]:
            if banpick.strip().split(' ')[1] == 'ban':
                bancount += 1

        gen_df['BofX'] = 3 if bancount == 4 else 5
        gen_df = addpickbanstring(pickbanlist,gen_df.copy())
        #print(gen_df)
    else:
        # Exception handling for Optic vs. Rise match that had no pickban string on vlr.gg page
        gen_df["Pick/Ban"] = "No Pickban info"
    return gen_df
