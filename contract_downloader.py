import os
import csv
import pandas as pd
from datetime import datetime, time as datetime_time

def fix_csv_format(exchange):
    """
    Fix CSV file format to ensure consistency across platforms
    """
    try:
        # Read the CSV file with robust error handling
        df = pd.read_csv(
            f"{exchange}.csv",
            on_bad_lines='skip',  # Updated from error_bad_lines
            dtype=str,  # Read all columns as strings initially
            encoding='utf-8'
        )
        
        # Define expected numeric columns
        numeric_cols = ['token', 'strike', 'lotsize', 'tick_size']
        
        # Convert numeric columns properly
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean up other columns
        df = df.fillna('')  # Replace NaN with empty string
        
        # Save with consistent formatting
        df.to_csv(
            f"{exchange}.csv",
            index=False,
            quoting=csv.QUOTE_NONNUMERIC,
            encoding='utf-8',
            line_terminator='\n'  # Ensure consistent line endings
        )
        return True
    except Exception as e:
        print(f"Error fixing {exchange}.csv format: {str(e)}")
        return False

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
                # Fix CSV format after successful download
                if fix_csv_format("NFO"):
                    print("NFO contract master downloaded and formatted successfully.")
                else:
                    print("Error fixing NFO contract master format.")
                    success = False
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
                # Fix CSV format after successful download
                if fix_csv_format("NSE"):
                    print("NSE contract master downloaded and formatted successfully.")
                else:
                    print("Error fixing NSE contract master format.")
                    success = False
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
