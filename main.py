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
import csv
import os
from contract_downloader import download_contract

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

# Download contract master
download_contract(alice)


# Load conditions from Excel
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

# Get file paths with date
def get_data_file_paths():
    # Create data directory if it doesn't exist
    data_dir = 'market_data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Get current date for file names
    current_date = datetime.now().strftime('%Y%m%d')
    
    # Define file paths
    trading_data_file = os.path.join(data_dir, f'trading_data_{current_date}.csv')
    depth_data_file = os.path.join(data_dir, f'market_depth_{current_date}.csv')
    
    return trading_data_file, depth_data_file

# Initialize CSV files with headers if they don't exist
def initialize_csv():
    trading_data_file, depth_data_file = get_data_file_paths()
    
    # Main trading data CSV
    if not os.path.exists(trading_data_file):
        headers = [
            'timestamp', 'symbol', 'open', 'high', 'low', 'close', 'ltp',
            'volume', 'bid_qty', 'offer_qty', 'expiry',
            'lower_circuit', 'upper_circuit', 'oi', 'ltt', 'avg_price',
            'buy_state', 'sell_state', 'sl_state'
        ]
        with open(trading_data_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"Created new trading data file: {trading_data_file}")
    
    # Market depth CSV
    if not os.path.exists(depth_data_file):
        depth_headers = [
            'timestamp', 'symbol', 'type',  # type will be 'bid' or 'offer'
            'price', 'orders', 'quantity'
        ]
        with open(depth_data_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(depth_headers)
        print(f"Created new market depth file: {depth_data_file}")

# Dictionary to store market data
market_data = {}
depth_data = {}  # To store market depth information

# Record market depth to CSV
def record_depth_data():
    while True:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_rows = []
            
            with market_data_lock:
                for symbol in depth_data:
                    data = depth_data[symbol]
                    
                    # Record bid depth
                    if 'bid' in data:
                        for level in data['bid']:
                            data_rows.append([
                                current_time,
                                symbol,
                                'bid',
                                level.get('price', 0),
                                level.get('orders', 0),
                                level.get('quantity', 0)
                            ])
                    
                    # Record offer depth
                    if 'offer' in data:
                        for level in data['offer']:
                            data_rows.append([
                                current_time,
                                symbol,
                                'offer',
                                level.get('price', 0),
                                level.get('orders', 0),
                                level.get('quantity', 0)
                            ])
            
            if data_rows:
                _, depth_data_file = get_data_file_paths()
                with open(depth_data_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(data_rows)
                
                print(f"Depth data recorded at {current_time}")
            
        except Exception as e:
            print(f"Error recording depth data: {e}")
            
        time.sleep(10)  # Record every 10 seconds

# Record data to CSV
def record_data():
    while True:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_rows = []
            
            for symbol in market_data:
                if symbol in conditions:
                    data = market_data[symbol]
                    data_rows.append([
                        current_time,
                        symbol,
                        data.get('open', 0),
                        data.get('high', 0),
                        data.get('low', 0),
                        data.get('close', 0),
                        data.get('ltp', 0),
                        data.get('volume', 0),
                        data.get('bid_qty', 0),
                        data.get('offer_qty', 0),
                        data.get('expiry', ''),
                        data.get('lower_circuit', 0),
                        data.get('upper_circuit', 0),
                        data.get('oi', 0),
                        data.get('ltt', ''),
                        data.get('avg_price', 0),
                        conditions[symbol]['buy_state'],
                        conditions[symbol]['sell_state'],
                        conditions[symbol]['sl_state']
                    ])
            
            trading_data_file, _ = get_data_file_paths()
            with open(trading_data_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(data_rows)
                
            print(f"Data recorded at {current_time}")
            
        except Exception as e:
            print(f"Error recording data: {e}")
            
        time.sleep(10)  # Record every 10 seconds

# Specify the correct file path
file_path = 'instruments.xlsx'
conditions = load_conditions_from_excel(file_path)
print(f"this is conditions:{conditions}") #Debug code to check the condition generated properly

LTP = {}
socket_opened = False
subscribe_list = []

# Lock for thread safety
state_lock = threading.Lock()
market_data_lock = threading.Lock()

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
    global LTP, market_data, depth_data
    feed_message = json.loads(message)

    if 'ts' in feed_message:
        symbol = feed_message['ts']
        
        with market_data_lock:
            # Initialize market data for the symbol if not exists
            if symbol not in market_data:
                market_data[symbol] = {}
            if symbol not in depth_data:
                depth_data[symbol] = {'bid': [], 'offer': []}
            
            # Update market data with available fields
            if 'lp' in feed_message:  # Last Price
                LTP[symbol] = float(feed_message['lp'])
                market_data[symbol]['ltp'] = float(feed_message['lp'])
            
            if 'o' in feed_message:  # Open
                market_data[symbol]['open'] = float(feed_message['o'])
            
            if 'h' in feed_message:  # High
                market_data[symbol]['high'] = float(feed_message['h'])
            
            if 'l' in feed_message:  # Low
                market_data[symbol]['low'] = float(feed_message['l'])
            
            if 'c' in feed_message:  # Close
                market_data[symbol]['close'] = float(feed_message['c'])
            
            if 'v' in feed_message:  # Volume
                market_data[symbol]['volume'] = int(feed_message['v'])
            
            if 'bq' in feed_message:  # Bid Quantity
                market_data[symbol]['bid_qty'] = int(feed_message['bq'])
            
            if 'sq' in feed_message:  # Offer Quantity
                market_data[symbol]['offer_qty'] = int(feed_message['sq'])
            
            if 'oi' in feed_message:  # Open Interest
                market_data[symbol]['oi'] = int(feed_message['oi'])
            
            if 'ltt' in feed_message:  # Last Trade Time
                market_data[symbol]['ltt'] = feed_message['ltt']
            
            if 'ap' in feed_message:  # Average Price
                market_data[symbol]['avg_price'] = float(feed_message['ap'])
            
            # Update market depth data
            if 'dp' in feed_message:  # Depth
                depth = feed_message['dp']
                
                # Process bid depth
                if 'bid' in depth:
                    depth_data[symbol]['bid'] = []
                    for bid in depth['bid']:
                        depth_data[symbol]['bid'].append({
                            'price': float(bid.get('p', 0)),
                            'orders': int(bid.get('no', 0)),
                            'quantity': int(bid.get('q', 0))
                        })
                
                # Process offer depth
                if 'ask' in depth:
                    depth_data[symbol]['offer'] = []
                    for offer in depth['ask']:
                        depth_data[symbol]['offer'].append({
                            'price': float(offer.get('p', 0)),
                            'orders': int(offer.get('no', 0)),
                            'quantity': int(offer.get('q', 0))
                        })
            
            # Get additional instrument details
            try:
                if 'NIFTY' in symbol:
                    instrument = alice.get_instrument_for_fno(
                        exch='NFO',
                        symbol='NIFTY',
                        expiry_date=conditions[symbol]['expiry_date'],
                        is_fut=False,
                        strike=conditions[symbol]['strike'],
                        is_CE='C' in symbol
                    )
                else:
                    instrument = alice.get_instrument_by_symbol('NSE', symbol)
                
                if instrument:
                    market_data[symbol]['expiry'] = getattr(instrument, 'expiry', '')
                    market_data[symbol]['lower_circuit'] = getattr(instrument, 'lower_circuit', 0)
                    market_data[symbol]['upper_circuit'] = getattr(instrument, 'upper_circuit', 0)
            except Exception as e:
                print(f"Error getting instrument details for {symbol}: {e}")

        print(f"{symbol}: {market_data[symbol]}")  # Debug print
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

# Initialize CSV files
initialize_csv()

# Start data recording threads
data_recording_thread = threading.Thread(target=record_data)
data_recording_thread.daemon = True
data_recording_thread.start()

depth_recording_thread = threading.Thread(target=record_depth_data)
depth_recording_thread.daemon = True
depth_recording_thread.start()

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
