import os
import csv
import pandas as pd
from datetime import datetime, time as datetime_time

def fix_csv_format(exchange):
    """
    Fix CSV file format to ensure consistency across platforms
    """
    try:
        # Read the file content
        with open(f"{exchange}.csv", 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split into lines and clean up
        lines = content.splitlines()
        if not lines:
            print(f"Warning: {exchange}.csv is empty")
            return False
            
        # Process header
        header = lines[0].strip()
        if not header:
            print(f"Warning: {exchange}.csv has no header")
            return False
            
        # Expected columns
        expected_columns = ['token', 'symbol', 'name', 'expiry', 'strike', 'lotsize', 'instrumenttype', 'exch_seg', 'tick_size']
        
        # Write back with proper format
        with open(f"{exchange}.csv", 'w', newline='\n', encoding='utf-8') as f:
            # Write header
            f.write(','.join(expected_columns) + '\n')
            
            # Process and write data rows
            for line in lines[1:]:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Split the line and clean fields
                fields = line.split(',')
                cleaned_fields = []
                
                # Process each field
                for i, field in enumerate(fields):
                    field = field.strip().strip('"')
                    # Handle numeric fields
                    if i == 0:  # token
                        field = field if field.isdigit() else '0'
                    elif i == 4:  # strike
                        try:
                            float(field)
                        except:
                            field = '0.0'
                    elif i == 5:  # lotsize
                        field = field if field.isdigit() else '0'
                    elif i == 8:  # tick_size
                        try:
                            float(field)
                        except:
                            field = '0.0'
                    cleaned_fields.append(field)
                
                # Ensure we have all columns
                while len(cleaned_fields) < len(expected_columns):
                    cleaned_fields.append('')
                
                # Write the line
                f.write(','.join(cleaned_fields[:len(expected_columns)]) + '\n')
        
        return True
    except Exception as e:
        print(f"Error fixing {exchange}.csv format: {str(e)}")
        print(f"Attempting to read file content directly:")
        try:
            with open(f"{exchange}.csv", 'r', encoding='utf-8') as f:
                print(f.read()[:200])  # Print first 200 chars for debugging
        except Exception as read_error:
            print(f"Error reading file: {read_error}")
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
