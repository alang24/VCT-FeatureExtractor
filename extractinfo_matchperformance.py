
import pandas as pd


def get_performance(mapsstats_soup,seriesinfo):
    statscontainer = mapsstats_soup.find("div",class_="vm-stats-container")
    print(statscontainer.find_all("table",attrs={"class":"wf-table-inset mod-matrix mod-normal"}))

        
    return