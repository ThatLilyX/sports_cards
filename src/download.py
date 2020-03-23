import argparse
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import requests
import logging

SEARCH_EBAY = r"https://www.ebay.com/sch/i.html?_from=R40&_sacat=0&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_stpos=07014&_sop=13&_dmd=1&LH_Complete=1&_fosrp=1&"
Logger = logging.getLogger(__name__)

def get_url(pageNum: int, auction: bool = True, keywords: str = r"prizm+silver+psa10+basketball") -> str:
    if auction:
        insert_mode = r"LH_Auction=1"
    else:
        insert_mode = r"LH_BIN=1"

    url_partA = SEARCH_EBAY + insert_mode + "&_nkw=" + keywords
    url_partB = r"&_pgn=" + str(pageNum) + "&_skc=" + str(50*(pageNum-1)) + "&rt=nc"
    url_partC = r"&_sacat=0"
    
    if pageNum == 1:
        url = url_partA + url_partC
    else:
        url = url_partA + url_partB
    return url

def download_data(requested_pages, auction=True, keywords=r"prizm+silver+psa10+basketball"):
    data = defaultdict(list)
    for pageNum in range(1, requested_pages):
        url = get_url(pageNum, auction=auction, keywords=keywords)
        logging.info(r"Requesting URL: " + url)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        items = soup.findAll(class_='sresult lvresult clearfix li')
        logging.info(r"Number of items on page "+str(pageNum)+r": "+str(len(items)))
        
        for item in items:
            title = item.find(class_='lvtitle').find(class_='vip').contents[0]
            item_url = item.find(class_='lvtitle').find(class_='vip')['href']
            
            if auction:
                time = item.find(class_='tme').contents[1].contents[0]
                bids = item.find(class_='lvformat').contents[1].contents[0]
                bids = int(bids.split(" ")[0])
                price = item.find(class_='lvprice prc').find(class_="bold bidsold").contents[0]
                price = float(str(price).replace("$", "").replace(",", ""))
            else:
                bids = "N/A"
                logging.info(r"Redirected to subpage: " + item_url)
                item_page = requests.get(item_url)
                item_soup = BeautifulSoup(item_page.text, 'html.parser')
                
                try:
                    time = item_soup.find(id="bb_tlft").contents[0].replace(r"/n", "").replace(r"/t", "")
                except AttributeError:
                    logging.exception(r"Cannot find timestamp for URL: " + item_url)
                    time = "N/A"

                price_finder = item.find(class_='lvprice prc').find(class_="bold bidsold")
                try:
                    price_finder = price_finder.find(class_="sboffer")
                except AttributeError:
                    logging.warning(r"class 'sboffer' is not found for URL: " + url)
                price = price_finder.contents[0]
                price = float(str(price).replace("$", "").replace(",", ""))
            
            data["Timestamp"].append(time)
            data["Title"].append(title)
            data["URL"].append(item_url)
            data["Price"].append(price)
            data["Bids"].append(bids)
    
    return pd.DataFrame(data).set_index("Timestamp")

if __name__ == "__main__":
    pass