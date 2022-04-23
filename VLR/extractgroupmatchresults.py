import pandas as pd
import numpy as np


def extract_matchresults_groups(both_groups_soup, group_name):
    """
    Helper function that creates a DataFrame capturing match results and other information of a particular VCT Group.
    Takes a soup object holding both containers and subsets it further into Group A and B. Places each match's info
    in a dictionary, and then places said dictionary into a list with all the matches

    Information list:
    - URL to VLR.gg match webpage
    - Winning, losing team
    - Match score in a tuple, sorted by winning team's map wins first

    :param both_groups_soup: soup object of container with both groups
    :param group_name: str, "A" or "B", exception handling if neither
    :return: DataFrame with match results of each group
    """

    # Checks validity of group name
    if group_name != "A" and group_name != "B":
        print("Error")

    # Subsets soup object with both groups into respective group depending on group_name parameter
    soup_list = both_groups_soup.find_all("div", class_="wf-cardzx")
    match_soup = soup_list[0] if group_name == "A" else soup_list[1]

    # Subsets individual group object into container with the list of matches in said group. Then, extracts information
    # of each match from each row in the table
    groupmatch_list = []
    for match in match_soup.find_all("a", class_="event-group-match wf-module-item"):
        # Gets Url
        url = match.get("href")

        # Finds Winner and Loser
        matchres = match.find("div", style="display: flex; justify-content: center;")
        both_set = set(matchres.find_all("div", class_=["team"]))
        winner_set = set(matchres.find_all("div", class_=["team mod-winner"]))
        loser_set = both_set - winner_set
        winner = list(winner_set)[0].text.strip()
        loser = list(loser_set)[0].text.strip()

        # Gets Score
        score_array = pd.Series(matchres.find("div", class_="score").text.split(":")).str.strip().sort_values(
            ascending=False)

        # Places information in dictionary and appends it to list
        match_dict = {"URL": url, "Winner": winner, "Loser": loser, "Score": score_array.values}
        groupmatch_list.append(match_dict)

    # Transforms list of dictionaries into DataFrame
    return pd.DataFrame(groupmatch_list)


def combine_matchresults_groups(soup):
    """
    Main function that takes in the main HTML webpage of the group and outputs a table that has the match results and
    information across both groups. Uses extract_matchresults_groups() as helper function to get information
    from each group, then combines them into one.

    :param soup: Soup object containing the HTML page of the entire group stage, contains info on both groups
    :return: DataFrame with group match results and other information
    """

    # Subset the whole soup into only the object that held both group tables
    bothtable_html = soup.find("div", class_="event-groups-container")

    # Call helper function to get a DataFrame of individual group's standings
    groupAmatches = extract_matchresults_groups(bothtable_html, "A")
    groupBmatches = extract_matchresults_groups(bothtable_html, "B")

    # Combine tables and reindex
    bothtab = pd.concat([groupAmatches, groupBmatches])
    bothtab.index = np.arange(bothtab.shape[0])

    # Export csv
    bothtab.to_csv('groupmatchresults.csv',index=False)
    return bothtab
