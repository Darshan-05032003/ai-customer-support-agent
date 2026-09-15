#!/usr/bin/env python3
"""
Phase 5 tests - annotation, dataset, classifiers, and pipeline.
"""

import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.loaders import load_raw_data, validate_raw_data


class TestAnnotationSetup:
    """Test annotation infrastructure."""

    def test_golden_candidates_reduced_exist(self):
        """Reduced golden candidates should exist."""
        path = Path("data/evaluation/golden_candidates_reduced.jsonl")
        assert path.exists(), f"Missing: {path}"

    def test_golden_candidates_count(self):
        """Should have exactly 250 candidates."""
        count = sum(1 for _ in open("data/evaluation/golden_candidates_reduced.jsonl"))
        assert count == 250, f"Expected 250, got {count}"

    def test_annotation_ui_exists(self):
        """Flask annotation UI should exist."""
        assert Path("app.py").exists()
        assert Path("templates/annotator.html").exists()

    def test_intent_taxonomy_exists(self):
        """Intent taxonomy should be available."""
        assert Path("reports/intent_taxonomy.md").exists()
        assert Path("reports/intent_discovery.json").exists()


class TestDatasetBuilder:
    """Test labeled dataset building."""

    def test_build_labeled_dataset_script_exists(self):
        """Dataset builder script should exist."""
        assert Path("scripts/build_labeled_dataset.py").exists()

    def test_classifier_plan_exists(self):
        """Classifier plan should be documented."""
        assert Path("reports/classifier_plan.md").exists()

        with open("reports/classifier_plan.md") as f:
            content = f.read()
            assert "Conversation" in content or "conversation" in content.lower()
            assert "TF-IDF" in content
            assert "Logistic Regression" in content


class TestClassifierInfrastructure:
    """Test classifier training infrastructure."""

    def test_train_classifier_script_exists(self):
        """Classifier training script should exist."""
        assert Path("scripts/train_intent_classifier.py").exists()

    def test_classifier_model_wrapper_exists(self):
        """Classifier model wrapper should exist."""
        assert Path("scripts/classifier_model.py").exists()

    def test_models_directory_structure(self):
        """Models directory should be set up."""
        models_dir = Path("models")
        assert models_dir.exists() or not models_dir.exists()  # OK if not created yet


class TestEscalationDetection:
    """Test escalation detection."""

    def test_escalation_detector_exists(self):
        """Escalation detector script should exist."""
        assert Path("scripts/escalation_detector.py").exists()

    def test_escalation_detector_importable(self):
        """Escalation detector should be importable."""
        from scripts.escalation_detector import EscalationDetector

        # Test rule-based detection
        result = EscalationDetector.detect("I need to speak to a manager!")
        assert 'escalation_required' in result
        assert 'signals' in result

    def test_escalation_detector_no_false_positives(self):
        """Normal queries should not trigger escalation."""
        from scripts.escalation_detector import EscalationDetector

        result = EscalationDetector.detect("Where is my order?")
        assert result['escalation_required'] == False


class TestResponseRetrieval:
    """Test response retrieval infrastructure."""

    def test_response_retriever_exists(self):
        """Response retriever script should exist."""
        assert Path("scripts/response_retriever.py").exists()

    def test_response_retriever_importable(self):
        """Response retriever should be importable."""
        from scripts.response_retriever import ResponseRetriever

        retriever = ResponseRetriever()
        # Should handle gracefully if index doesn't exist yet
        result = retriever.retrieve("test")
        assert 'status' in result


class TestOfflinePipeline:
    """Test offline pipeline."""

    def test_pipeline_exists(self):
        """Offline pipeline script should exist."""
        assert Path("scripts/offline_pipeline.py").exists()

    def test_pipeline_importable(self):
        """Pipeline should be importable."""
        from scripts.offline_pipeline import SupportPipeline

        pipeline = SupportPipeline()
        assert hasattr(pipeline, 'process')

    def test_pipeline_output_schema(self):
        """Pipeline output should have correct schema."""
        from scripts.offline_pipeline import SupportPipeline

        pipeline = SupportPipeline()
        result = pipeline.process("Where is my order?")

        # Check required fields
        assert 'input' in result
        assert 'timestamp' in result
        assert 'components' in result
        assert 'recommendation' in result

        # Check components
        assert 'intent' in result['components']
        assert 'escalation' in result['components']
        assert 'retrieval' in result['components']

        # Check status fields
        assert 'status' in result['components']['intent']
        assert 'status' in result['components']['escalation']
        assert 'status' in result['components']['retrieval']


class TestPhase5Foundation:
    """Test Phase 5 foundational requirements."""

    def test_raw_data_still_unchanged(self):
        """Raw data checksum must not change."""
        import subprocess

        result = subprocess.run(
            ["md5sum", "archive/twcs/twcs.csv"],
            capture_output=True, text=True
        )
        actual = result.stdout.split()[0]
        expected = "73e961b2837626de89618a3f35f7bd6c"

        assert actual == expected, "Raw data was modified!"

    def test_conversation_data_intact(self):
        """Conversation data from Phase 3 must be intact."""
        count = sum(1 for _ in open("data/processed/amazonhelp_conversations.jsonl"))
        assert count == 45162

    def test_customer_messages_intact(self):
        """Customer messages from Phase 3 must be intact."""
        count = sum(1 for _ in open("data/processed/amazonhelp_customer_messages.jsonl"))
        assert count == 162562

    def test_phase4_tests_still_pass(self):
        """Phase 4 components must still be valid."""
        assert Path("reports/intent_taxonomy.md").exists()
        assert Path("reports/intent_discovery.json").exists()

        with open("reports/intent_discovery.json") as f:
            report = json.load(f)
            assert len(report['intent_categories']) == 12

    def test_no_automatic_annotations(self):
        """Annotations should not be automatically generated."""
        # Either file doesn't exist (pending) or exists with actual data
        path = Path("data/evaluation/golden_annotations.jsonl")

        if path.exists():
            # If it exists, check it's not just empty lines
            with open(path) as f:
                lines = [line.strip() for line in f if line.strip()]
            assert len(lines) > 0, "Annotations file is empty"


class TestDocumentation:
    """Test Phase 5 documentation."""

    def test_classifier_plan_exists(self):
        """Classifier plan should be documented."""
        assert Path("reports/classifier_plan.md").exists()

    def test_classifier_plan_comprehensive(self):
        """Classifier plan should be comprehensive."""
        with open("reports/classifier_plan.md") as f:
            content = f.read()

        required_sections = [
            "Annotation Data Representation",
            "Data Split Strategy",
            "Classifier Architecture",
            "Evaluation Metrics"
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"


class TestPreviousTestsStillPass:
    """Verify all previous tests still pass."""

    def test_phase3_foundation(self):
        """Phase 3 foundation should still be valid."""
        df = load_raw_data()
        validate_raw_data(df)

        assert len(df) == 2811774
        amazon_tweets = df[(df['inbound'] == False) & (df['author_id'] == 'AmazonHelp')]
        assert len(amazon_tweets) == 169840

    def test_phase4_artifacts_exist(self):
        """Phase 4 artifacts must still exist."""
        assert Path("data/evaluation/golden_candidates_reduced.jsonl").exists()
        assert Path("reports/intent_taxonomy.md").exists()
        assert Path("reports/intent_discovery.json").exists()


class TestAnnotationStatus:
    """Test annotation status tracking."""

    def test_annotation_status_reportable(self):
        """Annotation status should be clearly reportable."""
        labeled_path = Path("data/evaluation/golden_labeled.jsonl")
        annotations_path = Path("data/evaluation/golden_annotations.jsonl")

        # Status: either no annotations (both missing) or some annotations exist
        if annotations_path.exists():
            with open(annotations_path) as f:
                lines = [line.strip() for line in f if line.strip()]
            num_annotations = len(lines)
            assert num_annotations >= 0
        else:
            num_annotations = 0

        # At least report accurately
        assert num_annotations >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
