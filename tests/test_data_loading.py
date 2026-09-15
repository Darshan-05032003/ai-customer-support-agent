"""
Tests for data loading and validation.
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def archive_dir():
    """Get archive directory path."""
    return Path(__file__).parent.parent / "archive"


@pytest.fixture
def main_dataset(archive_dir):
    """Load main TWCS dataset."""
    csv_path = archive_dir / "twcs" / "twcs.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None


@pytest.fixture
def sample_dataset(archive_dir):
    """Load sample dataset."""
    csv_path = archive_dir / "sample.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None


class TestDataDiscovery:
    """Test data file discovery and basic loading."""

    def test_archive_dir_exists(self, archive_dir):
        """Archive directory should exist."""
        assert archive_dir.exists(), f"Archive directory not found: {archive_dir}"

    def test_main_dataset_exists(self, archive_dir):
        """Main TWCS dataset file should exist."""
        csv_path = archive_dir / "twcs" / "twcs.csv"
        assert csv_path.exists(), f"Main dataset not found: {csv_path}"

    def test_sample_dataset_exists(self, archive_dir):
        """Sample dataset file should exist."""
        csv_path = archive_dir / "sample.csv"
        assert csv_path.exists(), f"Sample dataset not found: {csv_path}"


class TestMainDataset:
    """Test main dataset structure and integrity."""

    def test_main_dataset_loads(self, main_dataset):
        """Main dataset should load without errors."""
        assert main_dataset is not None
        assert len(main_dataset) > 0

    def test_main_dataset_has_required_columns(self, main_dataset):
        """Main dataset should have all required columns."""
        required = ['tweet_id', 'author_id', 'inbound', 'created_at', 'text',
                    'response_tweet_id', 'in_response_to_tweet_id']
        assert all(col in main_dataset.columns for col in required)

    def test_main_dataset_row_count(self, main_dataset):
        """Main dataset should have expected row count."""
        # From audit: 2,811,774 rows
        assert len(main_dataset) == 2811774

    def test_tweet_id_is_unique(self, main_dataset):
        """tweet_id should be unique primary key."""
        assert main_dataset['tweet_id'].duplicated().sum() == 0
        assert main_dataset['tweet_id'].isna().sum() == 0

    def test_no_full_row_duplicates(self, main_dataset):
        """Dataset should have no duplicate rows."""
        assert main_dataset.duplicated().sum() == 0

    def test_inbound_is_boolean(self, main_dataset):
        """inbound column should be boolean."""
        assert main_dataset['inbound'].dtype == bool

    def test_inbound_distribution(self, main_dataset):
        """inbound should be balanced (roughly 50/50)."""
        inbound_count = main_dataset['inbound'].sum()
        outbound_count = (~main_dataset['inbound']).sum()
        assert inbound_count == 1537843
        assert outbound_count == 1273931

    def test_text_field_not_empty(self, main_dataset):
        """text field should not have empty strings."""
        assert main_dataset['text'].isna().sum() == 0
        # Very few extremely short texts
        assert (main_dataset['text'].str.len() <= 5).sum() < 100

    def test_author_id_no_nulls(self, main_dataset):
        """author_id should have no nulls."""
        assert main_dataset['author_id'].isna().sum() == 0


class TestConversationLinkage:
    """Test conversation reconstruction capability."""

    def test_references_mostly_in_dataset(self, main_dataset):
        """Most in_response_to refs should exist in dataset."""
        all_tweet_ids = set(main_dataset['tweet_id'].astype(int).unique())
        response_refs = main_dataset['in_response_to_tweet_id'].dropna().astype(int)
        refs_found = response_refs.isin(all_tweet_ids).sum()
        pct_found = 100.0 * refs_found / len(response_refs)
        # From audit: 99.8%
        assert pct_found > 99.5

    def test_inbound_replies_have_responses(self, main_dataset):
        """Most inbound tweets should have responses."""
        inbound = main_dataset[main_dataset['inbound'] == True]
        with_response = inbound['response_tweet_id'].notna().sum()
        pct = 100.0 * with_response / len(inbound)
        # From audit: 84.8%
        assert pct > 80


class TestBrands:
    """Test brand identification and statistics."""

    def test_brand_outbound_only(self, main_dataset):
        """Brand author_ids should only appear in outbound tweets."""
        outbound = main_dataset[main_dataset['inbound'] == False]
        inbound = main_dataset[main_dataset['inbound'] == True]

        outbound_authors = set(outbound['author_id'].unique())
        inbound_authors = set(inbound['author_id'].unique())
        overlap = outbound_authors & inbound_authors
        # From audit: 0
        assert len(overlap) == 0

    def test_brand_count(self, main_dataset):
        """Should have 108 unique brands."""
        outbound = main_dataset[main_dataset['inbound'] == False]
        brand_count = outbound['author_id'].nunique()
        assert brand_count == 108

    def test_top_brand_is_amazonhelp(self, main_dataset):
        """AmazonHelp should be the top brand by tweet count."""
        outbound = main_dataset[main_dataset['inbound'] == False]
        top_brand = outbound['author_id'].value_counts().index[0]
        assert top_brand == "AmazonHelp"


class TestSampleDataset:
    """Test sample dataset structure."""

    def test_sample_dataset_loads(self, sample_dataset):
        """Sample dataset should load without errors."""
        assert sample_dataset is not None
        assert len(sample_dataset) > 0

    def test_sample_schema_matches_main(self, main_dataset, sample_dataset):
        """Sample should have same schema as main."""
        assert list(sample_dataset.columns) == list(main_dataset.columns)

    def test_sample_row_count(self, sample_dataset):
        """Sample should have 93 rows."""
        assert len(sample_dataset) == 93

    def test_sample_has_no_duplicates(self, sample_dataset):
        """Sample should have no duplicate tweet_ids."""
        assert sample_dataset['tweet_id'].duplicated().sum() == 0


class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_response_to_less_than_total(self, main_dataset):
        """Less than 100% should have in_response_to (ok for conversation starters)."""
        has_response_to = main_dataset['in_response_to_tweet_id'].notna().sum()
        pct = 100.0 * has_response_to / len(main_dataset)
        # From audit: 71.7%
        assert 70 < pct < 75

    def test_response_field_less_than_total(self, main_dataset):
        """Less than 100% should have response_tweet_id (ok for unanswered)."""
        has_response = main_dataset['response_tweet_id'].notna().sum()
        pct = 100.0 * has_response / len(main_dataset)
        # From audit: 63.0%
        assert 60 < pct < 65

    def test_no_missing_text(self, main_dataset):
        """No tweet should have empty text."""
        assert main_dataset['text'].isna().sum() == 0
        assert (main_dataset['text'].str.len() > 0).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
