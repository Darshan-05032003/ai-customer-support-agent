"""
Data loading utilities for Hiver assignment.

Handles loading and basic validation of the Customer Support on Twitter dataset.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Set


def load_raw_data(data_path: str = "archive/twcs/twcs.csv") -> pd.DataFrame:
    """
    Load the raw Twitter Customer Support dataset.

    Args:
        data_path: Path to the CSV file (relative to project root)

    Returns:
        DataFrame with all tweets

    Raises:
        FileNotFoundError: If the dataset file doesn't exist
    """
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")

    df = pd.read_csv(path)
    return df


def build_tweet_lookup(df: pd.DataFrame) -> Dict[int, dict]:
    """
    Build a fast lookup dictionary from tweet_id to tweet record.

    Args:
        df: DataFrame with tweets

    Returns:
        Dictionary mapping tweet_id to tweet data
    """
    lookup = {}
    for idx, row in df.iterrows():
        tweet_id = int(row['tweet_id'])
        lookup[tweet_id] = row.to_dict()
    return lookup


def get_brand_tweets(df: pd.DataFrame, brand_name: str = "AmazonHelp") -> pd.DataFrame:
    """
    Extract all tweets from a specific brand.

    Args:
        df: DataFrame with all tweets
        brand_name: Brand author_id to filter

    Returns:
        DataFrame with brand's outbound tweets
    """
    brand_tweets = df[(df['inbound'] == False) & (df['author_id'] == brand_name)]
    return brand_tweets


def get_brand_tweet_ids(df: pd.DataFrame, brand_name: str = "AmazonHelp") -> Set[int]:
    """
    Get set of all tweet IDs belonging to a brand.

    Args:
        df: DataFrame with all tweets
        brand_name: Brand author_id to filter

    Returns:
        Set of tweet IDs
    """
    brand_tweets = get_brand_tweets(df, brand_name)
    return set(brand_tweets['tweet_id'].astype(int).values)


def validate_raw_data(df: pd.DataFrame) -> bool:
    """
    Validate that the raw data has expected structure.

    Args:
        df: DataFrame to validate

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    required_columns = [
        'tweet_id', 'author_id', 'inbound', 'created_at',
        'text', 'response_tweet_id', 'in_response_to_tweet_id'
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Check tweet_id uniqueness
    if df['tweet_id'].duplicated().any():
        raise ValueError("Duplicate tweet_ids found in dataset")

    return True
