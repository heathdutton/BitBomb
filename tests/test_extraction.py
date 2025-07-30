#!/usr/bin/env python3
import zipfile
import os
import sys

def extract_sample():
    """Safely extract and display sample wallet data"""
    print("\nExtracting sample from ultimate_crypto_bomb.zip...")
    
    sample_lines = []
    bytes_processed = 0
    max_bytes = 10 * 1024 * 1024  # 10MB limit
    
    try:
        with zipfile.ZipFile('ultimate_crypto_bomb.zip', 'r') as zf:
            # Get first level
            print(f"Level 1 - Files: {len(zf.namelist())}")
            
            # Extract just one file from first level
            first_file = zf.namelist()[0]
            level1_data = zf.read(first_file)
            bytes_processed += len(level1_data)
            
            # Open the nested zip
            with zipfile.ZipFile(BytesIO(level1_data), 'r') as zf2:
                print(f"Level 2 - Files: {len(zf2.namelist())}")
                
                # Get one file from second level
                if bytes_processed < max_bytes and zf2.namelist():
                    second_file = zf2.namelist()[0]
                    level2_data = zf2.read(second_file)
                    bytes_processed += len(level2_data)
                    
                    # Continue to level 3
                    with zipfile.ZipFile(BytesIO(level2_data), 'r') as zf3:
                        print(f"Level 3 - Files: {len(zf3.namelist())}")
                        
                        # Get actual wallet data
                        if bytes_processed < max_bytes and zf3.namelist():
                            wallet_file = zf3.namelist()[0]
                            print(f"Level 4 - Extracting from {wallet_file}")
                            
                            # Only read first part to avoid memory issues
                            with zf3.open(wallet_file) as wf:
                                wallet_data = wf.read(10000)  # Read first 10KB only
                            
                            # Extract first 10 wallet entries
                            lines = wallet_data.decode('utf-8', errors='ignore').split('\n')
                            sample_lines = [line for line in lines if line.strip()][:10]
    
    except Exception as e:
        print(f"Controlled extraction stopped: {e}")
    
    print(f"\nSample wallet data (first 10 lines):")
    print("-" * 50)
    for line in sample_lines:
        print(line)
    print("-" * 50)
    print(f"\nBytes processed: {bytes_processed:,}")
    print("Extraction safely terminated.\n")

if __name__ == "__main__":
    from io import BytesIO
    extract_sample()
