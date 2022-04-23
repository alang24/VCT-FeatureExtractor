import requests
from bs4 import BeautifulSoup

from FeatureExtraction.extractgroupstandings import combine_groupstandings
from FeatureExtraction.extractgroupmatchresults import combine_matchresults_groups


if __name__ == "__main__":
    url = "https://www.vlr.gg/event/799/champions-tour-north-america-stage-1-challengers/group-stage"
    #url= "https://www.vlr.gg/event/854/champions-tour-stage-1-emea-challengers/group-stage"
    result = requests.get(url)
    soupparser = BeautifulSoup(result.text,'lxml')
    combine_groupstandings(soupparser)
    combine_matchresults_groups(soupparser)
