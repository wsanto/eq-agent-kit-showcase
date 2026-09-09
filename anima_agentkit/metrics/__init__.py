"""
Comprehensive Metrics System for ANIMA AgentKit

This module provides a robust metrics collection and aggregation system
that integrates:
- IGA (Interest Generation Algorithm) metrics
- Memory system metrics
- Belief system metrics
- Goal system metrics
- Emotion/arousal metrics
- Breakthrough detection metrics
- Context composition metrics

All metrics are collected from the various components and aggregated
for dashboard visualization and analysis.
"""

from .collector import (
    MetricsCollector,
    MetricEvent,
    MetricType,
    get_metrics_collector
)
from .system_metrics import (
    SystemMetrics,
    IGAMetrics,
    MemoryMetrics,
    BeliefMetrics,
    GoalMetrics,
    EmotionMetrics,
    BreakthroughMetrics,
    ContextMetrics,
    ConversationMetrics
)
from .aggregator import (
    MetricsAggregator,
    AggregatedMetrics,
    TimeRange
)

__all__ = [
    # Core collector
    'MetricsCollector',
    'MetricEvent',
    'MetricType',
    'get_metrics_collector',

    # Metric types
    'SystemMetrics',
    'IGAMetrics',
    'MemoryMetrics',
    'BeliefMetrics',
    'GoalMetrics',
    'EmotionMetrics',
    'BreakthroughMetrics',
    'ContextMetrics',
    'ConversationMetrics',

    # Aggregation
    'MetricsAggregator',
    'AggregatedMetrics',
    'TimeRange'
]
