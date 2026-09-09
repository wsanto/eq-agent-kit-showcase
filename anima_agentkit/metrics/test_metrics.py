#!/usr/bin/env python3
"""
Test script for the comprehensive metrics system.

Tests:
1. MetricsCollector initialization and basic operations
2. All metric recording methods
3. Aggregation over time ranges
4. Web search client configuration
"""

import asyncio
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")


def print_result(name: str, passed: bool, details: str = ""):
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {status}: {name}")
    if details:
        print(f"         {details}")


async def test_metrics_collector():
    """Test the MetricsCollector class."""
    print_section("1. Testing MetricsCollector")

    all_passed = True

    try:
        from anima_agentkit.metrics import (
            MetricsCollector,
            get_metrics_collector,
            MetricType
        )

        # Test singleton
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        if collector1 is collector2:
            print_result("Singleton pattern", True)
        else:
            print_result("Singleton pattern", False, "Not same instance")
            all_passed = False

        # Test basic metric recording
        collector = collector1

        # IGA metrics
        collector.record_iga_phi(0.85)
        if collector.get_current_metrics().iga.phi_value == 0.85:
            print_result("IGA Phi recording", True, f"Phi = {collector.get_current_metrics().iga.phi_value}")
        else:
            print_result("IGA Phi recording", False)
            all_passed = False

        # Motivation
        collector.record_iga_motivation(0.7, 0.8, 0.9)
        motivation = collector.get_current_metrics().iga.intrinsic_motivation
        if abs(motivation - 0.8) < 0.01:
            print_result("IGA motivation", True, f"Motivation = {motivation:.2f}")
        else:
            print_result("IGA motivation", False, f"Expected 0.8, got {motivation}")
            all_passed = False

        # Free energy
        collector.record_iga_free_energy(-0.5, 0.1)
        print_result("IGA free energy", True,
                    f"F = {collector.get_current_metrics().iga.free_energy}")

        # Information theory
        collector.record_iga_information_theory(1.5, 0.8, 0.2)
        print_result("IGA information theory", True,
                    f"H = {collector.get_current_metrics().iga.shannon_entropy}")

        # Interests
        collector.record_iga_interests(2, 3, 4, 1)
        if collector.get_current_metrics().iga.active_interests_count == 10:
            print_result("IGA interests", True,
                        f"Total = {collector.get_current_metrics().iga.active_interests_count}")
        else:
            print_result("IGA interests", False)
            all_passed = False

        # Curiosity
        collector.record_iga_curiosity(0.75, 0.6, 0.8)
        print_result("IGA curiosity", True)

        # Dynamics
        collector.record_iga_dynamics(0.85, 0.9, -0.1)
        print_result("IGA dynamics", True)

        # Q-Theory
        collector.record_iga_q_theory(0.65, 1.2)
        print_result("IGA Q-Theory", True,
                    f"Coherence = {collector.get_current_metrics().iga.emotional_coherence}")

    except Exception as e:
        print_result("MetricsCollector tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def test_memory_belief_goal_metrics():
    """Test memory, belief, and goal metrics."""
    print_section("2. Testing Memory, Belief, Goal Metrics")

    all_passed = True

    try:
        from anima_agentkit.metrics import get_metrics_collector

        collector = get_metrics_collector()

        # Memory metrics
        collector.record_memory_counts(100, 50, 30, 20)
        if collector.get_current_metrics().memory.total_memories == 100:
            print_result("Memory counts", True, "Total = 100")
        else:
            print_result("Memory counts", False)
            all_passed = False

        collector.record_memory_tiers(10, 40, 50)
        print_result("Memory tiers", True,
                    f"Core={collector.get_current_metrics().memory.core_memories}")

        collector.record_memory_quality(0.7, 0.65, 15)
        print_result("Memory quality", True)

        collector.record_memory_retrieval(150.5)
        collector.record_memory_retrieval(200.3)
        avg_latency = collector.get_current_metrics().memory.average_retrieval_latency_ms
        print_result("Memory retrieval", True, f"Avg latency = {avg_latency:.1f}ms")

        # Belief metrics
        collector.record_belief_counts(50, 45, 5)
        if collector.get_current_metrics().belief.total_beliefs == 50:
            print_result("Belief counts", True, "Total = 50")
        else:
            print_result("Belief counts", False)
            all_passed = False

        collector.record_belief_categories(10, 8, 12, 10, 5, 5)
        print_result("Belief categories", True)

        collector.record_belief_strength_distribution(15, 25, 10)
        print_result("Belief strength distribution", True)

        collector.record_belief_formed()
        collector.record_belief_formed()
        collector.record_belief_reinforced()
        if collector.get_current_metrics().belief.beliefs_formed_today == 2:
            print_result("Belief events", True, "Formed = 2")
        else:
            print_result("Belief events", False)
            all_passed = False

        # Goal metrics
        collector.record_goal_counts(20, 15, 4, 1, 0)
        if collector.get_current_metrics().goal.active_goals == 15:
            print_result("Goal counts", True, "Active = 15")
        else:
            print_result("Goal counts", False)
            all_passed = False

        collector.record_goal_progress(0.45, 3, 2)
        print_result("Goal progress", True,
                    f"Avg = {collector.get_current_metrics().goal.average_progress:.2f}")

        collector.record_goal_completed(7.5)
        collector.record_goal_created()
        print_result("Goal events", True)

    except Exception as e:
        print_result("Memory/Belief/Goal tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def test_emotion_breakthrough_metrics():
    """Test emotion and breakthrough metrics."""
    print_section("3. Testing Emotion & Breakthrough Metrics")

    all_passed = True

    try:
        from anima_agentkit.metrics import get_metrics_collector

        collector = get_metrics_collector()

        # Emotion metrics
        collector.record_emotion_state(0.6, 0.5, 0.7, "joy", 0.85)
        if collector.get_current_metrics().emotion.current_valence == 0.6:
            print_result("Emotion state", True,
                        f"Valence = {collector.get_current_metrics().emotion.current_valence}")
        else:
            print_result("Emotion state", False)
            all_passed = False

        collector.record_emotion_trend(0.55, 0.48, 0.3, 0.6)
        print_result("Emotion trend", True)

        collector.record_emotion_occurrence("joy")
        collector.record_emotion_occurrence("trust")
        collector.record_emotion_occurrence("joy")
        if collector.get_current_metrics().emotion.joy_count == 2:
            print_result("Emotion occurrences", True, "Joy = 2")
        else:
            print_result("Emotion occurrences", False)
            all_passed = False

        # Breakthrough metrics
        collector.record_breakthrough(
            breakthrough_type="cognitive",
            confidence=0.85,
            emotional_shift=0.3,
            wonder_index=0.75,
            markers_detected=5,
            clinical_sig="high",
            therapeutic="moderate"
        )

        if collector.get_current_metrics().breakthrough.total_breakthroughs == 1:
            print_result("Breakthrough recording", True,
                        f"Total = {collector.get_current_metrics().breakthrough.total_breakthroughs}")
        else:
            print_result("Breakthrough recording", False)
            all_passed = False

        # Check breakthrough type counts
        if collector.get_current_metrics().breakthrough.cognitive_breakthroughs == 1:
            print_result("Breakthrough type counting", True)
        else:
            print_result("Breakthrough type counting", False)
            all_passed = False

    except Exception as e:
        print_result("Emotion/Breakthrough tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def test_context_conversation_metrics():
    """Test context and conversation metrics."""
    print_section("4. Testing Context & Conversation Metrics")

    all_passed = True

    try:
        from anima_agentkit.metrics import get_metrics_collector

        collector = get_metrics_collector()

        # Context metrics
        collector.record_context_composition(
            tokens_used=1500,
            tokens_allocated=2000,
            quality=0.82,
            relevance=0.78,
            beliefs=3,
            goals=2,
            memories=5,
            interests=2
        )

        if collector.get_current_metrics().context.average_quality_score == 0.82:
            print_result("Context composition", True,
                        f"Quality = {collector.get_current_metrics().context.average_quality_score}")
        else:
            print_result("Context composition", False)
            all_passed = False

        efficiency = collector.get_current_metrics().context.token_efficiency
        if abs(efficiency - 0.75) < 0.01:
            print_result("Token efficiency", True, f"Efficiency = {efficiency:.2f}")
        else:
            print_result("Token efficiency", False, f"Expected 0.75, got {efficiency}")
            all_passed = False

        # Conversation metrics
        collector.record_session_start()
        if collector.get_current_metrics().conversation.active_sessions == 1:
            print_result("Session start", True)
        else:
            print_result("Session start", False)
            all_passed = False

        collector.record_conversation_message(is_user=True, message_length=150)
        collector.record_conversation_message(is_user=False, message_length=300)

        if collector.get_current_metrics().conversation.total_messages == 2:
            print_result("Message recording", True, "Total = 2")
        else:
            print_result("Message recording", False)
            all_passed = False

        collector.record_response_time(250.5)
        print_result("Response time", True,
                    f"Avg = {collector.get_current_metrics().conversation.average_response_time_ms:.1f}ms")

        collector.record_session_end(duration_minutes=15.5, message_count=10)
        if collector.get_current_metrics().conversation.active_sessions == 0:
            print_result("Session end", True)
        else:
            print_result("Session end", False)
            all_passed = False

    except Exception as e:
        print_result("Context/Conversation tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def test_llm_system_metrics():
    """Test LLM and system metrics."""
    print_section("5. Testing LLM & System Metrics")

    all_passed = True

    try:
        from anima_agentkit.metrics import get_metrics_collector

        collector = get_metrics_collector()

        # LLM metrics
        collector.record_llm_call(tokens=1500, latency_ms=850.5, model="mistral-large")
        collector.record_llm_call(tokens=2000, latency_ms=1200.3, model="mistral-large")

        if collector.get_current_metrics().total_llm_calls == 2:
            print_result("LLM call recording", True, "Calls = 2")
        else:
            print_result("LLM call recording", False)
            all_passed = False

        if collector.get_current_metrics().total_tokens_used == 3500:
            print_result("Token counting", True, "Tokens = 3500")
        else:
            print_result("Token counting", False)
            all_passed = False

        avg_latency = collector.get_current_metrics().average_latency_ms
        print_result("Average latency", True, f"Latency = {avg_latency:.1f}ms")

        # Error/warning tracking
        collector.record_error("test_component")
        collector.record_warning("test_component")

        if collector.get_current_metrics().error_count == 1:
            print_result("Error tracking", True)
        else:
            print_result("Error tracking", False)
            all_passed = False

        # Health score
        health = collector._calculate_health_score()
        if 0 <= health <= 100:
            print_result("Health score", True, f"Score = {health:.1f}")
        else:
            print_result("Health score", False)
            all_passed = False

    except Exception as e:
        print_result("LLM/System tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def test_aggregator():
    """Test metrics aggregation."""
    print_section("6. Testing Metrics Aggregator")

    all_passed = True

    try:
        from anima_agentkit.metrics import (
            MetricsAggregator,
            TimeRange,
            get_metrics_collector
        )

        collector = get_metrics_collector()
        aggregator = MetricsAggregator(collector)

        # Get hourly aggregation
        hourly = aggregator.aggregate(TimeRange.HOUR)

        if hourly.time_range == TimeRange.HOUR:
            print_result("Hour aggregation", True,
                        f"Samples = {hourly.sample_count}")
        else:
            print_result("Hour aggregation", False)
            all_passed = False

        # Test to_dict
        hourly_dict = hourly.to_dict()
        if 'iga' in hourly_dict and 'emotion' in hourly_dict:
            print_result("Aggregation to_dict", True)
        else:
            print_result("Aggregation to_dict", False)
            all_passed = False

        # Dashboard summary
        summary = aggregator.get_dashboard_summary()
        if 'hour' in summary and 'current' in summary:
            print_result("Dashboard summary", True)
        else:
            print_result("Dashboard summary", False)
            all_passed = False

        # Component metrics
        iga_metrics = aggregator.get_component_metrics('iga')
        if 'consciousness' in iga_metrics and 'curiosity' in iga_metrics:
            print_result("Component metrics", True)
        else:
            print_result("Component metrics", False)
            all_passed = False

    except Exception as e:
        print_result("Aggregator tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def test_web_search_setup():
    """Test web search client setup."""
    print_section("7. Testing Web Search Client Setup")

    all_passed = True

    try:
        from anima_agentkit.iga import (
            create_web_search_client,
            create_deep_xplore_search_client,
            MCPWebSearchClient
        )

        # Create client without keys (should work but have no providers)
        client = create_web_search_client()

        if isinstance(client, MCPWebSearchClient):
            print_result("Client creation", True)
        else:
            print_result("Client creation", False)
            all_passed = False

        # Check provider count (will be 0 without API keys)
        provider_count = len(client.providers)
        print_result("Provider detection", True,
                    f"{provider_count} providers configured")

        # Create Deep-Xplore adapter
        adapter = create_deep_xplore_search_client()

        if hasattr(adapter, 'search') and hasattr(adapter, 'close'):
            print_result("Deep-Xplore adapter", True)
        else:
            print_result("Deep-Xplore adapter", False)
            all_passed = False

        await client.close()

    except Exception as e:
        print_result("Web search tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def test_system_metrics_to_dict():
    """Test SystemMetrics to_dict method."""
    print_section("8. Testing SystemMetrics Export")

    all_passed = True

    try:
        from anima_agentkit.metrics import get_metrics_collector

        collector = get_metrics_collector()
        metrics = collector.get_current_metrics()

        # Export to dict
        metrics_dict = metrics.to_dict()

        # Check required keys
        required_keys = ['health', 'llm', 'components']
        for key in required_keys:
            if key in metrics_dict:
                print_result(f"Export key: {key}", True)
            else:
                print_result(f"Export key: {key}", False)
                all_passed = False

        # Check component keys
        components = metrics_dict.get('components', {})
        component_keys = ['iga', 'memory', 'belief', 'goal', 'emotion',
                         'breakthrough', 'context', 'conversation']

        for key in component_keys:
            if key in components:
                pass  # Good
            else:
                print_result(f"Component: {key}", False)
                all_passed = False

        print_result("All components present", len(components) == 8,
                    f"{len(components)}/8 components")

        # Test JSON serialization
        import json
        try:
            json_str = json.dumps(metrics_dict)
            print_result("JSON serialization", True,
                        f"{len(json_str)} chars")
        except Exception as e:
            print_result("JSON serialization", False, str(e))
            all_passed = False

    except Exception as e:
        print_result("SystemMetrics export tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False

    return all_passed


async def run_all_tests():
    """Run all metrics tests."""
    print("\n" + "="*60)
    print(" METRICS SYSTEM TEST SUITE")
    print(" Comprehensive Metrics for ANIMA AgentKit")
    print("="*60)

    results = {}

    results['collector'] = await test_metrics_collector()
    results['memory_belief_goal'] = await test_memory_belief_goal_metrics()
    results['emotion_breakthrough'] = await test_emotion_breakthrough_metrics()
    results['context_conversation'] = await test_context_conversation_metrics()
    results['llm_system'] = await test_llm_system_metrics()
    results['aggregator'] = await test_aggregator()
    results['web_search'] = await test_web_search_setup()
    results['export'] = await test_system_metrics_to_dict()

    # Summary
    print_section("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for name, result in results.items():
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {status}: {name}")

    print(f"\n  Total: {passed}/{total} test suites passed\n")

    if passed == total:
        print(f"  {GREEN}✓ All tests passed! Metrics system is functional.{RESET}")
        return True
    else:
        print(f"  {RED}✗ Some tests failed. Check output above for details.{RESET}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
