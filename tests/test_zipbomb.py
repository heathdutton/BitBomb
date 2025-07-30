#!/usr/bin/env python3
import zipfile
import os
import time
import resource
import signal
import sys

def limit_resources():
    """Set resource limits to prevent system damage"""
    # Limit memory to 100MB
    resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, 100 * 1024 * 1024))
    
    # Limit file size to 50MB per file
    resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, 50 * 1024 * 1024))
    
    # Limit CPU time to 30 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    
    # Note: Disk quota is enforced at Docker level with --storage-opt

def timeout_handler(signum, frame):
    print("Timeout reached! Extraction taking too long.")
    sys.exit(1)

def test_zipbomb():
    """Test the zipbomb in a controlled environment"""
    print("Testing crypto wallet zipbomb...")
    zipfile_name = 'test_zipbomb.zip'
    print(f"Initial zip size: {os.path.getsize(zipfile_name) / 1024 / 1024:.2f} MB")
    
    # Set resource limits
    limit_resources()
    
    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)  # 60 second timeout
    
    extraction_dir = "/tmp/extracted"
    os.makedirs(extraction_dir, exist_ok=True)
    
    # Track disk usage
    total_disk_used = 0
    max_disk_allowed = 50 * 1024 * 1024  # 50MB
    
    try:
        start_time = time.time()
        total_size = 0
        file_count = 0
        
        with zipfile.ZipFile(zipfile_name, 'r') as zf:
            print(f"Files in archive: {len(zf.namelist())}")
            
            for info in zf.infolist():
                print(f"Extracting: {info.filename} (compressed: {info.compress_size} bytes, "
                      f"uncompressed: {info.file_size} bytes)")
                
                # Check disk space before extraction
                if total_disk_used + info.file_size > max_disk_allowed:
                    print(f"Disk space limit would be exceeded! Stopping extraction.")
                    print(f"Current disk usage: {total_disk_used / 1024 / 1024:.2f} MB")
                    break
                
                # Extract file
                zf.extract(info, extraction_dir)
                total_size += info.file_size
                total_disk_used += info.file_size
                file_count += 1
                
                # Check if extracted file contains wallet data
                extracted_path = os.path.join(extraction_dir, info.filename)
                if info.filename.endswith('.csv'):
                    # Read a sample of wallet data
                    try:
                        with open(extracted_path, 'r') as f:
                            sample = f.read(1000)
                            print(f"Sample wallet data:\n{sample[:200]}...\n")
                    except Exception as e:
                        print(f"Could not read extracted file: {e}")
        
        elapsed_time = time.time() - start_time
        print(f"\nExtraction completed!")
        print(f"Files extracted: {file_count}")
        print(f"Total uncompressed size: {total_size / 1024 / 1024:.2f} MB")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        print(f"Expansion ratio: {total_size / os.path.getsize(zipfile_name):.2f}x")
        
    except MemoryError:
        print("Memory limit exceeded! This confirms the zipbomb is working.")
    except OSError as e:
        print(f"Resource limit hit: {e}")
    except Exception as e:
        print(f"Error during extraction: {e}")
    
    # Clean up
    import shutil
    if os.path.exists(extraction_dir):
        shutil.rmtree(extraction_dir)

if __name__ == "__main__":
    test_zipbomb()