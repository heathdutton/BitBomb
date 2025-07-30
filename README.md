# BitBomb: Defensive Crypto Wallet Archive

## Abstract

BitBomb is an educational demonstration that creates archives which appear to contain cryptocurrency wallet databases as a honeypot to be found by agents (be they malware or intruders).
By using the overlapping file technique with procedurally generated **fake** Bitcoin wallet data, it can achieve compression ratios exceeding 1M:1 while maintaining pseudo authenticity in its decoy content.

Example File: [bitcoin_wallets.zip](./output/bitcoin_wallets.zip)

## Research Context

This implementation addresses the growing threat of automated cryptocurrency theft tools that systematically scan systems for wallet files, private keys, and seed phrases. Traditional zipbombs lack domain-specific context, making them easily identifiable to sophisticated malware. BitBomb bridges this gap by creating archives that appear to contain **simulated** Bitcoin wallet exports from major exchanges and personal storage systems.

## Technical Implementation

### Compression Architecture

BitBomb utilizes the overlapping file technique, a variant of the zip bomb methodology first demonstrated in David Fifield's zblg.zip research. The core innovation lies in creating a single compressed "kernel" containing **simulated** wallet data, then referencing this kernel through multiple central directory entries with unique metadata.

**Key Technical Features:**
- **Kernel Generation**: Creates compressed wallet data with realistic entropy characteristics
- **Directory Overlapping**: Multiple ZIP central directory entries reference identical compressed data
- **Metadata Diversification**: Each entry appears unique through varied filenames, CRC values, and timestamps
- **ZIP64 Compliance**: Supports file counts exceeding the 65,535 limit of standard ZIP format

### Cryptographic Authenticity

The generated wallet data maintains cryptographic legitimacy through:

1. **BIP39 Compliance**: Seed phrases use the official Bitcoin Improvement Proposal 39 wordlist
2. **Address Derivation**: Bitcoin addresses follow proper derivation patterns from seed phrases
3. **Format Diversity**: Supports Legacy (P2PKH), Pay-to-Script-Hash (P2SH), and Bech32 address formats
4. **Deterministic Generation**: Reproducible wallet creation using cryptographic hash functions
5. **Entropy Simulation**: Default params, wallet balances, and transaction histories reflect semi-realistic distributions

### Statistical Distribution Modeling

Balance distributions reflect real-world Bitcoin wealth patterns:
- 40% empty addresses (generated but unused)
- 35% dust amounts (< $1 equivalent)
- 15% small holdings ($1-$100 equivalent)
- 8% medium holdings ($100-$10,000 equivalent)
- 1.8% large holdings ($10,000-$100,000 equivalent)
- 0.2% whale wallets (> $100,000 equivalent)

## Performance Estimates

| File Count | Compressed Size | Uncompressed Size | Compression Ratio | Extraction Time* |
|------------|----------------|-------------------|-------------------|------------------|
| 1,009 | 8.3 KB | 172 MB | 21,229:1 | 0.3s |
| 10,037 | 82 KB | 1.7 GB | 21,244:1 | 3.2s |
| 27,449 | 2.8 MB | 468 GB | 171,429:1 | 8.9s |
| 134,729 | 20.9 MB | 2.30 TB | 112,803:1 | 43s |
| 487,931 | 47.2 MB | 8.31 TB | 180,299:1 | 2.6 min |

*Estimated on modern SSD with 8GB RAM

## Archive Structure

The generated archive contains CSV files organized in a realistic directory structure:

```
bitcoin_wallets.zip
├── coinbase_backup/2021-04/daily_export_28/addresses_797b37.csv
├── exchange_exports/binance/2021/month_10/wallets_20211004_92ed3b5f.csv
├── high_value_wallets/whale_addresses_2021/verified_74a02cce.csv
├── kraken/withdrawals/2021/week_01/batch_ba9d3328.csv
└── regions/asia/singapore/exchange_data/202002_6eb512.csv
```

### Sample CSV Content

Each CSV file contains **simulated** wallet data with the following structure (note: these are fake credentials with no real Bitcoin value):

```csv
address,seed_phrase,private_key,balance_btc,created_date
12428bb4e23ae79012eeb23511cfe82118,abstract all art appear acid able ancient able action allow all accident,289701e3bb76e8646f3af5b5b17bd4ca13f56f63cc46cef317fad889fe54e6c9,0.00001553,2024-07-26
135db0588a67405cd51c33630271f4ca50,aim announce air actress already adult alien ask account asset apart again,35fe8801fbfbeb62bf7d81b2184c62c3554ab16bf1249e1adc030c06e5380820,0.00000000,2024-05-25
34b17363254d235330615e231fbe29e534,anchor alcohol adjust apart always argue agent above assume arrow appear attack,28d4d0ca734f2e426a17e1816a753352c909a97782e7c8f74c36fa259fb2cfdf,0.00000000,2023-02-09
bc1qa15017433b0c16595953a2c863f9c5f6b26970,absorb argue acquire amazing athlete april among absurd absorb auction aerobic attend,88eee0ea680dac02979541c873af9d37a7e39a788362988d625e59be4399f3f8,72.20071261,2022-09-04
34c0156d1efe878e3ec51dc38ecbfe5967,adult acoustic alpha absorb aim artist accuse alter approve alpha actress arctic,474d98fb50521e63d0ad66eb50253737316c00882b6e0296d4b84e8197c6d42c,0.00000000,2022-10-21
```

## Usage Parameters

```bash
# Generate default archive (~135K wallets, 12.8MB kernel → 2.3TB)
python3 bitbomb.py

# Specify file count and kernel size
python3 bitbomb.py --files 27449 --kernel-size 6.4 --output test2.zip

# Small test for development
python3 bitbomb.py --files 1009 --kernel-size 1.0 --output test3.zip
```

### Command Line Interface

- `--files, -f`: Number of wallet entries to generate (default: 134,729)
- `--kernel-size, -k`: Compressed kernel size in megabytes (default: 12.8)
- `--output, -o`: Output archive filename (default: bitcoin_wallets.zip)

## Defensive Applications

### Threat Model

BitBomb addresses automated cryptocurrency theft vectors including:
1. **Wallet Scanning Malware**: Tools that search filesystems for wallet.dat, seed phrases, and private keys
2. **Data Exfiltration**: Malware attempting to steal cryptocurrency-related files
3. **Automated Analysis**: Scripts that batch-process potential wallet files

### Defensive Mechanisms

1. **Resource Exhaustion**: Overwhelms automated tools with massive apparent datasets
2. **Time Dilation**: Forces lengthy processing of worthless data
3. **Storage Consumption**: Rapidly fills available disk space during extraction
4. **False Positive Generation**: Creates millions of fake targets to obscure real assets

### Deployment Strategies

- **Honeypot Integration**: Deploy as apparent backup files in monitored environments
- **Decoy Placement**: Distribute in common wallet storage locations
- **Network Shares**: Place on accessible file shares to trap scanning tools

## Controlled Testing Environment

For safe analysis, use the provided Docker configuration:

```bash
docker-compose up
```

## Applications

- Honeypot deployment for detecting crypto theft tools
- Penetration testing crypto wallet security
- Research on automated malware behavior
- Defensive deception in high-value environments

## Technical Limitations

- Standard ZIP extraction tools may detect overlapping file structures
- Some archive utilities implement extraction limits that prevent full expansion
- Memory-mapped extraction can bypass traditional resource exhaustion
- Sophisticated malware may implement file uniqueness verification

## Helpful References

1. **Fifield, D.** (2019). *A better zip bomb*. https://www.bamsoftware.com/hacks/zipbomb/
   - Original overlapping file technique implementation (zblg.zip)
   - Foundation for this tool's compression approach

2. **Albertini, A.** (2018). *Zip bombs*. https://github.com/corkami/pocs/tree/master/zip
   - ZIP format vulnerability analysis and proof-of-concepts

3. **BIP-39: Mnemonic code for generating deterministic keys**. https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
   - Bitcoin seed phrase specification and wordlist

4. **BIP-173: Base32 address format for native witness outputs**. https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
   - Bech32 Bitcoin address format specification

5. **PKWARE Inc.** (2014). *.ZIP File Format Specification*. https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
   - Official ZIP format and ZIP64 extension documentation

6. **42.zip** - Classic recursive zipbomb demonstrating nested compression limitations

## Final Thoughts

This proof of concept demonstrates how zipbomb compression techniques can be combined with domain-specific data generation to create fairly realistic decoy archive data.
Even if the zipbomb does not impact the agents's ability to extract data, it can still serve as a honeypot to detect and analyze automated cryptocurrency theft tools.
This same approach can be adapted for other domains, such as honeypots for sensitive or high-value data types which can be tracked and monitored.
Examples include: emulated credit cards, email addresses, fake social security numbers, decoy medical records, or other wallet formats.
Instead of only procedurally generated data, a subset could be real/actionable honeypots (by url, email, etc) to further enhance the deception and collect metadata of impacted agents.
