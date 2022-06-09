import requests
from bs4 import BeautifulSoup
import pandas as pd
from extractgroupstandings import combine_groupstandings
from extractgroupmatchresults import combine_matchresults_groups


if __name__ == "__main__":
    stage = input("Stage (1 or 2): ")
    region = input("Region (NA or EU): ")
    urllookup = pd.read_csv('urllookup.txt')
    url = urllookup.loc['Stage'+stage,region.upper()]
    result = requests.get(url)
    soupparser = BeautifulSoup(result.text,'lxml')
    combine_groupstandings(soupparser,region,stage)
    combine_matchresults_groups(soupparser,region,stage)
