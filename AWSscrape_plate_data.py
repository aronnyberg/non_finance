import json
import pandas as pd
import boto3
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
import time
from dateutil import parser

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

def pullDynamo():
    #pull existing data from Dynamodb
    table = dynamodb.Table('usedPlates')
    response = table.scan()
    df = pd.DataFrame(response['Items'])
    return df, df.count()[0]

#just to count to see how many listing we're expecting


def pullData():
    # pull old data
    newListingsN = 0
    dynamoOutput = pullDynamo()
    #add something to make use of this, change in N due to process
    existingListingsN = dynamoOutput[1]
    existingDataDF = dynamoOutput[0]
    # sort such that newest listing is at the bottom, to which we append newer listings
    existingDataDF.sort_values(by=['Listings Collected Number'], ascending=True, inplace=True)
    
    #dict to hold the data in
    adict = {"Item Title":[], "Item Price":[], "Listings Collected Number":[], "Sold Date":[]}
    #ebay page url, for loop adds page number
    ebayUrl = "https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw=20kg+weight+plates&_in_kw=1&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&LH_ItemCondition=4&_samilow=&_samihi=&_sadis=15&_stpos=BS313AX&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1&_sop=13&_dmd=1&_ipg=60&LH_Complete=3&_pgn="
    
    # need to catch failed url?
    toBreak = False
    pageN = 0
    
        #range can change to 1 or 2 when automatically pull
    pageUrl = ebayUrl+str(pageN)
    r= requests.get(pageUrl)
    data=r.text
    soup=BeautifulSoup(data, 'html.parser')
    listings = soup.find_all(class_="s-item s-item__pl-on-bottom")
    while toBreak == False:
        for each in listings:
            each_title_span = each.find(class_='s-item__title')
            each_title = each_title_span.next_element.next_element
            # following checks if for each listing, if that listing is already in the database
            #would be good to get a better way of seeing if each item has already been collected, this seems hacky
            #assumes newer listings are at the start of the for loop
            # matching the listing name doesn't work due to package(repeat) sellers, collect purchase id?
            #although presumably not the same issue with used barbells

            # if current listing was the last added in the database )
            #
            print(each_title)
            # if this particular listing is the same as the newest already added listing
            if each_title == existingDataDF.iloc[-1,:]['Item Title']:
                #print(existingDataDF.iloc[-1,:]['Item Title'])
            #if len(existingDataDF.loc[existingDataDF['Item Title'] == each_title]) > 0:
                toBreak = True
                break

            each_price_span = each.find(class_='s-item__price')
            each_price = each_price_span.next_element.next_element

            each_date_span = each.find(class_='s-item__title--tagblock')
            try:
                each_date = parser.parse(each_date_span.next_element.next_element[5:]).isoformat()
            except:
                # sometimes returns a None object
                pass

            #specifying the £ sound to be the first character in item price ensures the html not accidentally picked up there.
            # and we don't want to remove a price without removing the item, so best to exclude the item before it's added to our lists.
            if str(each_price)[:1] == "£":
                #existingListingsN +=1
                newListingsN += 1
                adict['Item Title'].append(each_title)
                adict['Item Price'].append(each_price)
                adict['Listings Collected Number'].append(newListingsN) 
                adict['Sold Date'].append(each_date)
            else:
                #not sure why I don't get data after some point on the 4th page tried re-writing, oh well
                pass

        pageN += 1


    #here need to make sure the last listing added (the oldest) is added first
    df = pd.DataFrame(adict)
    if df.count()[0] > 0:
        # switch around so last collected (oldest) are at the top
        df.sort_values(by=['Listings Collected Number'], ascending=False, inplace=True)
        # get the numbers the right way round
        #Doesn't this need to be + 1? No, because existingsListingsN is a count variable, ie n is 1 less than length
        df['Listings Collected Number'] = range(newListingsN) + existingListingsN 
        #and add those to the existing df so have a sequence of all listings in date order
        #df['Listings Collected Number'] = df['Listings Collected Number']+existingListingsN + 1
        # returns df of new data to be added
        print("expecting "+str(newListingsN)+" new listings to be added")
        return newListingsN, df
    else:
    # df should only list whatever it collected, ie whatever wasn't already in the csv
        newListingsN = 0
        print("expecting no new listings to be added")
        return newListingsN



def dynamoDump():
    #already called dynamo?
    #dynamodb = boto3.resource('dynamodb')
    pullDataOutput = pullData()
    if type(pullDataOutput) == tuple:
        newDF = pullDataOutput[1]
        table = dynamodb.Table('usedPlates')
        #would be better to declare this variable beforehand
        # if newDF == None not working, so will try 
        if isinstance(newDF, pd.DataFrame):
            #if newDF == None:
            #    
            #else:
            # I don't think the following catch is needed anymore, only checking dataframe (already checked created) has something in it
            if len(newDF.index) > 0:
                n2 = 0
                #print("working through here")
                try:
                    with table.batch_writer() as batch:
                        for index, row in newDF.iterrows():
                            n2 += 1
                            batch.put_item(json.loads(row.to_json(), parse_float=Decimal))
                        print("added "+str(n2) + " listing")
            
                except:
                    print("there's something wrong with the data-writing, data has been collected but it's not being included in the df")
            else:
                print("I don't think this catch is needed anymore, there's something wrong with the data-writing, data has been collected but it's not being included in the df")
        else:
            print("seems like there's new listings but not reading it")
            
    else:
        print("no new data to add " + str(pullDataOutput) + " is 0 right?")

#def lambda_handler(event, context):
#    dynamoDump()


dynamoDump()

# need to add data in dynamo