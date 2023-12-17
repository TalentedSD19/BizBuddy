from fastapi import FastAPI 
from fastapi import Request 
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import requests
import time

app = FastAPI()

global_id = ''
global_mid = ''
global_sid = ''
global_ratings = []
global_date = ''
global_product = ''
global_quantity = 0
yes = 0
global_issue =''
global_risks =''
global_optimization = ''

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    print(intent)
    # output_contexts = payload['queryResult']['outputContexts']

    #tracking current state of order by id-------------------------------
    if intent == "track_order_by_id":
        parameters = payload['queryResult']['parameters'] 
        print(parameters)
        merchant_id = parameters['merchant_id']
        order_id = parameters['order_id']
        position = track_order_by_id(merchant_id,order_id)
        return JSONResponse(content={
    "fulfillmentText" : f"Order id {parameters['order_id']} : {position}"})


    #Search suppliers by rating-----------------------------------------

    #suppliers_with_top_delivery_rating----------------------------------
    elif intent == "option_delivery_speed_rating":
        top_suppliers = await suppliers_with_top_delivery_rating()
        return JSONResponse(content={
    "fulfillmentText" : f"The top suppliers with with highest delivery ratings are \n{top_suppliers}"})
    
    #suppliers_with_top_responsiveness_rating----------------------------------
    elif intent == "option_responsiveness_rating":
        top_suppliers = suppliers_with_top_responsiveness_rating()
        return JSONResponse(content={
    "fulfillmentText" : f"The most responsive suppliers are \n{top_suppliers}"})

    #suppliers_with_lowest_prices----------------------------------------------
    elif intent == "option_price_rating":
        top_suppliers = suppliers_with_lowest_prices()
        return JSONResponse(content={
    "fulfillmentText" : f"The top suppliers with with the lowest prices are \n{top_suppliers}"})

    #suppliers_with_highest_product_quality----------------------------------------------
    elif intent == "option_product_quality_rating":
        top_suppliers = suppliers_with_highest_product_quality()
        return JSONResponse(content={
    "fulfillmentText" : f"The top suppliers with with highest product quality are \n{top_suppliers}"})


    #Search supplier by ID---------------------------------------------------------------
    elif intent == "search_by_supplier_id":
        parameters = payload['queryResult']['parameters']
        id = parameters['id']
        supplier = return_supplier_info_with_id(id)
        return JSONResponse(content={
    "fulfillmentText" : f"The information about the supplier with id {id} is \n{supplier}"})

    #search_suppliers_by_product_name
    elif intent == "search_suppliers_by_product_name":
        parameters = payload['queryResult']['parameters']
        product_name = parameters['product']
        suppliers = find_top_suppliers_selling_product_name(product_name)
        return JSONResponse(content={
    "fulfillmentText" : f"The suppliers selling the product {product_name} are {suppliers}"})

    #rate_supplier_by_id(collect id,collect ratings and then collect the written review and send it to backend)
    
    #collect id
    elif intent == "rate_supplier_by_id":
        parameters = payload['queryResult']['parameters']
        global global_mid
        global global_sid
        global_mid = parameters['merchant_id']
        global_sid = parameters['supplier_id']

    #collect ratings in list format in the order delivery,quality,responsiveness,price
    elif intent == 'rate_supplier_collect_ratings':
        parameters = payload['queryResult']['parameters']
        global global_ratings 
        global_ratings = [parameters['delivery'],parameters['quality'],parameters['responsiveness'],parameters['price']]


    #send the full rating and review back to backend
    elif intent == 'rate_supplier_collect_written_review':
        parameters = payload['queryResult']['parameters']
        review = parameters['any']
        confirm = await send_review_to_backend(global_mid,global_sid,global_ratings,review)
        return JSONResponse(content={
    "fulfillmentText" : f"{confirm} for {global_sid} by {global_mid}"})

    #find net profit
    elif intent == 'collect_merchant_id_for_profit':
        parameters = payload['queryResult']['parameters']
        id = review = parameters['id']
        profit = find_profit_by_id(id)
        return JSONResponse(content={
    "fulfillmentText" : f"{profit}"})

    #collect date profit
    elif intent == "datewise_profit_intro":
        parameters = payload['queryResult']['parameters']
        global global_date
        global_date = parameters['date'][:10]

    #find profit for collected date
    elif intent == "collect_id_for_datewise_profit":
        parameters = payload['queryResult']['parameters']
        id = parameters['id']
        profit = await find_datewise_profit_by_id(global_date,id)
        return JSONResponse(content={
    "fulfillmentText" : f"Your profit for the day {global_date} is Rupees {profit}"})

    #take order info
    elif intent == "take_order":
        parameters = payload['queryResult']['parameters']
        print(parameters)
        global global_product
        global global_quantity
        global_product = parameters['product']
        global_quantity = parameters['number']

    #place order to the given supplier
    elif intent == "confirm_order":
        parameters = payload['queryResult']['parameters']
        mid = parameters['merchant_id']
        sid = parameters['supplier_id']
        order_id = place_order(mid,sid,global_product,global_quantity)
        return JSONResponse(content={
    "fulfillmentText" : f"Your order for {global_quantity} units of {global_product} from supplier id: {sid} has been placed successfully. Your order id is {order_id}"})

    #cancel order by order id 
    elif intent == "cancel_order_by_id":
        parameters = payload['queryResult']['parameters']
        merchant_id = parameters['merchant_id']
        order_id = parameters['order_id']
        confirm = cancel_order(merchant_id, order_id)
        return JSONResponse(content={
    "fulfillmentText" : f"{confirm}"})

    #Return Product info and Suppliers selling by product name
    elif intent == 'search_by_product_name':
        parameters = payload['queryResult']['parameters']
        product_name = parameters['product']
        product_info = await return_product_info_by_name(product_name)
        return JSONResponse(content={
    "fulfillmentText" : f"{product_info}"})

    #Return Product info and Suppliers selling by product ID
    elif intent == 'search_by_product_id':
        parameters = payload['queryResult']['parameters']
        product_id = parameters['id']
        product_info = await return_product_info_by_id(product_id)
        return JSONResponse(content={
    "fulfillmentText" : f"{product_info}"})

    #search top supplier selling a product by product id
    elif intent == 'search_supplier_by_product_id':
        parameters = payload['queryResult']['parameters']
        product_id = parameters['id']
        top_suppliers = find_top_suppliers_selling_product_id(product_id)
        return JSONResponse(content={
    "fulfillmentText" : f"The top suppliers selling the product with id {product_id} are {top_suppliers}"})

    # # Handle issues with ticketing

    elif intent == 'fallback_intent':
        global global_issue
        global_issue = payload['queryResult']['queryText']
        print(global_issue)


    elif intent == 'default_fallback_intent_yes_no':
        query = payload['queryResult']['queryText']
        print(query)
        if query.lower() == 'yes':
            global yes
            yes = 1
        else:
            return JSONResponse(content={
        "fulfillmentText" : f"Type Menu to go back"})
        
    elif intent == "collect_email_and_merchant_id":
        parameters = payload['queryResult']['parameters']
        email = parameters['email']
        id = parameters['id']
        print(email,id)
        if yes:
            ticket_number = 0
            ticket_number = await store_issue_in_db(global_issue,email,id)
            print(ticket_number)
            return JSONResponse(content={
        "fulfillmentText" : f"Your ticket number is {ticket_number}.You will be contacted about the problem '{global_issue}' soon by our support team"})

    #Trying to create possible delay
    elif intent == "detailed_risk_analysis_confirmation":
        parameters = payload['queryResult']['parameters']
        global global_id
        global global_risks
        global_id = parameters['id']
        global_risks = await detailed_risk_analysis(global_id)
        return JSONResponse(content={
        "fulfillmentText" : f'''Do you want to get the detailed risk analysis for merchant {global_id}'''})
    
    #ASK AI for risk analysis output detailed_risk_analysis_confirmation
    elif intent == "detailed_risk_analysis_output":
        time.sleep(4)
        if global_risks == 'NOT_FOUND':
            return JSONResponse(content={
        "fulfillmentText" : f'''NO POSSIBLE RISKS IDENTIFIED FOR MERCHANT ID {global_id}'''})
        else:
            return JSONResponse(content={
        "fulfillmentText" : f'''POSSIBLE RISKS FOR MERCHANT ID {global_id}
{global_risks}'''})
        
    #creating possible delay for optimization
    elif intent == "business_optimization_recommendation_confirmation":
        parameters = payload['queryResult']['parameters']
        # global global_id
        global global_optimization
        global_id = parameters['id']
        global_optimization = await business_optimization_recommendation(global_id)
        return JSONResponse(content={
        "fulfillmentText" : f'''Do you want to get the possible optimizations for merchant id {global_id}'''})
    

    #ask AI for business optimization output  
    elif intent == "business_optimization_recommendation_output":
        time.sleep(3)
        if global_risks == 'NOT_FOUND':
            return JSONResponse(content={
        "fulfillmentText" : f'''NO POSSIBLE OPTIMIZATIONS IDENTIFIED FOR MERCHANT ID {global_id}'''})
        else:
            return JSONResponse(content={
        "fulfillmentText" : f'''POSSIBLE BUSINESS OPTIMIZATIONS TO BE MADE FOR MERCHANT ID {global_id}
{global_optimization}'''})
       
    #Trying to create a possible delay for my most profitable product
    elif intent == "my_most_profitable_product_confirmation":
        parameters = payload['queryResult']['parameters']
        global_id = parameters['id']
        global_product = await most_profitable_product(global_id)
    
    #ask AI for my most profitable product
    elif intent == "my_most_profitable_product":
        return JSONResponse(content={
        "fulfillmentText" : f'''Most profitable products for Merchant ID {global_id} are 
{global_product}'''})
    
    #Trying to create a possible delay 
    elif intent == "most_profitable_product_in_market":
        global_product = await most_profitable_product_in_market()
        return JSONResponse(content={
        "fulfillmentText" : f'''Most profitable products in the market are:
{global_product}'''})
    
    #ask AI for most profitable product in the market
    elif intent == "most_profitable_product_in_market_output":
        time.sleep(3)
        return JSONResponse(content={
        "fulfillmentText" : f'''Most profitable products in the market are:
{global_product}'''})

    #trying to create a possible delay
    elif intent == "most_selling_product_in_market":
        global_product = await most_selling_product_in_market()
        return JSONResponse(content={
        "fulfillmentText" : f'''Most selling products in the market are:
{global_product}'''})
    
    #ask AI for most selling product in the market
    elif intent == "most_selling_product_in_market_output":
        time.sleep(3)
        return JSONResponse(content={
        "fulfillmentText" : f'''Most selling products in the market are:
{global_product}'''})
    
    #ask for inventory stock for a particular merchant 
    elif intent == "inventory_overview":
        parameters = payload['queryResult']['parameters']
        merchant_id = parameters['id']
        stock_info = await find_inventory_stock(merchant_id)
        return JSONResponse(content={
        "fulfillmentText" : f'''{stock_info}'''})
    
    elif intent == "inventory_overview_AI":
        parameters = payload['queryResult']['parameters']
        merchant_id = parameters['id']
        stock_info = await find_inventory_stock_AI(merchant_id)
        return JSONResponse(content={
        "fulfillmentText" : f'''{stock_info}'''})

############################################################################################################################################################
############################################################################################################################################################
############################################################################################################################################################

def track_order_by_id(merchant_id,order_id):
    try:
        response = requests.get(f"https://bizminds-backend.onrender.com/api/operations/check_status/{merchant_id}/{order_id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        return data['message']
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def suppliers_with_top_delivery_rating():
    try:
        output =''
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/{1}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # print(data)
        for n,i in enumerate(data):
            if n == 11:
                break
            output+=f'''
Supplier ID = {i['supplier_id']}
Supplier Name = {i['name']}
Delivery Rating = {i['rating'][1]}

'''

        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def suppliers_with_top_responsiveness_rating():
    try:
        output =''
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/{3}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # print(data)
        for n,i in enumerate(data):
            if n == 11:
                break
            output+=f'''
Supplier ID = {i['supplier_id']}
Supplier Name = {i['name']}
Supplier Responsiveness Rating = {i['rating'][3]}

'''

        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def suppliers_with_lowest_prices():
    try:
        output =''
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/{4}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # print(data)
        for n,i in enumerate(data):
            if n == 11:
                break
            output+=f'''
Supplier ID = {i['supplier_id']}
Supplier Name = {i['name']}
Price Rating = {i['rating'][4]}

'''

        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def suppliers_with_highest_product_quality():
    try:
        output =''
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/{2}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # print(data)
        for n,i in enumerate(data):
            if n == 11:
                break
            output+=f'''
Supplier ID = {i['supplier_id']}
Supplier Name = {i['name']}
Product Quality Rating = {i['rating'][2]}

'''

        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def return_supplier_info_with_id(id):
    try:
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/get_supplier/{id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        output=f'''
Supplier ID = {data['supplier_id']}
Supplier Name = {data['name']}
Shop Name = {data['shop_name']}
Email = {data['email']}
Phone = {data['phone']}
Address = {data['address']}
Total Rating = {data['rating'][0]}
Delivery Rating = {data['rating'][1]}
Quality Rating = {data['rating'][2]}
Responsiveness Rating = {data['rating'][3]}
Price Rating = {data['rating'][4]}
Products sold : 
'''
        for n,i in enumerate(data['products_sold']):
            output+=f"{i} : Rupees {data['product_prices'][n]}\n"

        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

#Return Product info and the supplier id's selling it /api/suppliers/by_product_name/:name
async def return_product_info_by_id(product_id):
    try:
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/by_productID/{product_id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        product = data['Product'][0]
        suppliers = data['Suppliers']
        print(product,f'\n\n\n\n',suppliers)
        supplier_list = [i['supplier_id'] for i in suppliers]
        print(supplier_list)

        product_info = f'''
Product Name : {product['name']}
Product ID : {product['product_id']}
Product Info : {product['product_info']}
Product Image link : {product['image']}
Sold by : {supplier_list}
'''
        print(product_info)
        return product_info
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def return_product_info_by_name(product_name):
    try:
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/by_product_name/{product_name}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        product = data['product']
        suppliers = data['suppliers']
        supplier_list = [i['supplier_id'] for i in suppliers]

        product_info = f'''
Product Name : {product['name']}
Product ID : {product['product_id']}
Product Info : {product['product_info']}
Product Image link : {product['image']}
Sold by : {supplier_list}
'''
        print(product_info)
        return product_info
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def send_review_to_backend(global_mid,global_sid,global_ratings,review):
    review_data = {
    "merchant_id":f"{global_mid}",
    "supplier_id":f"{global_sid}",
    "rating":global_ratings,
    "review":review
    }

    try:
        response = requests.post("https://bizminds-backend.onrender.com/api/ratings/add_ratings_reviews", data=review_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # print(data)
        return data['message']
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")



def find_profit_by_id(id):
    try:
        response = requests.get(f"https://bizminds-backend.onrender.com/api/sales/get/totalprofit/{id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        revenue = data['Total_SP']
        profit = data['Total_Profit']
        output = f'''
Merchant ID :  {id}
Total Revenue till date: Rs {revenue}
Total Profit till date: Rs {profit}

'''

        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")



async def find_datewise_profit_by_id(date,id):
    date = date.replace('-','/')
    date = datetime.strptime(date, "%Y/%m/%d")
    date = date.strftime("%m/%d/%Y")
    if date[3]=='0':
        date = f'{date[:3]}{date[4:]}'
    if date[0]=='0':
        date = date[1:]
    date_data = {
        "merchant_id":f"{id}",
        "date": date
    }
    
    print(date_data)

    try:
        response = requests.post("https://bizminds-backend.onrender.com/api/sales/profit_by_day", data=date_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        return data['total_profit']
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def place_order(mid,sid,product,quantity):
    order_data = {
        "product": product,
        "supplier": sid,
        "quantity": quantity,
    }

    try:
        response = requests.post(f"https://bizminds-backend.onrender.com/api/operations/add/{mid}/placed", data=order_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data['operation']['operation_id']
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def cancel_order(merchant_id,order_id):
    try:
        response = requests.patch(f"https://bizminds-backend.onrender.com/api/operations/cancel_operation/{merchant_id}/{order_id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return f"Order ID {order_id} {data['message'][8:]}"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


#returns a list of all the sellers of the product id but unsorted
def find_top_suppliers_selling_product_id(product_id):
    try:
        output =''
        product_id=f'p{int(product_id)}'
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/by_productID/{product_id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        # suppliers = data['suppliers']
        # print(data)
        for i in data:
            output+=f'''
Supplier ID = {i['supplier_id']}
Supplier Name = {i['name']}
Shop Name = {i['shop_name']}
Email = {i['email']}
Phone = {i['phone']}
Address = {i['address']}
Rating = {i['rating'][0]}
Price of {product_id} = {i['product_prices'][i['products_sold'].index(product_id)]}

'''
        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


#returns a list of all the sellers of the product name sorted by net rating
def find_top_suppliers_selling_product_name(product_name):
    try:
        # print(product_name)
        output =''
        response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/by_product_name/{product_name}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        suppliers = data['suppliers']
        product_id = data['product']['product_id']
        # print(product_id)
        for i in suppliers:
            output+=f'''
Supplier ID = {i['supplier_id']}
Supplier Name = {i['name']}
Shop Name = {i['shop_name']}
Email = {i['email']}
Phone = {i['phone']}
Address = {i['address']}
Rating = {i['rating'][0]}
Price of {product_name} = {i['product_prices'][i['products_sold'].index(product_id)]}

'''
        print(output)
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


# handle issues api calling function
async def store_issue_in_db(issue,email,id):
    issue_data = {
        "merchant_id": f'{id}',
        "email": email,
        "issue": issue,
    }

    try:
        response = requests.post("https://bizminds-backend.onrender.com/api/issues/add", data=issue_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data['issue']['_id']
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


async def detailed_risk_analysis(id):
    try:
        response = requests.get(f"https://insights-bizminds.onrender.com/getRisks?merchantId={id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def business_optimization_recommendation(id):
    try:
        response = requests.get(f"https://insights-bizminds.onrender.com/getOptimization?merchantId={id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def most_profitable_product(id):
    try:
        response = requests.get(f"https://insights-bizminds.onrender.com/getProductWithMaxProfit?merchantId={id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
#         output = f'''
# Product Name : {data['name']}
# Product ID : {data['product_id']}
# Product Info : {data['product_info']}

# '''
#         print(output)
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    

async def most_selling_product_in_market():
    try:
        response = requests.get(f"https://insights-bizminds.onrender.com/topProductsSold")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def most_profitable_product_in_market():
    try:
        response = requests.get(f"https://insights-bizminds.onrender.com/topProductForMaxProfit")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def find_inventory_stock(merchant_id):
    try:
        output =''
        response = requests.get(f"https://bizminds-backend.onrender.com/api/stocks/inventory/{merchant_id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        data=data[0]
        print(data)
        products = data['products']
        quantity = data['quantity']
        for i in range(len(products)):
            # response = requests.get(f"https://bizminds-backend.onrender.com/api/suppliers/by_productID/{products[i]}")
            # # print(response)
            # response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            # data = response.json()
            # product_name = data['Product'][0]['name']
            # Product Name : {product_name}
            output+=f'''
Product ID : {products[i]}
Quantity Left : {quantity[i]}
'''
        return output
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

async def find_inventory_stock_AI(merchant_id):
    try:
        output =''
        response = requests.get(f"https://insights-bizminds.onrender.com/getLowStocks?merchantId={merchant_id}")
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
