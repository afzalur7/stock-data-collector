import os
import requests
from datetime import datetime, time as datetime_time

def download_contract(alice):
    """
    Downloads the contract master for both NFO and NSE using the provided alice object.
    
    Args:
        alice: The authenticated Aliceblue object
        
    Returns:
        bool: True if both downloads were successful, False otherwise
    """
    success = True
    
    try:
        # Check if it's before 8 AM
        current_time = datetime.now().time()
        target_time = datetime_time(8, 0)  # 8:00 AM
        before_8am = current_time < target_time
        
        if before_8am:
            print("Note: It's before 8 AM. Previous day's contract file will be downloaded.")
        
        # Get session ID from alice object
        session_id = alice.get_session_id()
        if session_id.get('stat') != 'Ok':
            print(f"Error getting session ID: {session_id.get('emsg')}")
            return False
            
        headers = {
            'Authorization': f"Bearer {session_id.get('sessionID')}",
            'User-Agent': 'pya3'
        }
        
        # Download NFO contract master
        try:
            nfo_url = 'https://ant.aliceblueonline.com/api/v2/contracts.json?exch=NFO'
            nfo_response = requests.get(nfo_url, headers=headers)
            
            if nfo_response.status_code == 200:
                with open('NFO.csv', 'wb') as f:
                    f.write(nfo_response.content)
                print("NFO contract master downloaded successfully.")
            else:
                print(f"Error downloading NFO contract master: {nfo_response.text}")
                success = False
        except Exception as e:
            print(f"Error downloading NFO contract master: {str(e)}")
            success = False
            
        # Download NSE contract master
        try:
            nse_url = 'https://ant.aliceblueonline.com/api/v2/contracts.json?exch=NSE'
            nse_response = requests.get(nse_url, headers=headers)
            
            if nse_response.status_code == 200:
                with open('NSE.csv', 'wb') as f:
                    f.write(nse_response.content)
                print("NSE contract master downloaded successfully.")
            else:
                print(f"Error downloading NSE contract master: {nse_response.text}")
                success = False
        except Exception as e:
            print(f"Error downloading NSE contract master: {str(e)}")
            success = False
            
        return success
            
    except Exception as e:
        print(f"Error downloading contract master: {e}")
        return False
