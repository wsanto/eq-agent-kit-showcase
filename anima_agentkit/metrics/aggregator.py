"""
Metrics Aggregator for ANIMA AgentKit.

Provides aggregated views of metrics over time ranges for
dashboard visualization and analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger

from .system_metrics import SystemMetrics
from .collector import MetricsCollector, get_metrics_collector


class TimeRange(str, Enum):
    """Time ranges for metric aggregation."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class AggregatedMetrics:
    """
    Aggregated metrics over a time range.

    Provides min, max, average, and trend information.
    """
    time_range: TimeRange
    start_time: datetime
    end_time: datetime
    sample_count: int = 0

    # IGA Aggregates
    avg_phi: float = 0.0
    max_phi: float = 0.0
    avg_intrinsic_motivation: float = 0.0
    avg_curiosity: float = 0.0
    avg_entropy: float = 0.0
    total_interests_formed: int = 0

    # Memory Aggregates
    total_memories_created: int = 0
    avg_memory_quality: float = 0.0
    avg_retrieval_latency: float = 0.0

    # Belief Aggregates
    beliefs_formed: int = 0
    beliefs_reinforced: int = 0
    beliefs_challenged: int = 0
    avg_belief_strength: float = 0.0

    # Goal Aggregates
    goals_completed: int = 0
    goals_created: int = 0
    avg_goal_progress: float = 0.0

    # Emotion Aggregates
    avg_valence: float = 0.0
    avg_arousal: float = 0.0
    volatility: float = 0.0
    dominant_emotion: str = ""

    # Breakthrough Aggregates
    total_breakthroughs: int = 0
    avg_breakthrough_confidence: float = 0.0

    # Context Aggregates
    avg_context_quality: float = 0.0
    avg_context_relevance: float = 0.0
    avg_token_efficiency: float = 0.0

    # Conversation Aggregates
    total_messages: int = 0
    total_sessions: int = 0
    avg_session_length: float = 0.0
    avg_response_time: float = 0.0

    # System Aggregates
    avg_health_score: float = 0.0
    total_errors: int = 0
    total_llm_calls: int = 0
    avg_llm_latency: float = 0.0
    total_cost_usd: float = 0.0

    # Trends
    phi_trend: List[float] = field(default_factory=list)
    motivation_trend: List[float] = field(default_factory=list)
    valence_trend: List[float] = field(default_factory=list)
    arousal_trend: List[float] = field(default_factory=list)
    health_trend: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'time_range': self.time_range.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'sample_count': self.sample_count,
            'iga': {
                'avg_phi': self.avg_phi,
                'max_phi': self.max_phi,
                'avg_motivation': self.avg_intrinsic_motivation,
                'avg_curiosity': self.avg_curiosity,
                'avg_entropy': self.avg_entropy,
                'interests_formed': self.total_interests_formed,
                'phi_trend': self.phi_trend
            },
            'memory': {
                'created': self.total_memories_created,
                'avg_quality': self.avg_memory_quality,
                'avg_retrieval_latency': self.avg_retrieval_latency
            },
            'belief': {
                'formed': self.beliefs_formed,
                'reinforced': self.beliefs_reinforced,
                'challenged': self.beliefs_challenged,
                'avg_strength': self.avg_belief_strength
            },
            'goal': {
                'completed': self.goals_completed,
                'created': self.goals_created,
                'avg_progress': self.avg_goal_progress
            },
            'emotion': {
                'avg_valence': self.avg_valence,
                'avg_arousal': self.avg_arousal,
                'volatility': self.volatility,
                'dominant': self.dominant_emotion,
                'valence_trend': self.valence_trend,
                'arousal_trend': self.arousal_trend
            },
            'breakthrough': {
                'total': self.total_breakthroughs,
                'avg_confidence': self.avg_breakthrough_confidence
            },
            'context': {
                'avg_quality': self.avg_context_quality,
                'avg_relevance': self.avg_context_relevance,
                'avg_efficiency': self.avg_token_efficiency
            },
            'conversation': {
                'messages': self.total_messages,
                'sessions': self.total_sessions,
                'avg_session_length': self.avg_session_length,
                'avg_response_time': self.avg_response_time
            },
            'system': {
                'avg_health': self.avg_health_score,
                'errors': self.total_errors,
                'llm_calls': self.total_llm_calls,
                'avg_llm_latency': self.avg_llm_latency,
                'total_cost': self.total_cost_usd,
                'health_trend': self.health_trend
            }
        }


class MetricsAggregator:
    """
    Aggregates metrics over time ranges.

    Provides statistical summaries and trends for dashboard visualization.
    """

    def __init__(self, collector: Optional[MetricsCollector] = None):
        self.collector = collector or get_metrics_collector()

    def aggregate(self, time_range: TimeRange) -> AggregatedMetrics:
        """
        Aggregate metrics for a time range.

        Args:
            time_range: The time range to aggregate

        Returns:
            Aggregated metrics
        """
        # Determine minutes for time range
        minutes_map = {
            TimeRange.HOUR: 60,
            TimeRange.DAY: 1440,
            TimeRange.WEEK: 10080,
            TimeRange.MONTH: 43200
        }
        minutes = minutes_map.get(time_range, 60)

        # Get metrics history
        history = self.collector.get_metrics_history(minutes)

        if not history:
            return AggregatedMetrics(
                time_range=time_range,
                start_time=datetime.utcnow() - timedelta(minutes=minutes),
                end_time=datetime.utcnow()
            )

        # Create aggregated result
        result = AggregatedMetrics(
            time_range=time_range,
            start_time=history[0].timestamp,
            end_time=history[-1].timestamp,
            sample_count=len(history)
        )

        # Aggregate values
        self._aggregate_iga(result, history)
        self._aggregate_memory(result, history)
        self._aggregate_belief(result, history)
        self._aggregate_goal(result, history)
        self._aggregate_emotion(result, history)
        self._aggregate_breakthrough(result, history)
        self._aggregate_context(result, history)
        self._aggregate_conversation(result, history)
        self._aggregate_system(result, history)

        return result

    def _aggregate_iga(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate IGA metrics."""
        if not history:
            return

        phi_values = [m.iga.phi_value for m in history]
        motivation_values = [m.iga.intrinsic_motivation for m in history]
        curiosity_values = [m.iga.curiosity_score for m in history]
        entropy_values = [m.iga.shannon_entropy for m in history]

        result.avg_phi = sum(phi_values) / len(phi_values) if phi_values else 0
        result.max_phi = max(phi_values) if phi_values else 0
        result.avg_intrinsic_motivation = sum(motivation_values) / len(motivation_values) if motivation_values else 0
        result.avg_curiosity = sum(curiosity_values) / len(curiosity_values) if curiosity_values else 0
        result.avg_entropy = sum(entropy_values) / len(entropy_values) if entropy_values else 0

        # Calculate total interests formed (difference from start to end)
        if len(history) >= 2:
            result.total_interests_formed = history[-1].iga.active_interests_count - history[0].iga.active_interests_count

        # Downsample trends (max 50 points)
        result.phi_trend = self._downsample(phi_values, 50)
        result.motivation_trend = self._downsample(motivation_values, 50)

    def _aggregate_memory(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate memory metrics."""
        if not history:
            return

        quality_values = [m.memory.average_importance for m in history]
        latency_values = [m.memory.average_retrieval_latency_ms for m in history]

        result.avg_memory_quality = sum(quality_values) / len(quality_values) if quality_values else 0
        result.avg_retrieval_latency = sum(latency_values) / len(latency_values) if latency_values else 0

        # Total memories created
        if len(history) >= 2:
            result.total_memories_created = history[-1].memory.total_memories - history[0].memory.total_memories

    def _aggregate_belief(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate belief metrics."""
        if not history:
            return

        strength_values = [m.belief.average_strength for m in history]
        result.avg_belief_strength = sum(strength_values) / len(strength_values) if strength_values else 0

        # Sum daily counters (last snapshot has cumulative values)
        result.beliefs_formed = history[-1].belief.beliefs_formed_today
        result.beliefs_reinforced = history[-1].belief.beliefs_reinforced_today
        result.beliefs_challenged = history[-1].belief.beliefs_challenged_today

    def _aggregate_goal(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate goal metrics."""
        if not history:
            return

        progress_values = [m.goal.average_progress for m in history]
        result.avg_goal_progress = sum(progress_values) / len(progress_values) if progress_values else 0

        # Weekly counters
        result.goals_completed = history[-1].goal.goals_completed_this_week
        result.goals_created = history[-1].goal.goals_created_this_week

    def _aggregate_emotion(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate emotion metrics."""
        if not history:
            return

        valence_values = [m.emotion.current_valence for m in history]
        arousal_values = [m.emotion.current_arousal for m in history]
        volatility_values = [m.emotion.emotional_volatility for m in history]

        result.avg_valence = sum(valence_values) / len(valence_values) if valence_values else 0
        result.avg_arousal = sum(arousal_values) / len(arousal_values) if arousal_values else 0
        result.volatility = sum(volatility_values) / len(volatility_values) if volatility_values else 0

        # Find dominant emotion
        emotion_counts = {
            'joy': history[-1].emotion.joy_count,
            'trust': history[-1].emotion.trust_count,
            'fear': history[-1].emotion.fear_count,
            'surprise': history[-1].emotion.surprise_count,
            'sadness': history[-1].emotion.sadness_count,
            'disgust': history[-1].emotion.disgust_count,
            'anger': history[-1].emotion.anger_count,
            'anticipation': history[-1].emotion.anticipation_count
        }
        result.dominant_emotion = max(emotion_counts, key=emotion_counts.get) if any(emotion_counts.values()) else ""

        # Trends
        result.valence_trend = self._downsample(valence_values, 50)
        result.arousal_trend = self._downsample(arousal_values, 50)

    def _aggregate_breakthrough(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate breakthrough metrics."""
        if not history:
            return

        confidence_values = [m.breakthrough.average_confidence for m in history]
        result.avg_breakthrough_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0

        # Use the latest cumulative value
        result.total_breakthroughs = history[-1].breakthrough.total_breakthroughs

    def _aggregate_context(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate context metrics."""
        if not history:
            return

        quality_values = [m.context.average_quality_score for m in history]
        relevance_values = [m.context.average_relevance_score for m in history]
        efficiency_values = [m.context.token_efficiency for m in history]

        result.avg_context_quality = sum(quality_values) / len(quality_values) if quality_values else 0
        result.avg_context_relevance = sum(relevance_values) / len(relevance_values) if relevance_values else 0
        result.avg_token_efficiency = sum(efficiency_values) / len(efficiency_values) if efficiency_values else 0

    def _aggregate_conversation(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate conversation metrics."""
        if not history:
            return

        session_lengths = [m.conversation.average_session_length_minutes for m in history]
        response_times = [m.conversation.average_response_time_ms for m in history]

        result.avg_session_length = sum(session_lengths) / len(session_lengths) if session_lengths else 0
        result.avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Use latest cumulative values
        result.total_messages = history[-1].conversation.total_messages
        result.total_sessions = history[-1].conversation.total_sessions

    def _aggregate_system(self, result: AggregatedMetrics, history: List[SystemMetrics]):
        """Aggregate system metrics."""
        if not history:
            return

        health_values = [m.health_score for m in history]
        latency_values = [m.average_latency_ms for m in history]

        result.avg_health_score = sum(health_values) / len(health_values) if health_values else 0
        result.avg_llm_latency = sum(latency_values) / len(latency_values) if latency_values else 0

        # Use latest cumulative values
        result.total_errors = history[-1].error_count
        result.total_llm_calls = history[-1].total_llm_calls
        result.total_cost_usd = history[-1].estimated_cost_usd

        # Health trend
        result.health_trend = self._downsample(health_values, 50)

    def _downsample(self, values: List[float], max_points: int) -> List[float]:
        """Downsample a list of values to max_points."""
        if not values or len(values) <= max_points:
            return values

        step = len(values) / max_points
        return [values[int(i * step)] for i in range(max_points)]

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get a summary for the main dashboard.

        Returns hourly, daily, and weekly aggregates.
        """
        return {
            'hour': self.aggregate(TimeRange.HOUR).to_dict(),
            'day': self.aggregate(TimeRange.DAY).to_dict(),
            'week': self.aggregate(TimeRange.WEEK).to_dict(),
            'current': self.collector.get_current_metrics().to_dict()
        }

    def get_component_metrics(self, component: str) -> Dict[str, Any]:
        """
        Get detailed metrics for a specific component.

        Args:
            component: Component name (iga, memory, belief, goal, emotion, breakthrough, context, conversation)

        Returns:
            Component-specific metrics
        """
        current = self.collector.get_current_metrics()

        component_map = {
            'iga': current.iga.to_dict(),
            'memory': current.memory.to_dict(),
            'belief': current.belief.to_dict(),
            'goal': current.goal.to_dict(),
            'emotion': current.emotion.to_dict(),
            'breakthrough': current.breakthrough.to_dict(),
            'context': current.context.to_dict(),
            'conversation': current.conversation.to_dict()
        }

        return component_map.get(component.lower(), {})
