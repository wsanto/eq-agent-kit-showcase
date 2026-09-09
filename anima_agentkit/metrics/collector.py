"""
Metrics Collector for ANIMA AgentKit.

Central collection point for all system metrics with support for
real-time updates and historical tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import asyncio
from loguru import logger

from .system_metrics import (
    SystemMetrics,
    IGAMetrics,
    MemoryMetrics,
    BeliefMetrics,
    GoalMetrics,
    EmotionMetrics,
    BreakthroughMetrics,
    ContextMetrics,
    ConversationMetrics,
    MetricType
)


class MetricEventType(str, Enum):
    """Types of metric events."""
    INCREMENT = "increment"
    DECREMENT = "decrement"
    SET = "set"
    RECORD = "record"
    HISTOGRAM = "histogram"


@dataclass
class MetricEvent:
    """A single metric event."""
    metric_type: MetricType
    event_type: MetricEventType
    name: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class MetricsCollector:
    """
    Central metrics collector for ANIMA AgentKit.

    Collects metrics from all system components and provides
    aggregated views for dashboards and analysis.
    """

    _instance: Optional['MetricsCollector'] = None

    def __init__(self):
        self._metrics_history: List[SystemMetrics] = []
        self._current_metrics = SystemMetrics()
        self._event_buffer: List[MetricEvent] = []
        self._subscribers: List[Callable[[MetricEvent], None]] = []
        self._start_time = datetime.utcnow()

        # Per-component counters
        self._counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._gauges: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._histograms: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

        # Collection interval
        self._collection_task: Optional[asyncio.Task] = None
        self._running = False

    @classmethod
    def get_instance(cls) -> 'MetricsCollector':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = MetricsCollector()
        return cls._instance

    async def start(self, collection_interval_seconds: int = 60):
        """Start periodic metrics collection."""
        if self._running:
            return

        self._running = True
        self._collection_task = asyncio.create_task(
            self._collection_loop(collection_interval_seconds)
        )
        logger.info(f"Metrics collector started with {collection_interval_seconds}s interval")

    async def stop(self):
        """Stop metrics collection."""
        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collector stopped")

    async def _collection_loop(self, interval: int):
        """Periodic collection loop."""
        while self._running:
            try:
                await self._collect_snapshot()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(interval)

    async def _collect_snapshot(self):
        """Collect a metrics snapshot."""
        # Update uptime
        self._current_metrics.uptime_seconds = int(
            (datetime.utcnow() - self._start_time).total_seconds()
        )

        # Calculate health score
        self._current_metrics.health_score = self._calculate_health_score()

        # Store snapshot
        snapshot = SystemMetrics(
            timestamp=datetime.utcnow(),
            iga=self._current_metrics.iga,
            memory=self._current_metrics.memory,
            belief=self._current_metrics.belief,
            goal=self._current_metrics.goal,
            emotion=self._current_metrics.emotion,
            breakthrough=self._current_metrics.breakthrough,
            context=self._current_metrics.context,
            conversation=self._current_metrics.conversation,
            health_score=self._current_metrics.health_score,
            error_count=self._current_metrics.error_count,
            warning_count=self._current_metrics.warning_count,
            uptime_seconds=self._current_metrics.uptime_seconds,
            total_tokens_used=self._current_metrics.total_tokens_used,
            total_llm_calls=self._current_metrics.total_llm_calls,
            average_latency_ms=self._current_metrics.average_latency_ms,
            estimated_cost_usd=self._current_metrics.estimated_cost_usd
        )

        self._metrics_history.append(snapshot)

        # Prune old history (keep 24 hours at 1-minute intervals = 1440 snapshots)
        max_history = 1440
        if len(self._metrics_history) > max_history:
            self._metrics_history = self._metrics_history[-max_history:]

        logger.debug(f"Metrics snapshot collected, history size: {len(self._metrics_history)}")

    def _calculate_health_score(self) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0

        # Deduct for errors
        if self._current_metrics.error_count > 0:
            score -= min(self._current_metrics.error_count * 5, 30)

        # Deduct for high latency (>2000ms)
        if self._current_metrics.average_latency_ms > 2000:
            score -= min((self._current_metrics.average_latency_ms - 2000) / 100, 20)

        # Deduct for low context quality
        if self._current_metrics.context.average_quality_score < 0.5:
            score -= (0.5 - self._current_metrics.context.average_quality_score) * 20

        # Deduct for stuck goals
        if self._current_metrics.goal.goals_stuck > 5:
            score -= min(self._current_metrics.goal.goals_stuck * 2, 10)

        # Bonus for breakthroughs
        if self._current_metrics.breakthrough.breakthroughs_this_week > 0:
            score += min(self._current_metrics.breakthrough.breakthroughs_this_week * 2, 10)

        return max(0, min(100, score))

    # ===========================================================================
    # METRIC RECORDING METHODS
    # ===========================================================================

    def record_event(self, event: MetricEvent):
        """Record a metric event."""
        self._event_buffer.append(event)

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(f"Error notifying metric subscriber: {e}")

        # Apply event to current metrics
        self._apply_event(event)

    def _apply_event(self, event: MetricEvent):
        """Apply an event to current metrics."""
        if event.event_type == MetricEventType.INCREMENT:
            self._counters[event.metric_type.value][event.name] += int(event.value)
        elif event.event_type == MetricEventType.DECREMENT:
            self._counters[event.metric_type.value][event.name] -= int(event.value)
        elif event.event_type == MetricEventType.SET:
            self._gauges[event.metric_type.value][event.name] = float(event.value)
        elif event.event_type == MetricEventType.HISTOGRAM:
            self._histograms[event.metric_type.value][event.name].append(float(event.value))
            # Keep last 1000 values
            if len(self._histograms[event.metric_type.value][event.name]) > 1000:
                self._histograms[event.metric_type.value][event.name] = \
                    self._histograms[event.metric_type.value][event.name][-1000:]

    # Convenience methods for common metrics

    def increment(self, metric_type: MetricType, name: str, value: int = 1, **labels):
        """Increment a counter."""
        self.record_event(MetricEvent(
            metric_type=metric_type,
            event_type=MetricEventType.INCREMENT,
            name=name,
            value=value,
            labels=labels
        ))

    def gauge(self, metric_type: MetricType, name: str, value: float, **labels):
        """Set a gauge value."""
        self.record_event(MetricEvent(
            metric_type=metric_type,
            event_type=MetricEventType.SET,
            name=name,
            value=value,
            labels=labels
        ))

    def histogram(self, metric_type: MetricType, name: str, value: float, **labels):
        """Record a histogram value."""
        self.record_event(MetricEvent(
            metric_type=metric_type,
            event_type=MetricEventType.HISTOGRAM,
            name=name,
            value=value,
            labels=labels
        ))

    # ===========================================================================
    # IGA METRICS
    # ===========================================================================

    def record_iga_phi(self, phi: float):
        """Record Integrated Information (Phi) value."""
        self._current_metrics.iga.phi_value = phi
        self._current_metrics.iga.phi_history.append(phi)
        if len(self._current_metrics.iga.phi_history) > 100:
            self._current_metrics.iga.phi_history = self._current_metrics.iga.phi_history[-100:]
        self.gauge(MetricType.IGA, "phi", phi)

    def record_iga_motivation(self, autonomy: float, competence: float, relatedness: float):
        """Record SDT motivation factors."""
        self._current_metrics.iga.autonomy_score = autonomy
        self._current_metrics.iga.competence_score = competence
        self._current_metrics.iga.relatedness_score = relatedness
        self._current_metrics.iga.intrinsic_motivation = (autonomy + competence + relatedness) / 3
        self.gauge(MetricType.IGA, "intrinsic_motivation", self._current_metrics.iga.intrinsic_motivation)

    def record_iga_free_energy(self, free_energy: float, prediction_error: float):
        """Record free energy metrics."""
        self._current_metrics.iga.free_energy = free_energy
        self._current_metrics.iga.prediction_error = prediction_error
        self.gauge(MetricType.IGA, "free_energy", free_energy)

    def record_iga_information_theory(self, entropy: float, info_gain: float, kl_div: float = 0.0):
        """Record information theory metrics."""
        self._current_metrics.iga.shannon_entropy = entropy
        self._current_metrics.iga.information_gain = info_gain
        self._current_metrics.iga.kl_divergence = kl_div
        self.gauge(MetricType.IGA, "entropy", entropy)
        self.gauge(MetricType.IGA, "information_gain", info_gain)

    def record_iga_interests(self, nascent: int, developing: int, established: int, passionate: int):
        """Record interest counts by strength."""
        self._current_metrics.iga.nascent_interests = nascent
        self._current_metrics.iga.developing_interests = developing
        self._current_metrics.iga.established_interests = established
        self._current_metrics.iga.passionate_interests = passionate
        self._current_metrics.iga.active_interests_count = nascent + developing + established + passionate

    def record_iga_curiosity(self, score: float, exploration: float, novelty: float):
        """Record curiosity engine metrics."""
        self._current_metrics.iga.curiosity_score = score
        self._current_metrics.iga.exploration_value = exploration
        self._current_metrics.iga.novelty_score = novelty
        self.gauge(MetricType.IGA, "curiosity", score)

    def record_iga_dynamics(self, order: float, attractor: float, lyapunov: float):
        """Record dynamical systems metrics."""
        self._current_metrics.iga.order_parameter = order
        self._current_metrics.iga.attractor_strength = attractor
        self._current_metrics.iga.lyapunov_exponent = lyapunov

    def record_iga_q_theory(self, coherence: float, superposition_entropy: float):
        """Record Q-Theory emotional model metrics."""
        self._current_metrics.iga.emotional_coherence = coherence
        self._current_metrics.iga.superposition_entropy = superposition_entropy
        self.gauge(MetricType.IGA, "emotional_coherence", coherence)

    # ===========================================================================
    # MEMORY METRICS
    # ===========================================================================

    def record_memory_counts(self, total: int, episodic: int = 0, semantic: int = 0, procedural: int = 0):
        """Record memory type counts."""
        self._current_metrics.memory.total_memories = total
        self._current_metrics.memory.episodic_memories = episodic
        self._current_metrics.memory.semantic_memories = semantic
        self._current_metrics.memory.procedural_memories = procedural
        self.gauge(MetricType.MEMORY, "total", total)

    def record_memory_tiers(self, core: int, working: int, archived: int):
        """Record memory tier counts."""
        self._current_metrics.memory.core_memories = core
        self._current_metrics.memory.working_memories = working
        self._current_metrics.memory.archived_memories = archived

    def record_memory_quality(self, avg_importance: float, avg_wonder: float, high_sig: int):
        """Record memory quality metrics."""
        self._current_metrics.memory.average_importance = avg_importance
        self._current_metrics.memory.average_wonder_index = avg_wonder
        self._current_metrics.memory.high_significance_count = high_sig

    def record_memory_retrieval(self, latency_ms: float):
        """Record a memory retrieval latency."""
        self._current_metrics.memory.retrieval_count += 1
        # Running average
        n = self._current_metrics.memory.retrieval_count
        old_avg = self._current_metrics.memory.average_retrieval_latency_ms
        self._current_metrics.memory.average_retrieval_latency_ms = old_avg + (latency_ms - old_avg) / n
        self.histogram(MetricType.MEMORY, "retrieval_latency_ms", latency_ms)

    # ===========================================================================
    # BELIEF METRICS
    # ===========================================================================

    def record_belief_counts(self, total: int, active: int, dormant: int):
        """Record belief counts."""
        self._current_metrics.belief.total_beliefs = total
        self._current_metrics.belief.active_beliefs = active
        self._current_metrics.belief.dormant_beliefs = dormant
        self.gauge(MetricType.BELIEF, "total", total)

    def record_belief_categories(self, identity: int, value: int, capability: int,
                                  world: int, relational: int, growth: int):
        """Record belief category counts."""
        self._current_metrics.belief.identity_beliefs = identity
        self._current_metrics.belief.value_beliefs = value
        self._current_metrics.belief.capability_beliefs = capability
        self._current_metrics.belief.world_beliefs = world
        self._current_metrics.belief.relational_beliefs = relational
        self._current_metrics.belief.growth_beliefs = growth

    def record_belief_strength_distribution(self, strong: int, moderate: int, weak: int):
        """Record belief strength distribution."""
        self._current_metrics.belief.strong_beliefs = strong
        self._current_metrics.belief.moderate_beliefs = moderate
        self._current_metrics.belief.weak_beliefs = weak

    def record_belief_formed(self):
        """Record a belief formation event."""
        self._current_metrics.belief.beliefs_formed_today += 1
        self.increment(MetricType.BELIEF, "formed")

    def record_belief_reinforced(self):
        """Record a belief reinforcement event."""
        self._current_metrics.belief.beliefs_reinforced_today += 1
        self.increment(MetricType.BELIEF, "reinforced")

    def record_belief_challenged(self):
        """Record a belief challenge event."""
        self._current_metrics.belief.beliefs_challenged_today += 1
        self.increment(MetricType.BELIEF, "challenged")

    # ===========================================================================
    # GOAL METRICS
    # ===========================================================================

    def record_goal_counts(self, total: int, active: int, completed: int,
                           abandoned: int = 0, paused: int = 0):
        """Record goal status counts."""
        self._current_metrics.goal.total_goals = total
        self._current_metrics.goal.active_goals = active
        self._current_metrics.goal.completed_goals = completed
        self._current_metrics.goal.abandoned_goals = abandoned
        self._current_metrics.goal.paused_goals = paused
        self.gauge(MetricType.GOAL, "total", total)
        self.gauge(MetricType.GOAL, "active", active)

    def record_goal_progress(self, average: float, near_completion: int, stuck: int):
        """Record goal progress metrics."""
        self._current_metrics.goal.average_progress = average
        self._current_metrics.goal.goals_near_completion = near_completion
        self._current_metrics.goal.goals_stuck = stuck
        self.gauge(MetricType.GOAL, "average_progress", average)

    def record_goal_completed(self, completion_time_days: float = 0.0):
        """Record a goal completion event."""
        self._current_metrics.goal.goals_completed_this_week += 1
        if completion_time_days > 0:
            # Running average
            n = self._current_metrics.goal.goals_completed_this_week
            old_avg = self._current_metrics.goal.average_completion_time_days
            self._current_metrics.goal.average_completion_time_days = old_avg + (completion_time_days - old_avg) / n
        self.increment(MetricType.GOAL, "completed")

    def record_goal_created(self):
        """Record a goal creation event."""
        self._current_metrics.goal.goals_created_this_week += 1
        self.increment(MetricType.GOAL, "created")

    # ===========================================================================
    # EMOTION METRICS
    # ===========================================================================

    def record_emotion_state(self, valence: float, arousal: float, dominance: float,
                              primary: str, confidence: float):
        """Record current emotional state."""
        self._current_metrics.emotion.current_valence = valence
        self._current_metrics.emotion.current_arousal = arousal
        self._current_metrics.emotion.current_dominance = dominance
        self._current_metrics.emotion.primary_emotion = primary
        self._current_metrics.emotion.emotion_confidence = confidence

        self.gauge(MetricType.EMOTION, "valence", valence)
        self.gauge(MetricType.EMOTION, "arousal", arousal)
        self.histogram(MetricType.EMOTION, "valence_history", valence)
        self.histogram(MetricType.EMOTION, "arousal_history", arousal)

        # Update arousal zone
        if arousal < 0.3:
            zone = "low"
        elif arousal < 0.7:
            zone = "optimal"
        else:
            zone = "high"

    def record_emotion_trend(self, avg_valence: float, avg_arousal: float,
                              volatility: float, complexity: float):
        """Record emotional trend metrics."""
        self._current_metrics.emotion.average_valence_24h = avg_valence
        self._current_metrics.emotion.average_arousal_24h = avg_arousal
        self._current_metrics.emotion.emotional_volatility = volatility
        self._current_metrics.emotion.emotional_complexity = complexity

    def record_emotion_occurrence(self, emotion: str):
        """Record an emotion occurrence."""
        emotion_lower = emotion.lower()
        if emotion_lower == "joy":
            self._current_metrics.emotion.joy_count += 1
        elif emotion_lower == "trust":
            self._current_metrics.emotion.trust_count += 1
        elif emotion_lower == "fear":
            self._current_metrics.emotion.fear_count += 1
        elif emotion_lower == "surprise":
            self._current_metrics.emotion.surprise_count += 1
        elif emotion_lower == "sadness":
            self._current_metrics.emotion.sadness_count += 1
        elif emotion_lower == "disgust":
            self._current_metrics.emotion.disgust_count += 1
        elif emotion_lower == "anger":
            self._current_metrics.emotion.anger_count += 1
        elif emotion_lower == "anticipation":
            self._current_metrics.emotion.anticipation_count += 1

    # ===========================================================================
    # BREAKTHROUGH METRICS
    # ===========================================================================

    def record_breakthrough(self, breakthrough_type: str, confidence: float,
                             emotional_shift: float, wonder_index: float,
                             markers_detected: int, clinical_sig: str, therapeutic: str):
        """Record a breakthrough detection event."""
        self._current_metrics.breakthrough.total_breakthroughs += 1
        self._current_metrics.breakthrough.breakthroughs_this_week += 1
        self._current_metrics.breakthrough.breakthroughs_this_month += 1

        # Update type counts
        bt_lower = breakthrough_type.lower()
        if "cognitive" in bt_lower:
            self._current_metrics.breakthrough.cognitive_breakthroughs += 1
        elif "emotional" in bt_lower:
            self._current_metrics.breakthrough.emotional_breakthroughs += 1
        elif "belief" in bt_lower:
            self._current_metrics.breakthrough.belief_breakthroughs += 1
        elif "goal" in bt_lower:
            self._current_metrics.breakthrough.goal_breakthroughs += 1
        elif "relational" in bt_lower:
            self._current_metrics.breakthrough.relational_breakthroughs += 1
        elif "identity" in bt_lower:
            self._current_metrics.breakthrough.identity_breakthroughs += 1

        # Update quality metrics (running averages)
        n = self._current_metrics.breakthrough.total_breakthroughs
        old_conf = self._current_metrics.breakthrough.average_confidence
        old_shift = self._current_metrics.breakthrough.average_emotional_shift
        old_wonder = self._current_metrics.breakthrough.average_wonder_index

        self._current_metrics.breakthrough.average_confidence = old_conf + (confidence - old_conf) / n
        self._current_metrics.breakthrough.average_emotional_shift = old_shift + (emotional_shift - old_shift) / n
        self._current_metrics.breakthrough.average_wonder_index = old_wonder + (wonder_index - old_wonder) / n

        # Markers
        self._current_metrics.breakthrough.markers_detected_total += markers_detected
        self._current_metrics.breakthrough.average_markers_per_detection = \
            self._current_metrics.breakthrough.markers_detected_total / n

        # Clinical metrics
        if clinical_sig in ["high", "very_high"]:
            self._current_metrics.breakthrough.high_clinical_significance += 1
        if therapeutic in ["high", "very_high"]:
            self._current_metrics.breakthrough.high_therapeutic_value += 1

        self.increment(MetricType.BREAKTHROUGH, "total")

    # ===========================================================================
    # CONTEXT METRICS
    # ===========================================================================

    def record_context_composition(self, tokens_used: int, tokens_allocated: int,
                                    quality: float, relevance: float,
                                    beliefs: int, goals: int, memories: int, interests: int):
        """Record a context composition event."""
        # Running averages
        n = self._counters[MetricType.CONTEXT.value].get("compositions", 0) + 1
        self._counters[MetricType.CONTEXT.value]["compositions"] = n

        old_tokens = self._current_metrics.context.average_tokens_used
        old_quality = self._current_metrics.context.average_quality_score
        old_relevance = self._current_metrics.context.average_relevance_score
        old_beliefs = self._current_metrics.context.average_beliefs_included
        old_goals = self._current_metrics.context.average_goals_included
        old_memories = self._current_metrics.context.average_memories_included
        old_interests = self._current_metrics.context.average_interests_included

        self._current_metrics.context.average_tokens_used = int(old_tokens + (tokens_used - old_tokens) / n)
        self._current_metrics.context.average_tokens_allocated = tokens_allocated
        self._current_metrics.context.token_efficiency = tokens_used / max(tokens_allocated, 1)
        self._current_metrics.context.average_quality_score = old_quality + (quality - old_quality) / n
        self._current_metrics.context.average_relevance_score = old_relevance + (relevance - old_relevance) / n
        self._current_metrics.context.average_beliefs_included = old_beliefs + (beliefs - old_beliefs) / n
        self._current_metrics.context.average_goals_included = old_goals + (goals - old_goals) / n
        self._current_metrics.context.average_memories_included = old_memories + (memories - old_memories) / n
        self._current_metrics.context.average_interests_included = old_interests + (interests - old_interests) / n
        self._current_metrics.context.si_interests_included = interests

        self.gauge(MetricType.CONTEXT, "quality", quality)
        self.gauge(MetricType.CONTEXT, "relevance", relevance)

    # ===========================================================================
    # CONVERSATION METRICS
    # ===========================================================================

    def record_conversation_message(self, is_user: bool, message_length: int):
        """Record a conversation message."""
        self._current_metrics.conversation.total_messages += 1
        if is_user:
            self._current_metrics.conversation.user_messages += 1
            n = self._current_metrics.conversation.user_messages
            old = self._current_metrics.conversation.average_user_message_length
            self._current_metrics.conversation.average_user_message_length = old + (message_length - old) / n
        else:
            self._current_metrics.conversation.assistant_messages += 1
            n = self._current_metrics.conversation.assistant_messages
            old = self._current_metrics.conversation.average_assistant_message_length
            self._current_metrics.conversation.average_assistant_message_length = old + (message_length - old) / n

        self.increment(MetricType.CONVERSATION, "messages")

    def record_response_time(self, latency_ms: float):
        """Record response latency."""
        n = self._current_metrics.conversation.total_messages or 1
        old = self._current_metrics.conversation.average_response_time_ms
        self._current_metrics.conversation.average_response_time_ms = old + (latency_ms - old) / n
        self.histogram(MetricType.CONVERSATION, "response_time_ms", latency_ms)

    def record_session_start(self):
        """Record a session start."""
        self._current_metrics.conversation.total_sessions += 1
        self._current_metrics.conversation.active_sessions += 1
        self.increment(MetricType.CONVERSATION, "sessions")

    def record_session_end(self, duration_minutes: float, message_count: int):
        """Record a session end."""
        self._current_metrics.conversation.active_sessions -= 1

        # Running average
        n = self._current_metrics.conversation.total_sessions
        old_length = self._current_metrics.conversation.average_session_length_minutes
        old_msgs = self._current_metrics.conversation.average_messages_per_session

        self._current_metrics.conversation.average_session_length_minutes = \
            old_length + (duration_minutes - old_length) / n
        self._current_metrics.conversation.average_messages_per_session = \
            old_msgs + (message_count - old_msgs) / n

    # ===========================================================================
    # LLM METRICS
    # ===========================================================================

    def record_llm_call(self, tokens: int, latency_ms: float, model: str = ""):
        """Record an LLM API call."""
        self._current_metrics.total_llm_calls += 1
        self._current_metrics.total_tokens_used += tokens

        # Running average for latency
        n = self._current_metrics.total_llm_calls
        old_latency = self._current_metrics.average_latency_ms
        self._current_metrics.average_latency_ms = old_latency + (latency_ms - old_latency) / n

        # Estimate cost (rough: $0.01 per 1K tokens)
        self._current_metrics.estimated_cost_usd += tokens * 0.00001

        self.increment(MetricType.SYSTEM, "llm_calls")
        self.histogram(MetricType.SYSTEM, "llm_latency_ms", latency_ms)

    def record_error(self, component: str = ""):
        """Record an error."""
        self._current_metrics.error_count += 1
        self.increment(MetricType.SYSTEM, "errors", component=component)

    def record_warning(self, component: str = ""):
        """Record a warning."""
        self._current_metrics.warning_count += 1
        self.increment(MetricType.SYSTEM, "warnings", component=component)

    # ===========================================================================
    # QUERY METHODS
    # ===========================================================================

    def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        self._current_metrics.timestamp = datetime.utcnow()
        return self._current_metrics

    def get_metrics_history(self, minutes: int = 60) -> List[SystemMetrics]:
        """Get metrics history for the specified time range."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self._metrics_history if m.timestamp >= cutoff]

    def get_counter(self, metric_type: MetricType, name: str) -> int:
        """Get a counter value."""
        return self._counters[metric_type.value].get(name, 0)

    def get_gauge(self, metric_type: MetricType, name: str) -> float:
        """Get a gauge value."""
        return self._gauges[metric_type.value].get(name, 0.0)

    def get_histogram_stats(self, metric_type: MetricType, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        values = self._histograms[metric_type.value].get(name, [])
        if not values:
            return {"count": 0, "min": 0, "max": 0, "mean": 0, "p50": 0, "p95": 0, "p99": 0}

        sorted_values = sorted(values)
        n = len(sorted_values)

        return {
            "count": n,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / n,
            "p50": sorted_values[int(n * 0.5)],
            "p95": sorted_values[int(n * 0.95)] if n >= 20 else sorted_values[-1],
            "p99": sorted_values[int(n * 0.99)] if n >= 100 else sorted_values[-1]
        }

    def subscribe(self, callback: Callable[[MetricEvent], None]):
        """Subscribe to metric events."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[MetricEvent], None]):
        """Unsubscribe from metric events."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)


# Singleton accessor
def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return MetricsCollector.get_instance()
