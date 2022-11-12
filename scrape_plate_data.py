import requests
from bs4 import BeautifulSoup
import pandas as pd

ebayUrl = "https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw=20kg+weight+plates&_in_kw=1&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1&_sop=13&_dmd=1&_ipg=60&LH_Complete="
r= requests.get(ebayUrl)
data=r.text
soup=BeautifulSoup(data, 'html.parser')

#listings = soup.find_all(class_='s-item__title')
#listings = soup.find_all(class_='s-item__price')

#print(listings[0])
#print(listings[1].next_element.next_element)

#class="s-item s-item__pl-on-bottom s-item--watch-at-corner"
#class="s-item s-item__pl-on-bottom"
listings = soup.find_all(class_="s-item s-item__pl-on-bottom")
#print(listings[0].find(class_='s-item__title'))

adict = {"Item Title":[], "Item Price":[]}
for each in listings:
    each_title_span = each.find(class_='s-item__title')
    each_title = each_title_span.next_element.next_element

    each_price_span = each.find(class_='s-item__price')
    each_price = each_price_span.next_element.next_element

    #specifying the £ sound to be the first character in item price ensures the html not accidentally picked up there.
    # and we don't want to remove a price without removing the item, so best to exclude the item before it's added to our lists.
    if str(each_price)[:1] == "£":
        adict['Item Title'].append(each_title)
        adict['Item Price'].append(each_price)

print(pd.DataFrame(adict))