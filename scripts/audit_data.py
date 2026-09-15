#!/usr/bin/env python3
"""
Data audit script for Hiver SDE assignment.

Inspects the Customer Support on Twitter dataset without modifying raw files.
Produces comprehensive statistics on dataset structure, schema, brands, and conversation links.
"""

import os
import sys
import pandas as pd
from pathlib import Path


def find_raw_data(archive_dir="archive"):
    """Discover raw data files in archive directory."""
    archive_path = Path(archive_dir)

    if not archive_path.exists():
        print(f"ERROR: Archive directory not found: {archive_path}")
        sys.exit(1)

    files = {}

    # Look for CSV files
    for csv_file in archive_path.rglob("*.csv"):
        relative = csv_file.relative_to(archive_path)
        file_size_mb = csv_file.stat().st_size / (1024 ** 2)
        files[str(relative)] = {
            "path": csv_file,
            "size_mb": file_size_mb,
        }

    return files


def audit_csv(filepath, name):
    """Audit a single CSV file."""
    print(f"\n{'=' * 70}")
    print(f"FILE: {name}")
    print(f"{'=' * 70}")

    file_size_mb = filepath.stat().st_size / (1024 ** 2)
    print(f"File size: {file_size_mb:.1f} MB")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"ERROR reading file: {e}")
        return None

    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    print(f"\n--- Data types ---")
    print(df.dtypes)

    print(f"\n--- Missing values ---")
    for col in df.columns:
        missing = df[col].isna().sum()
        pct = 100.0 * missing / len(df) if len(df) > 0 else 0
        print(f"  {col:30s}: {missing:>10,} ({pct:>6.2f}%)")

    print(f"\n--- Duplicates ---")
    full_dupes = df.duplicated().sum()
    print(f"  Full row duplicates: {full_dupes:,}")

    # Check for primary key
    if 'tweet_id' in df.columns:
        tweet_id_dupes = df['tweet_id'].duplicated().sum()
        print(f"  Duplicate tweet_ids: {tweet_id_dupes:,}")

    print(f"\n--- Sample rows (first 2) ---")
    print(df.head(2).to_string())

    return df


def analyze_main_dataset(df):
    """Analyze the main TWCS dataset structure and brands."""
    if df is None:
        return

    print(f"\n{'=' * 70}")
    print(f"MAIN DATASET ANALYSIS")
    print(f"{'=' * 70}")

    # Inbound/outbound distribution
    if 'inbound' in df.columns:
        print(f"\n--- Inbound/Outbound distribution ---")
        inbound_dist = df['inbound'].value_counts()
        print(inbound_dist)
        print(f"  Inbound (customers): {inbound_dist[True]:>10,}")
        print(f"  Outbound (brands):   {inbound_dist[False]:>10,}")

        inbound = df[df['inbound'] == True]
        outbound = df[df['inbound'] == False]
    else:
        inbound = df
        outbound = df

    # Brand analysis
    if 'author_id' in df.columns:
        print(f"\n--- Author/Brand analysis ---")
        print(f"  Total unique authors: {df['author_id'].nunique():,}")

        if 'inbound' in df.columns:
            print(f"  Unique inbound authors (customers): {inbound['author_id'].nunique():,}")
            print(f"  Unique outbound authors (brands): {outbound['author_id'].nunique():,}")

            brand_counts = outbound['author_id'].value_counts()
            print(f"\n  Top 20 brands by outbound tweet count:")
            for brand, count in brand_counts.head(20).items():
                print(f"    {brand:30s} {count:>8,}")

            print(f"\n  Brand size distribution:")
            print(f"    Brands with 1000+ tweets: {(brand_counts >= 1000).sum()}")
            print(f"    Brands with 500+ tweets:  {(brand_counts >= 500).sum()}")
            print(f"    Brands with 100+ tweets:  {(brand_counts >= 100).sum()}")

            # Check for author overlap
            inbound_authors = set(inbound['author_id'].unique())
            outbound_authors = set(outbound['author_id'].unique())
            overlap = inbound_authors & outbound_authors
            print(f"    Authors in both inbound and outbound: {len(overlap)}")

    # Conversation structure
    print(f"\n--- Conversation structure ---")

    if 'in_response_to_tweet_id' in df.columns:
        has_response_to = df['in_response_to_tweet_id'].notna().sum()
        pct = 100.0 * has_response_to / len(df)
        print(f"  Tweets with in_response_to_tweet_id: {has_response_to:,} ({pct:.1f}%)")

    if 'response_tweet_id' in df.columns:
        has_response = df['response_tweet_id'].notna().sum()
        pct = 100.0 * has_response / len(df)
        print(f"  Tweets with response_tweet_id: {has_response:,} ({pct:.1f}%)")

        # Check for multiple responses (comma-separated)
        multi_response = df[df['response_tweet_id'].notna()]['response_tweet_id'].str.contains(',', na=False)
        print(f"  Tweets with multiple responses: {multi_response.sum():,}")

    # Can conversations be reconstructed?
    print(f"\n--- Conversation linkage ---")
    if 'in_response_to_tweet_id' in df.columns and 'tweet_id' in df.columns:
        all_tweet_ids = set(df['tweet_id'].astype(int).unique())
        response_refs = df['in_response_to_tweet_id'].dropna().astype(int)
        refs_found = response_refs.isin(all_tweet_ids).sum()
        refs_missing = len(response_refs) - refs_found
        pct_found = 100.0 * refs_found / len(response_refs)
        pct_missing = 100.0 * refs_missing / len(response_refs)
        print(f"  in_response_to refs found in dataset: {refs_found:,} ({pct_found:.1f}%)")
        print(f"  in_response_to refs missing:          {refs_missing:,} ({pct_missing:.1f}%)")
        print(f"  → Conversations can be reconstructed reliably: {'YES' if pct_found > 99 else 'PARTIAL'}")

    if 'inbound' in df.columns:
        inbound_with_response = inbound[inbound['response_tweet_id'].notna()]
        pct = 100.0 * len(inbound_with_response) / len(inbound)
        print(f"  Inbound tweets with >= 1 response: {len(inbound_with_response):,} ({pct:.1f}%)")

        outbound_replies = outbound[outbound['in_response_to_tweet_id'].notna()]
        pct = 100.0 * len(outbound_replies) / len(outbound)
        print(f"  Outbound (brand) tweets are replies: {len(outbound_replies):,} ({pct:.1f}%)")

    # Text analysis
    if 'text' in df.columns:
        print(f"\n--- Text field ---")
        text_lengths = df['text'].str.len()
        print(f"  Min length: {text_lengths.min()} chars")
        print(f"  Max length: {text_lengths.max()} chars")
        print(f"  Mean length: {text_lengths.mean():.1f} chars")
        print(f"  Median length: {text_lengths.median():.1f} chars")
        short_texts = (text_lengths <= 10).sum()
        print(f"  Texts <= 10 chars: {short_texts:,}")

    # Timestamp analysis
    if 'created_at' in df.columns:
        print(f"\n--- Timestamps ---")
        print(f"  First recorded: {df['created_at'].iloc[0]}")
        print(f"  Last recorded: {df['created_at'].iloc[-1]}")


def main():
    print("Hiver SDE Assignment - Data Audit")
    print(f"{'=' * 70}")

    # Find raw data files
    raw_files = find_raw_data("archive")

    if not raw_files:
        print("ERROR: No CSV files found in archive/")
        sys.exit(1)

    print(f"\nDiscovered {len(raw_files)} CSV file(s):\n")
    for name, info in sorted(raw_files.items()):
        print(f"  {name:40s} {info['size_mb']:>8.1f} MB")

    # Audit each file
    dfs = {}
    for name, info in sorted(raw_files.items()):
        df = audit_csv(info['path'], name)
        if df is not None:
            dfs[name] = df

    # Detailed analysis of main dataset (largest)
    if 'twcs/twcs.csv' in dfs:
        analyze_main_dataset(dfs['twcs/twcs.csv'])
    elif 'twcs.csv' in dfs:
        analyze_main_dataset(dfs['twcs.csv'])

    # Banking77 check
    print(f"\n{'=' * 70}")
    print(f"BANKING77 DATASET")
    print(f"{'=' * 70}")
    banking77_found = False
    for root, dirs, files in os.walk("."):
        for f in files:
            if 'banking' in f.lower() or 'bank77' in f.lower():
                print(f"  Found: {os.path.join(root, f)}")
                banking77_found = True

    if not banking77_found:
        print("  Status: NOT FOUND (not required for this phase)")
        print("  Note: Banking77 is optional per assignment description")

    print(f"\n{'=' * 70}")
    print("Audit complete.")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
