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

        

def test_AddFixedPriceItem():  
    try:
        api = Trading(config_file=config_file, appid=appid,
                      certid=certid, devid=devid, warnings=False)

        myitem = {
            "Item": {
                "Title": "Harry Potter and the Philosopher's Stone",
                "Description": "This is the first book in the Harry Potter series. In excellent condition!",
                "PrimaryCategory": {"CategoryID": "377"},
                "StartPrice": "100",
                "CategoryMappingAllowed": "true",
                "Country": "US",
                "ConditionID": "3000",
                "Currency": "USD",
                "DispatchTimeMax": "3",
                "ListingDuration": "Days_7",
                "ListingType": "FixedPriceItem",
                "PaymentMethods": "PayPal",
                "PayPalEmailAddress": "robert.weyant@gmail.com",
                "PictureDetails": {"PictureURL": "https://upload.wikimedia.org/wikipedia/en/b/bf/Harry_Potter_and_the_Sorcerer's_Stone.jpg"},
                "PostalCode": "95125",
                "Quantity": "1",
                "ReturnPolicy": {
                    "ReturnsAcceptedOption": "ReturnsAccepted",
                    "RefundOption": "MoneyBack",
                    "ReturnsWithinOption": "Days_30",
                    "Description": "If you are not satisfied, return the book for refund.",
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

        return(api.execute('VerifyAddFixedPriceItem', myitem))
        
    except ConnectionError as e:
        print(e)
        print(e.response.dict())
        # return something?

    
def test_ReviseFixedPriceItem(ItemID,newPrice):
    print ItemID
    print newPrice
    return True

# kwargs?
def dev_AddFixedPriceItem(PrimaryCategory,
                        StartPrice,
                        Title="Harry Potter and the Philosopher's Stone",
                        Description="This is the first book in the Harry Potter series. In excellent condition!",
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
                "PrimaryCategory": {"CategoryID": str(PrimaryCategory)},
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

def dev_ReviseFixedPriceItem(ItemID,newPrice):
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
       
       

def get_ebay_item_price(itemID):
    ''' 
    searches for itemID and returns the start price.    
    '''
    try:
        api = Trading(debug=False, config_file=config_file, appid=appid,
                      certid=certid, devid=devid,warnings=False)
    
        api.execute('GetItem', {'ItemID': itemID})
        return float(api.response.reply.Item.StartPrice.value)
       
    except ConnectionError as e:
        print(e)
        print(e.response.dict())
        return False

    
def check_ebay_item_exists(itemID):
    ''' 
    True if Item exists   
    '''
    try:
        api = Trading(debug=False, config_file=config_file, appid=appid,
                      certid=certid, devid=devid,warnings=False)
        api.execute('GetItem', {'ItemID': itemID})
        return True
       
    except ConnectionError as e:
        return False
    

def update_price_history(spreadsheet,ean,price):
    ''' update price_history '''
    ws_price_history = spreadsheet.worksheet('price_history')
    num_rows = len(ws_price_history.get_all_values())
    
    ws_price_history.update_cell(num_rows+1,1,ean)
    ws_price_history.update_cell(num_rows+1,2,price)
    ws_price_history.update_cell(num_rows+1,3,mktime(localtime()))

    
def load_amazon_api(): return API(locale='us')

   
def create_ebay_listing(row_num,item,index_locations,amazon_api,spreadsheet):
    ''' create new ebay listing'''
    
    ws_summary = spreadsheet.worksheet('summary')

    try:
        print 'Creating new eBay Listing for EAN:%s' % item['ean']
        create_ebay_item_response = dev_AddFixedPriceItem(PrimaryCategory=37631,StartPrice=1000)
        itemID=create_ebay_item_response.reply.ItemID
        ws_summary.update_cell(row_num+1,index_locations['ebayid_index']+1,itemID)
        print 'Successfully created eBay Listing:%s' % (itemID)
        return create_ebay_item_response
    except:
        return False

def update_ebay_listing(item):        
    ''' update ebay listing '''
    print 'Updating eBay Listing: %s for EAN: %s' % (item['ebayID'],item['ean'])
    newEbayPrice = round(float(item['curPrice'])*1.1+2,2)
    print newEbayPrice
    
    try:
        response=dev_ReviseFixedPriceItem(ItemID=item['ebayID'],
                                           newPrice=newEbayPrice)
        print response
        return response
        
    except:
        print 'FAILURE during update'
        return False
        
def update_summary(row_num,item,index_locations,amazon_api,spreadsheet):
    ''' update google spreadsheet if amazon product changed. '''
    ws_summary = spreadsheet.worksheet('summary')
    
    large=amazon_api.item_lookup(item['ean'],ResponseGroup='Large')
    newTitle=large.Items.Item.ItemAttributes.Title
    if large.Items.Item.Offers.TotalOfferPages > 0: 
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
            
        if title_changed or price_changed:
            ws_summary.update_cell(row_num+1,index_locations['updated_index']+1,mktime(localtime()))
            ws_summary.update_cell(row_num+1,int(index_locations['count_index'])+1,int(item['curCount'])+1)
            item['curCount']+=1
    
        update_price_history(spreadsheet,item['ean'],float(newPrice))
    
        if price_changed and item['ebayID'] != '' and check_ebay_item_exists(item['ebayID']):
            update_ebay_listing(item)
        elif price_changed and not check_ebay_item_exists(item['ebayID']):
            create_ebay_listing(row_num,item,index_locations,amazon_api,spreadsheet)
    else:   pass 
        
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
        print ws_list[row_num]
        item={'ean':ws_list[row_num][index_locations['ean_index']],
              'curTitle':ws_list[row_num][index_locations['title_index']],
              'curPrice':ws_list[row_num][index_locations['price_index']],
              'curCount':ws_list[row_num][index_locations['count_index']],
              'ebayID':ws_list[row_num][index_locations['ebayid_index']]}
    
        print item['ebayID']==''
        if item['curCount'] == '': item['curCount'] = 0
        item['curCount']=int(item['curCount'])
        update_summary(row_num,item,index_locations,amazon_api,ss)
        
if __name__=='__main__':
    main()

        
        