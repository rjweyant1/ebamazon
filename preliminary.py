from amazonproduct import API
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
#from pandas import *
from numpy import arange
from time import *

from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError

# Load eBay Credentials
credentials_file='/media/roberto/Main Storage/Documents/Oauth/ebay/ebay_oauth_creds.txt'
with open(credentials_file,'r') as creds_file:
    (appid,devid,certid,config_file) = [line.strip().split(':')[1] for line in creds_file]
        
def load_listings(
    oauthfile = '/media/roberto/Main Storage/Documents/Oauth/google/API Project-c86cee112445.json',                  
    scope = ['https://spreadsheets.google.com/feeds']):
    ''' load google spreadsheet with data '''
    
    
    json_key = json.load(open(oauthfile))
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
    
    # Authorize
    gspreadclient = gspread.authorize(credentials)
    
    # Load spreadsheet
    spreadsheet = gspreadclient.open('current amazon listings')

    return (gspreadclient,spreadsheet)
       
def update_summary(row_num,item,index_locations,amazon_api,spreadsheet):
    ''' update google spreadsheet if amazon product changed. '''
    ws_summary = spreadsheet.worksheet('summary')
    
    large=amazon_api.item_lookup(item['ean'],ResponseGroup='Large')
    newTitle=large.Items.Item.ItemAttributes.Title
    newPrice=large.Items.Item.Offers.Offer.OfferListing.Price.Amount/100.
    
    print "Title: %s\nPrice: %s" % (newTitle,newPrice)
    
    title_changed = item['curTitle'] != newTitle
    price_changed = item['curPrice'] != newPrice    
    
    if title_changed:
        ws_summary.update_cell(row_num+1,index_locations['title_index']+1,newTitle)
        item['curTitle'] = newTitle
        
    if price_changed:
        ws_summary.update_cell(row_num+1,index_locations['price_index']+1,newPrice)
        item['curPrice'] = newPrice
        update_ebay_listing()
        
    if title_changed or price_changed:
        ws_summary.update_cell(row_num+1,index_locations['updated_index']+1,mktime(localtime()))
        ws_summary.update_cell(row_num+1,int(index_locations['count_index'])+1,int(item['curCount'])+1)
        item['curCount']+=1

    update_price_history(spreadsheet,item['ean'],float(newPrice))


def create_ebay_listing(Title="Harry Potter and the Philosopher's Stone",
                        Description="This is the first book in the Harry Potter series. In excellent condition!",
                        PrimaryCategory,
                        StartPrice,
                        PictureURL="https://upload.wikimedia.org/wikipedia/en/b/bf/Harry_Potter_and_the_Sorcerer's_Stone.jpg",
                        ListingDuration="GTC",
                        PayPalEmailAddress="robert.weyant@gmail.com",
                        action='VerifyAddFixedPriceItem'                        
                        ):
   
    try:
        api = Trading(config_file=config_file, appid=appid,
                      certid=certid, devid=devid, warnings=False)

        myitem = {
            "Item": {
                "Title": Title,
                "Description": Description,
                "PrimaryCategory": {"CategoryID": PrimaryCategory},
                "StartPrice": StartPrice,
                "CategoryMappingAllowed": "true",
                "Country": "US",
                "ConditionID": "1000",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": ListingDuration,
                "ListingType": "FixedPriceItem",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": PayPalEmailAddress,
                "PictureDetails": {"PictureURL": PictureURL},
                "PostalCode": "48105",
                "Quantity": "1",
                "ReturnPolicy": {
                    "ReturnsAcceptedOption": "ReturnsAccepted",
                    "RefundOption": "MoneyBack",
                    "ReturnsWithinOption": "Days_30",
                    "Description": "If you are not satisfied, return the item for a refund.",
                    "ShippingCostPaidByOption": "Buyer"
                },
                "ShippingDetails": {
                    "ShippingType": "Flat",
                    "ShippingServiceOptions": {
                        "ShippingServicePriority": "1",
                        "ShippingService": "UPS3rdDay",
                        "ShippingServiceCost": "2.50"
                    }
                },
                "Site": "US"
            }
        }

        return(api.execute(action, myitem))
        #dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())
       
def update_ebay_listing(ItemID,newPrice):
    ''' change ebay listing if price changed '''    
       
    try:
        api = Trading(config_file=config_file, appid=appid,
                      certid=certid, devid=devid, warnings=False)

        myitem = {
            "Item": {
                "ItemID": str(ItemID),
                "StartPrice": str(newPrice)
                
            }
        }

        return(api.execute('ReviseFixedPriceItem', myitem))
        
    except ConnectionError as e:
        print(e)
        print(e.response.dict())

    return True
       
def update_price_history(spreadsheet,ean,price):
    ''' update price_history '''
    ws_price_history = spreadsheet.worksheet('price_history')
    num_rows = len(ws_price_history.get_all_values())
    
    ws_price_history.update_cell(num_rows+1,1,ean)
    ws_price_history.update_cell(num_rows+1,2,price)
    ws_price_history.update_cell(num_rows+1,3,mktime(localtime()))


    
def load_amazon_api(): return API(locale='us')

def main():            
    (gc,ss) = load_listings()
    ws_summary = ss.worksheet('summary')
    
    ws_list=ws_summary.get_all_values()
    
    amazon_api=load_amazon_api()
    
    index_locations={   'ean_index': ws_list[0].index('EAN'),
                        'title_index': ws_list[0].index('Title'),
                        'price_index': ws_list[0].index('Price'),
                        'count_index': ws_list[0].index('Times Updated'),
                        'updated_index':ws_list[0].index('Last Updated'),
                        'ebayid_index':ws_list[0].index('eBay ID')}
    
    for row_num in arange(1,len(ws_list)):
        item={'ean':ws_list[row_num][index_locations['ean_index']],
              'curTitle':ws_list[row_num][index_locations['title_index']],
              'curPrice':float(ws_list[row_num][index_locations['price_index']]),
              'curCount':int(ws_list[row_num][index_locations['count_index']])}
    
        if item['curCount'] == '': item['curCount'] = 0
        update_summary(row_num,item,index_locations,amazon_api,ss)
        
if __name__=='__main__':
    main()

        
        