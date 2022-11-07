import requests
from bs4 import BeautifulSoup


ebayUrl = "https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw=20kg+weight+plates&_in_kw=1&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&_samilow=&_samihi=&_sadis=15&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1&_sop=13&_dmd=1&_ipg=60&LH_Complete="
r= requests.get(ebayUrl)
data=r.text
soup=BeautifulSoup(data, 'html.parser')

listings = soup.find_all(class_='s-item__title')

print(listings)
"""
    for listing in listings:
        prod_name=" "
        prod_price = " "
        for name in listing.find_all('h3', attrs={'class':"s-item__title"}):
            if(str(name.find(text=True, recursive=False))!="None"):
                prod_name=str(name.find(text=True, recursive=False))
                item_name.append(prod_name)

        if(prod_name!=" "):
            price = listing.find('span', attrs={'class':"s-item__price"})
            prod_price = str(price.find(text=True, recursive=False))
            #prod_price = int(sub(",","",prod_price.split("GBP")[1].split(".")[0]))
            prices.append(prod_price)

print(item_name)
print(prices)
"""
