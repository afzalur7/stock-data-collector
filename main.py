#Strategy v5 is working fine however the problem with the v5 is that it sell the share if the condition met
#without buying the share. That may be good if we want to do the same thing with strategy. 
#However in this stragegy the buy will work first then only the sell will happen. 
#I want to do the same first by changeing the condidtion in Excel Sheet and then in next verstion we will
# check the whether the share or option is actualy bought in the account or not. 
#######

import pandas as pd
from pya3 import *
import json
import threading
import time
from datetime import datetime

# Authentication
def authenticate():
    try:
        alice = Aliceblue(user_id='1198669', api_key='PNbYOZ80hZKWlqgYoFOxFoJHdMrPcpUr1vBDMBxZSvuohe8zSvTPPkoiFIh839sjY7lNtlXkfQf3ZG8rIQNNZboibRfvLb8bMtqa3MFi7pAEZxHzOGMHDmzE6P8L9icS')
        session_id = alice.get_session_id()
        if session_id.get('stat') != 'Ok':
            raise Exception(session_id.get('emsg'))
        return alice
    except Exception as e:
        print(f"Error during authentication: {e}")
        exit(1)

alice = authenticate()

# Check connectivity
def check_connectivity():
    try:
        profile = alice.get_profile()
        # print(profile)
    except Exception as e:
        print(f"Error during connectivity check: {e}")
        exit(1)

check_connectivity()
# # ##This line of code is to download the contract master
# response = alice.get_contract_master("NFO") 

# # Check if the contract master was downloaded successfully
# if response['stat'] == 'Ok':
#     print("Previous day's master contract downloaded successfully.")
# else:
#     print(f"Error: {response['emsg']}")
# ### Contract master code ends here

# # Load conditions from Excel
def load_conditions_from_excel(file_path):
    df = pd.read_excel(file_path)
    conditions = {}
    for _, row in df.iterrows():
        symbol = row['symbol']
        conditions[symbol] = {
            'buy_price': row['buy_price'],
            'buy_quantity': row['buy_quantity'],
            'sell_price': row['sell_price'],
            'sell_quantity': row['sell_quantity'],
            'sl_price': row['sl_price'],
            'sl_quantity': row['sl_quantity'],
            'buy_state': row['buy_state'],
            'sell_state': row['sell_state'],
            'sl_state': row['sl_state'],
            'expiry_date': row['expiry_date'].strftime('%Y-%m-%d') if isinstance(row['expiry_date'], pd.Timestamp) else row['expiry_date'],
            'strike': row['strike']
        }
    return conditions

# Specify the correct file path
file_path = 'instruments.xlsx'
conditions = load_conditions_from_excel(file_path)
# print(f"this is conditions:{conditions}") #Debug code to check the condition generated properly

LTP = {}
socket_opened = False
subscribe_list = []

# Lock for thread safety
state_lock = threading.Lock()

# Define WebSocket callbacks
def socket_open():
    global socket_opened
    print("Connected")
    socket_opened = True

def socket_close():
    global socket_opened
    print("Closed")
    socket_opened = False

def socket_error(message):
    print("Error:", message)

def feed_data(message):
    global LTP
    feed_message = json.loads(message)

    if 'lp' in feed_message and 'ts' in feed_message:
        symbol = feed_message['ts']
        LTP[symbol] = float(feed_message['lp'])
        print(symbol, ': ', LTP[symbol])  # Debugging statement to print LTP
        check_conditions(symbol)

def check_conditions(symbol):
    try:
        with state_lock:
            if symbol not in conditions:
                return
            
            cond = conditions[symbol]
            ltp = LTP[symbol]

            # Buy Condition
            if not cond['buy_state'] and ltp <= cond['buy_price']:
                print(f"Buy condition met for {symbol}. LTP={ltp}, Buy Price={cond['buy_price']}")
                cond['buy_state'] = True
                cond['sell_state'] = False
                cond['sl_state'] = False
                # threading.Thread(target=place_order, args=(symbol, 'buy', ltp, cond['buy_quantity'], cond['expiry_date'], cond['strike'])).start()
            
            # Sell Condition
            elif not cond['sell_state'] and ltp >= cond['sell_price']:
                print(f"Sell condition met for {symbol}. LTP={ltp}, Sell Price={cond['sell_price']}")
                cond['sell_state'] = True
                cond['buy_state'] = False
                # threading.Thread(target=place_order, args=(symbol, 'sell', ltp, cond['sell_quantity'], cond['expiry_date'], cond['strike'])).start()
            
            # Stop Loss Condition
            elif not cond['sl_state'] and ltp <= cond['sl_price']:
                print(f"Stop loss condition met for {symbol}. LTP={ltp}, Stop Loss Price={cond['sl_price']}")
                cond['sl_state'] = True
                # threading.Thread(target=place_order, args=(symbol, 'sell', ltp, cond['sl_quantity'], cond['expiry_date'], cond['strike'])).start()
            
    except Exception as e:
        print(f"Error in check_conditions for {symbol}: {e}")

def place_order(symbol, transaction_type, price, quantity, expiry_date=None, strike=None):
    if 'NIFTY' in symbol:
        instrument = alice.get_instrument_for_fno(
            exch='NFO',
            symbol='NIFTY',
            expiry_date=expiry_date,
            is_fut=False,
            strike=strike,
            is_CE='C' in symbol
        )
    else:
        instrument = alice.get_instrument_by_symbol('NSE', symbol)
    
    if instrument is None:
        print(f"Error: Instrument not found for symbol {symbol}")
        return

    print(f"Placing order: Symbol={symbol}, Type={transaction_type}, Price={price}, Quantity={quantity}, Expiry Date={expiry_date}, Strike={strike}")
    try:
        if transaction_type == 'buy':
            order = alice.place_order(transaction_type=TransactionType.Buy,
                                      instrument=instrument,
                                      quantity=quantity,
                                      order_type=OrderType.Market,
                                      product_type=ProductType.Intraday,
                                      price=0.0,
                                      trigger_price=None,
                                      stop_loss=None,
                                      square_off=None,
                                      trailing_sl=None,
                                      is_amo=False,
                                      order_tag='order1')
            print(f"Buy order placed for {symbol} at market price with quantity {quantity}: {order}")

        elif transaction_type == 'sell':
            order = alice.place_order(transaction_type=TransactionType.Sell,
                                      instrument=instrument,
                                      quantity=quantity,
                                      order_type=OrderType.Market,
                                      product_type=ProductType.Intraday,
                                      price=0.0,
                                      trigger_price=None,
                                      stop_loss=None,
                                      square_off=None,
                                      trailing_sl=None,
                                      is_amo=False,
                                      order_tag='order1')
            print(f"Sell order placed for {symbol} at market price with quantity {quantity}: {order}")

    except Exception as e:
        print(f"Error placing order for {symbol}: {e}")

    # Reset the state after placing an order
    threading.Timer(30000, lambda: reset_state(symbol, transaction_type)).start()  # Reset after 50 minutes

def reset_state(symbol, transaction_type):
    with state_lock:
        if symbol in conditions:
            if transaction_type == 'buy':
                conditions[symbol]['buy_state'] = False
            elif transaction_type == 'sell':
                conditions[symbol]['sell_state'] = False
                conditions[symbol]['sl_state'] = False
    print(f"Reset state for {symbol} {transaction_type}")

# Subscribe to instruments
for symbol, cond in conditions.items():
    if 'NIFTY' in symbol:
        instrument = alice.get_instrument_for_fno(
            exch='NFO',
            symbol='NIFTY',
            expiry_date=cond['expiry_date'],
            is_fut=False,
            strike=cond['strike'],
            is_CE='C' in symbol
        )
    else:
        instrument = alice.get_instrument_by_symbol('NSE', symbol)
    if instrument is None:
        print(f"Error: Instrument not found for symbol {symbol}")
    else:
        subscribe_list.append(instrument)

# Filter out any invalid instruments
subscribe_list = [instr for instr in subscribe_list if isinstance(instr, Instrument)]

print(f"Subscribe List: {subscribe_list}")  # Debugging statement to print the subscribe list

# Start WebSocket in a separate thread
def start_websocket():
    alice.start_websocket(socket_open_callback=socket_open, 
                          socket_close_callback=socket_close,
                          socket_error_callback=socket_error, 
                          subscription_callback=feed_data, 
                          run_in_background=True)

websocket_thread = threading.Thread(target=start_websocket)
websocket_thread.start()

# Wait until socket is opened before subscribing
while not socket_opened:
    time.sleep(1)

alice.subscribe(subscribe_list)

# Run the script continuously with a small sleep delay
try:
    while True:
        if socket_opened:
            alice.subscribe(subscribe_list)
        time.sleep(1)  # Add a small delay to prevent high CPU usage
except KeyboardInterrupt:
    alice.stop_websocket()
    print("WebSocket stopped.")
