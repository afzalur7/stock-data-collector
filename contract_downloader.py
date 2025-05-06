def download_contract(alice):
    """
    Downloads the contract master from NFO using the provided alice object.
    
    Args:
        alice: The authenticated Aliceblue object
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        response = alice.get_contract_master("NFO") 
        
        if response['stat'] == 'Ok':
            print("Previous day's master contract downloaded successfully.")
            return True
        else:
            print(f"Error: {response['emsg']}")
            return False
            
    except Exception as e:
        print(f"Error downloading contract master: {e}")
        return False
