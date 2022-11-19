import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

#dict to hold the data in
adict = {"Item Title":[], "Item Price":[], "Unix Timestamp (collected)":[]}
#ebay page url, for loop adds page number
ebayUrl = "https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw=20kg+weight+plates&_in_kw=1&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1&_sop=13&_dmd=1&_ipg=60&LH_Complete=&_pgn="
csvPath = '~/code/non_finance/weightPlateData.csv'

existingDataDF = pd.read_csv(csvPath)
#don't think i need to catch a failed url, as failed url means we've run out of pages
toBreak = False
while toBreak == False:
    for n in range(1, 15):
        pageUrl = ebayUrl+str(n)
        r= requests.get(pageUrl)
        data=r.text
        soup=BeautifulSoup(data, 'html.parser')
        listings = soup.find_all(class_="s-item s-item__pl-on-bottom")

        for each in listings:
            each_title_span = each.find(class_='s-item__title')
            each_title = each_title_span.next_element.next_element
            #would be good to get a better way of seeing if each item has already been collected, this seems hacky
            if len(existingDataDF.loc[existingDataDF['Item Title'] == each_title]) > 0:
                toBreak = True
                break

            each_price_span = each.find(class_='s-item__price')
            each_price = each_price_span.next_element.next_element

            #specifying the £ sound to be the first character in item price ensures the html not accidentally picked up there.
            # and we don't want to remove a price without removing the item, so best to exclude the item before it's added to our lists.
            if str(each_price)[:1] == "£":
                adict['Item Title'].append(each_title)
                adict['Item Price'].append(each_price)
                adict['Unix Timestamp (collected)'].append(time.time())
            else:
                #not sure why I don't get data after some point on the 4th page tried re-writing, oh well
                pass

df = pd.DataFrame(adict)
if len(df) > 2:
    #need to merge the data sets together here
    # here print the new data to be added
    print("new data rows are:", df)

    df = df.append(existingDataDF)
    df.to_csv(csvPath)
else:
# df should only list whatever it collected, ie whatever wasn't already in the csv
    print('nothing new added')


