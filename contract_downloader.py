from datetime import datetime, time

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
        # Download NFO contract master
        nfo_response = alice.get_contract_master("NFO")
        if nfo_response['stat'] == 'Ok' or 'contract File Downloaded' in nfo_response.get('emsg', ''):
            print("NFO contract master downloaded successfully.")
        else:
            print(f"Error downloading NFO contract master: {nfo_response['emsg']}")
            success = False
            
        # Download NSE contract master
        nse_response = alice.get_contract_master("NSE")
        if nse_response['stat'] == 'Ok' or 'contract File Downloaded' in nse_response.get('emsg', ''):
            print("NSE contract master downloaded successfully.")
        else:
            print(f"Error downloading NSE contract master: {nse_response['emsg']}")
            success = False
            
        return success
            
    except Exception as e:
        print(f"Error downloading contract master: {e}")
        return False
