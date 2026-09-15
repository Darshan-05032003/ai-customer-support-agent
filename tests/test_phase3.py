"""
Phase 3 tests - conversation reconstruction, customer extraction, and annotation.
"""

import pytest
import json
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, validate_raw_data


class TestConversationReconstruction:
    """Test the production conversation reconstruction."""

    def test_conversations_file_exists(self):
        """Reconstructed conversations file should exist."""
        path = Path("data/processed/amazonhelp_conversations.jsonl")
        assert path.exists(), f"Missing: {path}"

    def test_conversations_manifest_exists(self):
        """Manifest should exist with metadata."""
        path = Path("data/processed/amazonhelp_conversations_manifest.json")
        assert path.exists(), f"Missing: {path}"

    def test_manifest_valid_json(self):
        """Manifest should be valid JSON."""
        with open("data/processed/amazonhelp_conversations_manifest.json") as f:
            manifest = json.load(f)

        assert "total_conversations" in manifest
        assert "total_messages" in manifest
        assert manifest["total_conversations"] == 45162
        assert manifest["total_messages"] == 289981

    def test_conversations_have_required_fields(self):
        """Each conversation should have required fields."""
        with open("data/processed/amazonhelp_conversations.jsonl") as f:
            for i, line in enumerate(f):
                record = json.loads(line)

                assert "conversation_id" in record
                assert "brand" in record
                assert "messages" in record
                assert record["brand"] == "AmazonHelp"

                if i >= 10:  # Check first 10
                    break

    def test_all_conversations_have_messages(self):
        """Every conversation should have 3+ messages."""
        with open("data/processed/amazonhelp_conversations.jsonl") as f:
            for i, line in enumerate(f):
                record = json.loads(line)
                messages = record["messages"]

                assert len(messages) >= 3, f"Conv {i} has {len(messages)} messages"

                if i >= 100:
                    break

    def test_conversations_have_customer_and_brand(self):
        """Every conversation must have customer and brand messages."""
        with open("data/processed/amazonhelp_conversations.jsonl") as f:
            for i, line in enumerate(f):
                record = json.loads(line)
                messages = record["messages"]

                roles = [m["role"] for m in messages]

                assert "customer" in roles, f"Conv {i} missing customer"
                assert "brand" in roles, f"Conv {i} missing brand"

                if i >= 100:
                    break

    def test_messages_have_required_fields(self):
        """Each message should have required schema fields."""
        required = ["tweet_id", "author_id", "role", "timestamp", "text", "parent_tweet_id"]

        with open("data/processed/amazonhelp_conversations.jsonl") as f:
            record = json.loads(f.readline())
            for msg in record["messages"]:
                for field in required:
                    assert field in msg, f"Missing {field} in message"

    def test_no_duplicate_conversations(self):
        """No conversation ID should appear twice."""
        conv_ids = set()

        with open("data/processed/amazonhelp_conversations.jsonl") as f:
            for line in f:
                record = json.loads(line)
                conv_id = record["conversation_id"]

                assert conv_id not in conv_ids, f"Duplicate conversation: {conv_id}"
                conv_ids.add(conv_id)

        assert len(conv_ids) == 45162


class TestCustomerMessageExtraction:
    """Test customer message extraction and splitting."""

    def test_customer_messages_file_exists(self):
        """Full customer messages file should exist."""
        assert Path("data/processed/amazonhelp_customer_messages.jsonl").exists()

    def test_customer_messages_count(self):
        """Should have correct number of customer messages."""
        count = sum(1 for _ in open("data/processed/amazonhelp_customer_messages.jsonl"))
        assert count == 162562

    def test_split_files_exist(self):
        """All split files should exist."""
        for split in ["train", "val", "test"]:
            path = Path(f"data/processed/amazonhelp_customer_messages_{split}.jsonl")
            assert path.exists(), f"Missing: {path}"

    def test_split_counts(self):
        """Splits should have expected counts."""
        train = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_train.jsonl"))
        val = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_val.jsonl"))
        test = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_test.jsonl"))

        assert train == 130350
        assert val == 15868
        assert test == 16344

    def test_split_proportions(self):
        """Split proportions should be approximately 80/10/10."""
        train = 130350
        val = 15868
        test = 16344
        total = train + val + test

        train_pct = 100.0 * train / total
        val_pct = 100.0 * val / total
        test_pct = 100.0 * test / total

        assert 79 < train_pct < 81
        assert 9 < val_pct < 11
        assert 9 < test_pct < 11

    def test_split_no_overlap(self):
        """No conversation ID should appear in multiple splits."""
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

        # Check no overlap
        assert len(train_convs & val_convs) == 0
        assert len(train_convs & test_convs) == 0
        assert len(val_convs & test_convs) == 0

    def test_split_manifest_valid(self):
        """Split manifest should be valid."""
        with open("data/processed/split_manifest.json") as f:
            manifest = json.load(f)

        assert "splits" in manifest
        assert "train" in manifest["splits"]
        assert "validation" in manifest["splits"]
        assert "test" in manifest["splits"]

        assert manifest["non_overlap_verified"] == True


class TestGoldenCandidates:
    """Test Golden Set candidate selection."""

    def test_golden_candidates_exist(self):
        """Golden candidates file should exist."""
        assert Path("data/evaluation/golden_candidates.jsonl").exists()

    def test_golden_candidates_count(self):
        """Should have between 200-500 candidates."""
        count = sum(1 for _ in open("data/evaluation/golden_candidates.jsonl"))
        assert 200 <= count <= 500, f"Got {count} candidates"

    def test_golden_candidates_schema(self):
        """Each candidate should have required schema."""
        required = ["conversation_id", "brand", "messages", "metadata", "annotation"]

        with open("data/evaluation/golden_candidates.jsonl") as f:
            for i, line in enumerate(f):
                record = json.loads(line)

                for field in required:
                    assert field in record, f"Missing {field} in candidate {i}"

                # Annotation should have null labels (not yet filled)
                anno = record["annotation"]
                assert anno["primary_intent"] is None
                assert anno["secondary_intent"] is None
                assert anno["is_ambiguous"] is None
                assert anno["escalation_required"] is None

                if i >= 10:
                    break

    def test_golden_template_exists(self):
        """Golden annotation template should exist."""
        assert Path("data/evaluation/golden_annotation_template.jsonl").exists()

    def test_golden_candidates_from_valid_convs(self):
        """All golden candidates should be from reconstructed conversations."""
        # Load valid conversation IDs
        valid_convs = set()
        with open("data/processed/amazonhelp_conversations.jsonl") as f:
            for line in f:
                record = json.loads(line)
                valid_convs.add(record["conversation_id"])

        # Check candidates
        with open("data/evaluation/golden_candidates.jsonl") as f:
            for line in f:
                record = json.loads(line)
                conv_id = record["conversation_id"]

                assert conv_id in valid_convs, f"Invalid conv_id: {conv_id}"


class TestAnnotationGuidelines:
    """Test annotation guideline files exist."""

    def test_golden_guidelines_exist(self):
        """Golden Set annotation guidelines should exist."""
        assert Path("reports/golden_set_annotation_guidelines.md").exists()

    def test_escalation_guidelines_exist(self):
        """Escalation annotation guidelines should exist."""
        assert Path("reports/escalation_annotation_guidelines.md").exists()

    def test_response_rubric_exists(self):
        """Response evaluation rubric should exist."""
        assert Path("reports/response_evaluation_rubric.md").exists()


class TestPhase3Foundation:
    """Test Phase 3 foundational requirements."""

    def test_raw_data_unchanged(self):
        """Raw data checksum should match."""
        import subprocess

        result = subprocess.run(
            ["md5sum", "archive/twcs/twcs.csv"],
            capture_output=True, text=True
        )
        actual = result.stdout.split()[0]

        # Expected from Phase 1
        expected = "73e961b2837626de89618a3f35f7bd6c"

        assert actual == expected, "Raw data was modified!"

    def test_phase1_tests_still_pass(self):
        """Phase 1 tests should still pass."""
        # This is tested separately, but check critical Phase 1 data
        df = load_raw_data()
        validate_raw_data(df)

        assert len(df) == 2811774
        amazon_tweets = df[(df['inbound'] == False) & (df['author_id'] == 'AmazonHelp')]
        assert len(amazon_tweets) == 169840

    def test_no_secrets_in_code(self):
        """No API keys or secrets should be in scripts."""
        import os

        bad_patterns = ["OPENAI_API_KEY", "api_key=", "SECRET=", "password="]

        for root, dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file)) as f:
                        content = f.read()
                        for pattern in bad_patterns:
                            assert pattern not in content, f"Found {pattern} in {file}"

    def test_conversations_statistics_reasonable(self):
        """Conversation statistics should be reasonable."""
        with open("data/processed/amazonhelp_conversations_manifest.json") as f:
            manifest = json.load(f)

        # All conversations should be 3+ messages
        assert manifest["thread_types"]["two_message_threads"] == 0
        assert manifest["thread_types"]["three_plus_message_threads"] == 45162

        # Avg should be > 3
        assert manifest["conversation_statistics"]["mean_length"] > 3

        # 98%+ should have 2+ customer turns
        assert manifest["customer_turn_analysis"]["threads_with_2plus_customer_turns_pct"] > 98


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
