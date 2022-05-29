def lookupteamname(name,namelookup):
    return namelookup.loc[namelookup["Full Name"]==name,'Abbrev Name'].iat[0]

def cleanpickbanstring(pickbanlist,teamlist):
    # Dict Comprehension for Nested Dict: Outer keys are teams and Inner Keys are Pick/Bans
    pickban_dict = {outer_k: {
            inner_k: [] if inner_k == "Ban" else ''
            for inner_k in ["Ban","Pick"]
        } 
        for outer_k in teamlist}

    # First pass to store picks and bans into dictionary
    for banpick in pickbanlist:
        breakdown = banpick.strip().split(' ')
        if len(breakdown) == 2:
            pickban_dict['Decider'] = breakdown[0]
        elif len(breakdown) == 3:
            if breakdown[1] == "ban":
                pickban_dict[breakdown[0]]["Ban"].append(breakdown[2])
            elif breakdown[1] == 'pick':
                pickban_dict[breakdown[0]]["Pick"] += breakdown[2]

    # Second Pass that turns list of two bans into separate entries Ban 1/2
    for team in pickban_dict:
        if type(pickban_dict[team]) is dict:
            temp = pickban_dict[team].pop("Ban")
            pickban_dict[team]["Ban 1"] = temp[0] 
            pickban_dict[team]["Ban 2"] = temp[1]
    return pickban_dict


def get_seriesinfo_gen(matchheadersoup,namelookup):  
    gen_dict = {}  

    # Store Match Date 
    matchdate = matchheadersoup.find("div",class_="moment-tz-convert")['data-utc-ts']
    gen_dict['Date'] = matchdate
    # Convert Versus Header: Team1 and Team2 and respective scores
    vsstring = matchheadersoup.find("div",class_="match-header-vs")
    team1 = vsstring.find("a",class_="mod-1").find("div",class_="wf-title-med").text.strip()
    team2 = vsstring.find("a",class_="mod-2").find("div",class_="wf-title-med").text.strip()
    score = vsstring.find("div",class_="js-spoiler")
    team1score = score.find_all("span")[0].text.strip()
    team2score = score.find_all("span")[2].text.strip()
    gen_dict["Score"] = {team1:team1score,team2:team2score}

    # Convert Map Pickban string: Team 1/2's Ban 1/2, Pick, Decider
    pickbanlist = matchheadersoup.find("div",class_="match-header-note").text.strip().split(';')
    teamlist = [lookupteamname(team1,namelookup),lookupteamname(team2,namelookup)]
    gen_dict["Pick/Ban"] = cleanpickbanstring(pickbanlist,teamlist)
    return gen_dict
