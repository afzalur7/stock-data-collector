import os
import pandas as pd
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
        
        # Download NFO contract master
        try:
            # Get the contract master data
            nfo_response = alice.get_contract_master("NFO")
            
            if nfo_response['stat'] == 'Ok' or 'contract File Downloaded' in nfo_response.get('emsg', ''):
                print("NFO contract master downloaded successfully.")
            else:
                print(f"Error downloading NFO contract master: {nfo_response.get('emsg', '')}")
                success = False
        except Exception as e:
            print(f"Error downloading NFO contract master: {str(e)}")
            success = False
            
        # Download NSE contract master
        try:
            # Get the contract master data
            nse_response = alice.get_contract_master("NSE")
            
            if nse_response['stat'] == 'Ok' or 'contract File Downloaded' in nse_response.get('emsg', ''):
                print("NSE contract master downloaded successfully.")
            else:
                print(f"Error downloading NSE contract master: {nse_response.get('emsg', '')}")
                success = False
        except Exception as e:
            print(f"Error downloading NSE contract master: {str(e)}")
            success = False
            
        return success
            
    except Exception as e:
        print(f"Error downloading contract master: {e}")
        return False
