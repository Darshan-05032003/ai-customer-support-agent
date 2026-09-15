#!/usr/bin/env python3
"""
Phase 4 tests - intent discovery, taxonomy, annotation readiness.
"""

import pytest
import json
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, validate_raw_data


class TestIntentDiscovery:
    """Test intent discovery and taxonomy."""

    def test_intent_discovery_report_exists(self):
        """Intent discovery report should exist."""
        path = Path("reports/intent_discovery.json")
        assert path.exists(), f"Missing: {path}"

    def test_intent_discovery_valid_json(self):
        """Intent discovery report should be valid JSON."""
        with open("reports/intent_discovery.json") as f:
            report = json.load(f)

        assert "total_messages_analyzed" in report
        assert report["total_messages_analyzed"] == 162562
        assert "intent_categories" in report
        assert len(report["intent_categories"]) == 12

    def test_all_12_intents_present(self):
        """All 12 intents should be in discovery report."""
        with open("reports/intent_discovery.json") as f:
            report = json.load(f)

        expected_intents = [
            'GENERAL_INQUIRY', 'ORDER_STATUS', 'DELIVERY_ISSUE', 'PRIME_SUBSCRIPTION',
            'ACCOUNT_LOGIN', 'TECHNICAL_ISSUE', 'REFUND_RETURN', 'CUSTOMER_SERVICE_COMPLAINT',
            'BILLING_PAYMENT', 'PRODUCT_INFORMATION', 'SHIPPING_ADDRESS', 'DAMAGED_ITEM'
        ]

        for intent in expected_intents:
            assert intent in report["intent_categories"], f"Missing intent: {intent}"

    def test_intent_distribution_sums_to_total(self):
        """Intent message counts should sum to total."""
        with open("reports/intent_discovery.json") as f:
            report = json.load(f)

        total_messages = report["total_messages_analyzed"]
        sum_counts = sum(
            data["count"] for data in report["intent_categories"].values()
        )

        assert sum_counts == total_messages, f"Counts don't sum: {sum_counts} != {total_messages}"

    def test_intent_percentages_sum_to_100(self):
        """Intent percentages should sum to ~100%."""
        with open("reports/intent_discovery.json") as f:
            report = json.load(f)

        total_pct = sum(
            data["percentage"] for data in report["intent_categories"].values()
        )

        assert 99.5 < total_pct < 100.5, f"Percentages don't sum to 100: {total_pct}"

    def test_general_inquiry_dominant(self):
        """GENERAL_INQUIRY should be largest category."""
        with open("reports/intent_discovery.json") as f:
            report = json.load(f)

        gi_count = report["intent_categories"]["GENERAL_INQUIRY"]["count"]
        for intent, data in report["intent_categories"].items():
            if intent != "GENERAL_INQUIRY":
                assert data["count"] <= gi_count, f"{intent} larger than GENERAL_INQUIRY"

    def test_each_intent_has_keywords(self):
        """Each intent should have associated keywords."""
        with open("reports/intent_discovery.json") as f:
            report = json.load(f)

        for intent, data in report["intent_categories"].items():
            assert "keywords" in data, f"{intent} missing keywords"
            assert len(data["keywords"]) > 0, f"{intent} has no keywords"

    def test_each_intent_has_examples(self):
        """Each intent should have examples."""
        with open("reports/intent_discovery.json") as f:
            report = json.load(f)

        for intent, data in report["intent_categories"].items():
            assert "examples" in data, f"{intent} missing examples"
            assert len(data["examples"]) > 0, f"{intent} has no examples"


class TestIntentTaxonomy:
    """Test intent taxonomy documentation."""

    def test_taxonomy_file_exists(self):
        """Intent taxonomy markdown should exist."""
        path = Path("reports/intent_taxonomy.md")
        assert path.exists(), f"Missing: {path}"

    def test_taxonomy_comprehensive(self):
        """Taxonomy should document all 12 intents."""
        with open("reports/intent_taxonomy.md") as f:
            content = f.read()

        expected_intents = [
            'GENERAL_INQUIRY', 'ORDER_STATUS', 'DELIVERY_ISSUE', 'PRIME_SUBSCRIPTION',
            'ACCOUNT_LOGIN', 'TECHNICAL_ISSUE', 'REFUND_RETURN', 'CUSTOMER_SERVICE_COMPLAINT',
            'BILLING_PAYMENT', 'PRODUCT_INFORMATION', 'SHIPPING_ADDRESS', 'DAMAGED_ITEM'
        ]

        for intent in expected_intents:
            assert intent in content, f"Missing {intent} in taxonomy"

    def test_taxonomy_has_definitions(self):
        """Each intent should have a definition section."""
        with open("reports/intent_taxonomy.md") as f:
            content = f.read()

        assert "Definition:" in content or "definition" in content.lower()
        assert "Inclusion Criteria" in content
        assert "Exclusion Criteria" in content

    def test_taxonomy_has_boundary_cases(self):
        """Taxonomy should document boundary cases."""
        with open("reports/intent_taxonomy.md") as f:
            content = f.read()

        assert "Boundary" in content or "boundary" in content.lower()
        assert "Overlap" in content or "overlap" in content.lower()

    def test_taxonomy_distribution_table(self):
        """Taxonomy should include distribution summary."""
        with open("reports/intent_taxonomy.md") as f:
            content = f.read()

        assert "GENERAL_INQUIRY" in content and "52.6%" in content
        assert "ORDER_STATUS" in content and "14.8%" in content
        assert "DELIVERY_ISSUE" in content and "8.9%" in content


class TestGoldenCandidates:
    """Test reduced golden candidates."""

    def test_reduced_candidates_exist(self):
        """Reduced golden candidates file should exist."""
        path = Path("data/evaluation/golden_candidates_reduced.jsonl")
        assert path.exists(), f"Missing: {path}"

    def test_reduced_count_is_250(self):
        """Should have exactly 250 reduced candidates."""
        count = sum(1 for _ in open("data/evaluation/golden_candidates_reduced.jsonl"))
        assert count == 250, f"Expected 250, got {count}"

    def test_reduced_candidates_schema(self):
        """Reduced candidates should have required schema."""
        required = ["conversation_id", "brand", "messages", "metadata", "annotation"]

        with open("data/evaluation/golden_candidates_reduced.jsonl") as f:
            for i, line in enumerate(f):
                record = json.loads(line)

                for field in required:
                    assert field in record, f"Missing {field} in candidate {i}"

                if i >= 10:
                    break

    def test_reduction_summary_exists(self):
        """Reduction summary metadata should exist."""
        path = Path("data/evaluation/golden_reduction_summary.json")
        assert path.exists(), f"Missing: {path}"

    def test_reduction_summary_valid(self):
        """Reduction summary should be valid and complete."""
        with open("data/evaluation/golden_reduction_summary.json") as f:
            summary = json.load(f)

        assert summary["total_selected"] == 250
        assert "stratification" in summary
        assert "methodology" in summary
        assert "seed" in summary
        assert summary["seed"] == 42

    def test_stratification_maintained(self):
        """Stratification should be maintained during reduction."""
        with open("data/evaluation/golden_reduction_summary.json") as f:
            summary = json.load(f)

        original = summary["original_distribution"]["by_length"]
        selected = summary["stratification"]["by_length"]

        # Check proportions are maintained (within 2%)
        for length_cat in original:
            orig_pct = 100.0 * original[length_cat] / sum(original.values())
            sel_pct = 100.0 * selected[length_cat] / sum(selected.values())

            assert abs(orig_pct - sel_pct) < 2.0, f"{length_cat} proportion changed: {orig_pct}% -> {sel_pct}%"

    def test_all_reduced_from_valid_convs(self):
        """All reduced candidates should be from valid conversations."""
        valid_convs = set()
        with open("data/processed/amazonhelp_conversations.jsonl") as f:
            for line in f:
                record = json.loads(line)
                valid_convs.add(record["conversation_id"])

        with open("data/evaluation/golden_candidates_reduced.jsonl") as f:
            for line in f:
                record = json.loads(line)
                conv_id = record["conversation_id"]

                assert conv_id in valid_convs, f"Invalid conv_id in reduced: {conv_id}"


class TestAnnotationInterface:
    """Test annotation Flask app and UI."""

    def test_app_file_exists(self):
        """Flask app should exist."""
        path = Path("app.py")
        assert path.exists(), f"Missing: {path}"

    def test_app_has_required_routes(self):
        """Flask app should have required routes."""
        with open("app.py") as f:
            content = f.read()

        required_routes = [
            '/api/candidate',
            '/api/annotate',
            '/api/progress',
            '/api/stats'
        ]

        for route in required_routes:
            assert route in content, f"Missing route: {route}"

    def test_template_file_exists(self):
        """HTML template should exist."""
        path = Path("templates/annotator.html")
        assert path.exists(), f"Missing: {path}"

    def test_template_has_form_elements(self):
        """Template should have annotation form elements."""
        with open("templates/annotator.html") as f:
            content = f.read()

        required = [
            'primaryIntent',
            'secondaryIntent',
            'escalation',
            'isAmbiguous',
            'annotationForm'
        ]

        for elem in required:
            assert elem in content, f"Missing form element: {elem}"

    def test_annotation_schema_in_app(self):
        """App should handle annotation schema."""
        with open("app.py") as f:
            content = f.read()

        # Should reference annotation fields
        assert "primary_intent" in content
        assert "escalation_required" in content
        assert "is_ambiguous" in content
        assert "annotator_notes" in content


class TestPhase4Foundation:
    """Test Phase 4 foundational requirements."""

    def test_raw_data_still_unchanged(self):
        """Raw data checksum should still match Phase 3."""
        import subprocess

        result = subprocess.run(
            ["md5sum", "archive/twcs/twcs.csv"],
            capture_output=True, text=True
        )
        actual = result.stdout.split()[0]
        expected = "73e961b2837626de89618a3f35f7bd6c"

        assert actual == expected, "Raw data was modified!"

    def test_conversation_data_intact(self):
        """Reconstructed conversation data should be intact."""
        with open("data/processed/amazonhelp_conversations_manifest.json") as f:
            manifest = json.load(f)

        assert manifest["total_conversations"] == 45162
        assert manifest["total_messages"] == 289981

    def test_customer_messages_intact(self):
        """Customer messages should be intact."""
        count = sum(1 for _ in open("data/processed/amazonhelp_customer_messages.jsonl"))
        assert count == 162562, f"Expected 162562 customer messages, got {count}"

    def test_splits_still_valid(self):
        """Train/val/test splits should still be valid."""
        train = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_train.jsonl"))
        val = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_val.jsonl"))
        test = sum(1 for _ in open("data/processed/amazonhelp_customer_messages_test.jsonl"))

        assert train == 130350
        assert val == 15868
        assert test == 16344

    def test_phase3_tests_still_pass(self):
        """Phase 3 foundation should still be valid."""
        df = load_raw_data()
        validate_raw_data(df)

        assert len(df) == 2811774
        amazon_tweets = df[(df['inbound'] == False) & (df['author_id'] == 'AmazonHelp')]
        assert len(amazon_tweets) == 169840

    def test_no_classifier_trained(self):
        """Classifier model should NOT be trained yet."""
        # Should not exist
        assert not Path("models/intent_classifier.pkl").exists()
        assert not Path("models/tfidf_vectorizer.pkl").exists()

    def test_discovery_scripts_executable(self):
        """Discovery scripts should exist and be valid Python."""
        scripts = [
            "scripts/semantic_intent_discovery.py",
            "scripts/reduce_golden_candidates.py"
        ]

        for script in scripts:
            path = Path(script)
            assert path.exists(), f"Missing: {script}"

            with open(script) as f:
                content = f.read()
                # Should have proper Python structure
                assert "#!/usr/bin/env python3" in content or "def main" in content

    def test_phase4_report_exists(self):
        """Phase 4 status report should exist."""
        path = Path("reports/phase4_status.md")
        assert path.exists(), f"Missing: {path}"

    def test_phase4_report_complete(self):
        """Phase 4 report should document all work."""
        with open("reports/phase4_status.md") as f:
            content = f.read()

        required_sections = [
            "Intent Discovery",
            "Intent Taxonomy",
            "Golden Candidates",
            "Annotation Interface",
            "Next Steps"
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"


class TestDocumentation:
    """Test all Phase 4 documentation."""

    def test_all_reports_exist(self):
        """All required reports should exist."""
        reports = [
            "reports/phase4_status.md",
            "reports/intent_discovery.json",
            "reports/intent_taxonomy.md"
        ]

        for report in reports:
            assert Path(report).exists(), f"Missing: {report}"

    def test_documentation_references_data(self):
        """Documentation should reference actual statistics."""
        with open("reports/phase4_status.md") as f:
            content = f.read()

        # Should mention key statistics
        assert "162,562" in content  # customer messages
        assert "12" in content  # intent categories
        assert "250" in content  # golden candidates


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
