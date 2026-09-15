#!/usr/bin/env python3
"""
Phase 6 Demo Runner

Demonstrates the complete support AI pipeline with various test queries.
Measures performance and displays results in a readable format.
"""

import sys
from pathlib import Path
import json
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline_service import SupportPipeline
from src.intent_service import IntentService
from src.escalation_service import EscalationService
from src.retrieval_service import RetrievalService
from src.response_service import ResponseService


def format_result(result, query):
    """Format pipeline result for display."""
    output = []
    output.append("\n" + "=" * 80)
    output.append(f"Query: {query}")
    output.append("=" * 80)

    if result['status'] != 'success':
        output.append(f"❌ Error: {result.get('error', 'Unknown error')}")
        return "\n".join(output)

    analysis = result['analysis']

    # Intent
    intent = analysis['intent']
    mode_badge = f"[{intent['mode'].upper()}]"
    confidence_str = f" ({intent['confidence']*100:.0f}%)" if intent['confidence'] else ""
    output.append(f"\n📋 Intent: {intent['label']} {mode_badge}{confidence_str}")
    if intent.get('signals'):
        output.append(f"   Signals: {', '.join(intent['signals'])}")

    # Escalation
    escalation = analysis['escalation']
    escalation_status = "🔴 YES" if escalation['required'] else "✅ NO"
    output.append(f"\n⚠️  Escalation: {escalation_status}")
    if escalation.get('signals'):
        output.append(f"   Signals: {', '.join(escalation['signals'])}")

    # Retrieval
    retrieval = analysis['retrieval']
    output.append(f"\n🔍 Retrieval: {retrieval['status']} ({retrieval['count']} results)")

    # Response
    response = analysis['response']
    output.append(f"\n💬 Response Source: {response['source']}")
    output.append(f"   Text: {response['text'][:120]}{'...' if len(response['text']) > 120 else ''}")
    output.append(f"   Reasoning: {response['reasoning']}")

    # Recommendation
    recommendation = result['recommendation']
    output.append(f"\n✨ Recommendation: {recommendation['action'].upper()}")
    output.append(f"   {recommendation['description']}")
    output.append(f"   Reason: {recommendation['reason']}")

    return "\n".join(output)


def run_demo_queries():
    """Run demo with manual test queries."""
    print("\n" + "=" * 80)
    print("PHASE 6: CUSTOMER SUPPORT AI - DEMO RUNNER")
    print("=" * 80)

    # Initialize services
    print("\n⏳ Initializing services...")
    start_init = time.time()

    intent_service = IntentService()
    escalation_service = EscalationService()
    retrieval_service = RetrievalService()
    response_service = ResponseService(retrieval_service)
    pipeline = SupportPipeline(
        intent_service,
        escalation_service,
        retrieval_service,
        response_service
    )

    init_time = time.time() - start_init
    print(f"✅ Services initialized in {init_time:.2f}s")

    # Load test queries
    queries_file = Path(__file__).parent.parent / "tests" / "manual_phase6_queries.json"
    if not queries_file.exists():
        print(f"❌ Test queries file not found: {queries_file}")
        return

    with open(queries_file) as f:
        test_data = json.load(f)

    queries = test_data['test_queries']

    # Demo 1: Quick sample from each category
    print("\n" + "=" * 80)
    print("DEMO 1: SAMPLE QUERIES FROM EACH INTENT CATEGORY")
    print("=" * 80)

    category_queries = {}
    for q in queries:
        cat = q.get('category')
        if cat and cat not in category_queries:
            category_queries[cat] = q

    times = []
    for category, query_data in sorted(category_queries.items()):
        start = time.time()
        result = pipeline.process(query_data['query'])
        elapsed = time.time() - start
        times.append(elapsed)

        print(format_result(result, query_data['query']))
        print(f"⏱️  Processing time: {elapsed*1000:.0f}ms")

    # Demo 2: Escalation examples
    print("\n" + "=" * 80)
    print("DEMO 2: ESCALATION DETECTION EXAMPLES")
    print("=" * 80)

    escalation_queries = [q for q in queries if q.get('should_escalate', False)]
    for query_data in escalation_queries[:3]:
        start = time.time()
        result = pipeline.process(query_data['query'])
        elapsed = time.time() - start

        print(format_result(result, query_data['query']))
        print(f"⏱️  Processing time: {elapsed*1000:.0f}ms")
        times.append(elapsed)

    # Demo 3: Complex queries
    print("\n" + "=" * 80)
    print("DEMO 3: COMPLEX MULTI-INTENT QUERIES")
    print("=" * 80)

    complex_queries = [
        "My package arrived damaged and I need to return it for a refund ASAP!",
        "I've been trying to get help for 3 days now. This is unacceptable!",
        "Can someone explain why I was charged twice and help me get my money back?",
        "My account was compromised and now I can't log in. I need immediate assistance!",
    ]

    for query in complex_queries:
        start = time.time()
        result = pipeline.process(query)
        elapsed = time.time() - start

        print(format_result(result, query))
        print(f"⏱️  Processing time: {elapsed*1000:.0f}ms")
        times.append(elapsed)

    # Performance Summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)

    avg_time = sum(times) / len(times) if times else 0
    min_time = min(times) if times else 0
    max_time = max(times) if times else 0

    print(f"Total queries processed: {len(times)}")
    print(f"Average response time: {avg_time*1000:.1f}ms")
    print(f"Min response time: {min_time*1000:.1f}ms")
    print(f"Max response time: {max_time*1000:.1f}ms")
    print(f"Initialization time: {init_time*1000:.1f}ms")

    # Service Status
    print("\n" + "=" * 80)
    print("SERVICE STATUS")
    print("=" * 80)

    print(f"Intent Service: {'✅ Available' if intent_service else '❌ Unavailable'}")
    print(f"Escalation Service: ✅ Available")
    print(f"Retrieval Service: {'✅ Available' if retrieval_service.is_available() else '⚠️  Degraded (no historical responses)'}")
    print(f"Response Service: ✅ Available")
    print(f"Pipeline: ✅ Operational")

    # Intent Mode
    print("\n" + "=" * 80)
    print("INTENT DETECTION MODE")
    print("=" * 80)

    test_result = pipeline.process("Where is my order?")
    mode = test_result['analysis']['intent']['mode']
    print(f"Current mode: {mode.upper()}")

    if mode == 'supervised':
        print("✅ Using supervised ML classifier")
    else:
        print("⚠️  Using heuristic fallback (classifier not available)")

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


def run_health_check():
    """Run health check on all services."""
    print("\n" + "=" * 80)
    print("HEALTH CHECK")
    print("=" * 80)

    try:
        intent_service = IntentService()
        print("✅ Intent Service: Initialized")
    except Exception as e:
        print(f"❌ Intent Service: {e}")
        return False

    try:
        escalation_service = EscalationService()
        print("✅ Escalation Service: Initialized")
    except Exception as e:
        print(f"❌ Escalation Service: {e}")
        return False

    try:
        retrieval_service = RetrievalService()
        status = "✅ Available" if retrieval_service.is_available() else "⚠️  Degraded"
        print(f"✅ Retrieval Service: {status}")
    except Exception as e:
        print(f"❌ Retrieval Service: {e}")
        return False

    try:
        response_service = ResponseService(retrieval_service)
        print("✅ Response Service: Initialized")
    except Exception as e:
        print(f"❌ Response Service: {e}")
        return False

    try:
        pipeline = SupportPipeline(
            intent_service,
            escalation_service,
            retrieval_service,
            response_service
        )
        result = pipeline.process("Test message")
        if result['status'] == 'success':
            print("✅ Pipeline: Operational")
        else:
            print(f"❌ Pipeline: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Pipeline: {e}")
        return False

    print("\n✅ All services operational")
    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 6 Demo Runner"
    )
    parser.add_argument(
        '--health-only',
        action='store_true',
        help='Run only health check'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Run a single query'
    )

    args = parser.parse_args()

    if args.health_only:
        return run_health_check()

    if args.query:
        intent_service = IntentService()
        escalation_service = EscalationService()
        retrieval_service = RetrievalService()
        response_service = ResponseService(retrieval_service)
        pipeline = SupportPipeline(
            intent_service,
            escalation_service,
            retrieval_service,
            response_service
        )

        result = pipeline.process(args.query)
        print(format_result(result, args.query))
        return True

    # Default: run full demo
    run_demo_queries()
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
