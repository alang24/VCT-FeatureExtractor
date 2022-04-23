import re
import numpy as np
import pandas as pd


def extract_groupstandings(both_groups_soup, group_name):
    """
    Helper function that creates a DataFrame capturing standings and other information of a particular VCT Group. Takes
    a soup object holding both containers and subsets it further into Group A and B.

    Information list:
    - Team Name
    - Wins and Losses
    - Rounds won, lost, and differential

    :param both_groups_soup: soup object of container with both groups
    :param group_name: str, "A" or "B", exception handling if neither
    :return: DataFrame of individual group
    """
    # Checks validity of group name
    if group_name != "A" and group_name != "B":
        print("Error")

    # Subsets soup object with both groups into respective group depending on group_name parameter
    soup_list = both_groups_soup.find_all("div", class_="event-group")
    group_soup = soup_list[0] if group_name == "A" else soup_list[1]

    # Subsets individual group object into the column header and the table body. Here the body is analyzed for the
    # various results, info on one team stored in a list, said list added to a list for all the teams
    results = group_soup.find("tbody")
    groupinfo_list = []
    for team in results.find_all("tr"):
        teaminfo_list = []
        # Info containing wins, losses, round for/against/differential
        for att in team.contents:
            if att.text.strip() != '':
                teaminfo_list.append(att.text.strip())

        # Special regex used for team name cell that had odd formatting
        findteamname = re.compile("[A-Za-z0-9 ]+")
        teaminfo_list[0] = re.findall(findteamname, teaminfo_list[0])[1]
        groupinfo_list.append(teaminfo_list)

    # Transform list of lists into DataFrame, with columns being information and rows being teams
    total_df = pd.DataFrame(groupinfo_list)

    # Individual group object soup's column header portion is copied to the DataFrame. Renaming, reindexing to clean
    # up the table
    total_df.columns = [label.text.strip() for label in group_soup.find_all("th")]
    total_df = total_df.rename(mapper={"Group " + group_name: "Team", "Δ": "RD"}, axis="columns")
    total_df["Group"] = "Group A" if group_name == "A" else "Group B"
    return total_df


def combine_groupstandings(soup):
    """
    Main function that takes in the main HTML webpage of the group and outputs a table that has the group standing
    results and other information from Group A and Group B. Uses make_groupstandings() as helper function to get table
    from each group, then combines them into one.

    :param soup: Soup object containing the HTML page of the entire group stage, contains info on both groups
    :return: DataFrame with group standings results and other information
    """

    # Subset the whole soup into only the object that held both group tables
    bothtable_html = soup.find("div", class_="event-groups-container")

    # Call helper function to get a DataFrame of individual group's standings
    groupAstandings = extract_groupstandings(bothtable_html, "A")
    groupBstandings = extract_groupstandings(bothtable_html, "B")

    # Combine tables and reindex
    bothtab = pd.concat([groupAstandings, groupBstandings])
    bothtab = bothtab.set_index("Team")

    # Export csv
    bothtab.to_csv('groupstandings.csv')
    return

