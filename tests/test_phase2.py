"""
Phase 2 tests - conversation extraction and intent discovery.
"""

import pytest
import pandas as pd
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, get_brand_tweets
from src.preprocessing.conversations import ConversationReconstructor, extract_customer_messages


class TestPhase2Foundation:
    """Test Phase 2 infrastructure."""

    def test_raw_data_unchanged(self):
        """Raw data should not be modified."""
        checksum_file = Path("/tmp/raw_data_checksum_before.txt")
        if checksum_file.exists():
            # Read expected checksum
            with open(checksum_file) as f:
                expected = f.read().strip()

            # Verify current checksum
            import subprocess
            result = subprocess.run(
                ["md5sum", "archive/twcs/twcs.csv"],
                capture_output=True, text=True
            )
            actual = result.stdout.strip()

            assert expected == actual, f"Raw data was modified!\nExpected: {expected}\nActual: {actual}"

    def test_amazonhelp_exists(self):
        """AmazonHelp brand should exist in dataset."""
        df = load_raw_data()
        amazon_tweets = get_brand_tweets(df, "AmazonHelp")
        assert len(amazon_tweets) > 0
        assert len(amazon_tweets) >= 169000  # From Phase 1 audit

    def test_processed_data_exists(self):
        """Processed data files should exist."""
        processed_dir = Path("data/processed")
        assert processed_dir.exists()

        assert (processed_dir / "intent_taxonomy.json").exists()
        assert (processed_dir / "amazonhelp_customer_messages_train.jsonl").exists()
        assert (processed_dir / "amazonhelp_customer_messages_val.jsonl").exists()
        assert (processed_dir / "amazonhelp_customer_messages_test.jsonl").exists()

    def test_intent_taxonomy_valid(self):
        """Intent taxonomy should be valid JSON with required fields."""
        with open("data/processed/intent_taxonomy.json") as f:
            taxonomy = json.load(f)

        assert "intents" in taxonomy
        assert "version" in taxonomy
        assert "brand" in taxonomy
        assert taxonomy["brand"] == "AmazonHelp"

        # Each intent should have required fields
        for intent in taxonomy["intents"]:
            assert "id" in intent
            assert "name" in intent
            assert "keywords" in intent
            assert isinstance(intent["keywords"], list)

    def test_intent_taxonomy_size(self):
        """Intent taxonomy should have reasonable number of intents."""
        with open("data/processed/intent_taxonomy.json") as f:
            taxonomy = json.load(f)

        n_intents = len(taxonomy["intents"])
        assert 5 <= n_intents <= 20, f"Expected 5-20 intents, got {n_intents}"

    def test_intent_ids_unique(self):
        """Intent IDs should be unique."""
        with open("data/processed/intent_taxonomy.json") as f:
            taxonomy = json.load(f)

        ids = [i["id"] for i in taxonomy["intents"]]
        assert len(ids) == len(set(ids)), "Duplicate intent IDs found"


class TestConversationExtraction:
    """Test conversation extraction."""

    def test_train_split_exists_and_valid(self):
        """Train split should exist with valid data."""
        train_path = Path("data/processed/amazonhelp_customer_messages_train.jsonl")
        assert train_path.exists()

        with open(train_path) as f:
            lines = [json.loads(line) for line in f]

        assert len(lines) > 0
        assert len(lines) > 70000  # Should be ~80k

        # Each record should have required fields
        for record in lines[:10]:
            assert "tweet_id" in record
            assert "customer_id" in record
            assert "text" in record
            assert "conversation_id" in record

    def test_val_split_exists(self):
        """Val split should exist."""
        val_path = Path("data/processed/amazonhelp_customer_messages_val.jsonl")
        assert val_path.exists()

        with open(val_path) as f:
            lines = f.readlines()

        assert len(lines) > 5000

    def test_test_split_exists(self):
        """Test split should exist."""
        test_path = Path("data/processed/amazonhelp_customer_messages_test.jsonl")
        assert test_path.exists()

        with open(test_path) as f:
            lines = f.readlines()

        assert len(lines) > 5000

    def test_splits_non_overlapping(self):
        """Train/val/test splits should not overlap at conversation level."""
        train_convs = set()
        val_convs = set()
        test_convs = set()

        with open("data/processed/amazonhelp_customer_messages_train.jsonl") as f:
            for line in f:
                record = json.loads(line)
                train_convs.add(record["conversation_id"])

        with open("data/processed/amazonhelp_customer_messages_val.jsonl") as f:
            for line in f:
                record = json.loads(line)
                val_convs.add(record["conversation_id"])

        with open("data/processed/amazonhelp_customer_messages_test.jsonl") as f:
            for line in f:
                record = json.loads(line)
                test_convs.add(record["conversation_id"])

        # No overlap
        assert len(train_convs & val_convs) == 0
        assert len(train_convs & test_convs) == 0
        assert len(val_convs & test_convs) == 0

    def test_split_proportions(self):
        """Splits should be approximately 80/10/10."""
        train_count = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_train.jsonl"))
        val_count = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_val.jsonl"))
        test_count = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_test.jsonl"))

        total = train_count + val_count + test_count

        train_pct = 100.0 * train_count / total
        val_pct = 100.0 * val_count / total
        test_pct = 100.0 * test_count / total

        # Within 1% of target
        assert 79 < train_pct < 81
        assert 9 < val_pct < 11
        assert 9 < test_pct < 11


class TestConversationReconstruction:
    """Test conversation reconstruction logic."""

    def test_reconstructor_init(self):
        """Reconstructor should initialize without errors."""
        df = load_raw_data("archive/sample.csv")  # Use sample
        reconstructor = ConversationReconstructor(df, "AppleSupport")
        assert reconstructor is not None

    def test_find_root_handles_missing_refs(self):
        """Root finding should handle missing parent references gracefully."""
        df = load_raw_data("archive/sample.csv")
        reconstructor = ConversationReconstructor(df, "AppleSupport")
        reconstructor.build_lookups()

        # Try to find root for a sample tweet
        if len(reconstructor.tweet_lookup) > 0:
            sample_id = list(reconstructor.tweet_lookup.keys())[0]
            root = reconstructor.find_conversation_root(sample_id)
            # Should not crash
            assert root is None or isinstance(root, int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
