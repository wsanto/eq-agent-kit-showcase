"""
System-wide metric dataclasses for ANIMA AgentKit.

These dataclasses define the structure of metrics collected from
all major system components.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class MetricType(str, Enum):
    """Types of metrics collected by the system."""
    IGA = "iga"
    MEMORY = "memory"
    BELIEF = "belief"
    GOAL = "goal"
    EMOTION = "emotion"
    BREAKTHROUGH = "breakthrough"
    CONTEXT = "context"
    CONVERSATION = "conversation"
    SYSTEM = "system"


@dataclass
class IGAMetrics:
    """
    Metrics from the Interest Generation Algorithm.

    Captures consciousness-based calculations, motivation factors,
    and interest formation dynamics.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Integrated Information (Phi)
    phi_value: float = 0.0
    phi_history: List[float] = field(default_factory=list)

    # Self-Determination Theory
    autonomy_score: float = 0.0
    competence_score: float = 0.0
    relatedness_score: float = 0.0
    intrinsic_motivation: float = 0.0

    # Free Energy Principle
    free_energy: float = 0.0
    prediction_error: float = 0.0

    # Information Theory
    shannon_entropy: float = 0.0
    information_gain: float = 0.0
    kl_divergence: float = 0.0

    # Interest Formation
    active_interests_count: int = 0
    nascent_interests: int = 0
    developing_interests: int = 0
    established_interests: int = 0
    passionate_interests: int = 0

    # Curiosity Engine
    curiosity_score: float = 0.0
    exploration_value: float = 0.0
    novelty_score: float = 0.0

    # Phase Transition
    order_parameter: float = 0.0
    attractor_strength: float = 0.0
    lyapunov_exponent: float = 0.0

    # Q-Theory Emotional Model
    emotional_coherence: float = 0.0
    superposition_entropy: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'consciousness': {
                'phi': self.phi_value,
                'phi_trend': self.phi_history[-10:] if self.phi_history else []
            },
            'motivation': {
                'autonomy': self.autonomy_score,
                'competence': self.competence_score,
                'relatedness': self.relatedness_score,
                'intrinsic': self.intrinsic_motivation
            },
            'free_energy': {
                'value': self.free_energy,
                'prediction_error': self.prediction_error
            },
            'information_theory': {
                'entropy': self.shannon_entropy,
                'information_gain': self.information_gain,
                'kl_divergence': self.kl_divergence
            },
            'interests': {
                'total': self.active_interests_count,
                'nascent': self.nascent_interests,
                'developing': self.developing_interests,
                'established': self.established_interests,
                'passionate': self.passionate_interests
            },
            'curiosity': {
                'score': self.curiosity_score,
                'exploration_value': self.exploration_value,
                'novelty': self.novelty_score
            },
            'dynamics': {
                'order_parameter': self.order_parameter,
                'attractor_strength': self.attractor_strength,
                'lyapunov': self.lyapunov_exponent
            },
            'q_theory': {
                'coherence': self.emotional_coherence,
                'superposition_entropy': self.superposition_entropy
            }
        }


@dataclass
class MemoryMetrics:
    """
    Metrics from the memory system.

    Tracks memory counts, tiers, and retrieval performance.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Memory Counts by Type
    total_memories: int = 0
    episodic_memories: int = 0
    semantic_memories: int = 0
    procedural_memories: int = 0

    # Memory Tiers
    core_memories: int = 0
    working_memories: int = 0
    archived_memories: int = 0

    # Memory Quality
    average_importance: float = 0.0
    average_wonder_index: float = 0.0
    high_significance_count: int = 0

    # Retrieval Metrics
    retrieval_count: int = 0
    average_retrieval_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0

    # GraphRAG Metrics
    total_nodes: int = 0
    total_relationships: int = 0
    average_node_degree: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'counts': {
                'total': self.total_memories,
                'episodic': self.episodic_memories,
                'semantic': self.semantic_memories,
                'procedural': self.procedural_memories
            },
            'tiers': {
                'core': self.core_memories,
                'working': self.working_memories,
                'archived': self.archived_memories
            },
            'quality': {
                'avg_importance': self.average_importance,
                'avg_wonder': self.average_wonder_index,
                'high_significance': self.high_significance_count
            },
            'retrieval': {
                'count': self.retrieval_count,
                'avg_latency_ms': self.average_retrieval_latency_ms,
                'cache_hit_rate': self.cache_hit_rate
            },
            'graph': {
                'nodes': self.total_nodes,
                'relationships': self.total_relationships,
                'avg_degree': self.average_node_degree
            }
        }


@dataclass
class BeliefMetrics:
    """
    Metrics from the belief system.

    Tracks belief formation, strength, and evolution.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Belief Counts
    total_beliefs: int = 0
    active_beliefs: int = 0
    dormant_beliefs: int = 0

    # Belief Categories
    identity_beliefs: int = 0
    value_beliefs: int = 0
    capability_beliefs: int = 0
    world_beliefs: int = 0
    relational_beliefs: int = 0
    growth_beliefs: int = 0

    # Belief Strength Distribution
    strong_beliefs: int = 0  # strength > 0.8
    moderate_beliefs: int = 0  # 0.5 < strength <= 0.8
    weak_beliefs: int = 0  # strength <= 0.5

    # Belief Dynamics
    average_strength: float = 0.0
    average_reference_count: float = 0.0
    beliefs_formed_today: int = 0
    beliefs_reinforced_today: int = 0
    beliefs_challenged_today: int = 0

    # Validation Metrics
    average_validation_score: float = 0.0
    user_confirmed_beliefs: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'counts': {
                'total': self.total_beliefs,
                'active': self.active_beliefs,
                'dormant': self.dormant_beliefs
            },
            'categories': {
                'identity': self.identity_beliefs,
                'value': self.value_beliefs,
                'capability': self.capability_beliefs,
                'world': self.world_beliefs,
                'relational': self.relational_beliefs,
                'growth': self.growth_beliefs
            },
            'strength_distribution': {
                'strong': self.strong_beliefs,
                'moderate': self.moderate_beliefs,
                'weak': self.weak_beliefs
            },
            'dynamics': {
                'avg_strength': self.average_strength,
                'avg_references': self.average_reference_count,
                'formed_today': self.beliefs_formed_today,
                'reinforced_today': self.beliefs_reinforced_today,
                'challenged_today': self.beliefs_challenged_today
            },
            'validation': {
                'avg_score': self.average_validation_score,
                'user_confirmed': self.user_confirmed_beliefs
            }
        }


@dataclass
class GoalMetrics:
    """
    Metrics from the goal system.

    Tracks goal progress, completion, and engagement.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Goal Counts by Status
    total_goals: int = 0
    active_goals: int = 0
    completed_goals: int = 0
    abandoned_goals: int = 0
    paused_goals: int = 0

    # Goal Progress
    average_progress: float = 0.0
    goals_near_completion: int = 0  # progress > 0.8
    goals_stuck: int = 0  # no progress in 7+ days

    # Goal Priority
    high_priority_goals: int = 0
    medium_priority_goals: int = 0
    low_priority_goals: int = 0

    # Goal Velocity
    goals_completed_this_week: int = 0
    goals_created_this_week: int = 0
    average_completion_time_days: float = 0.0

    # Goal Relevance
    average_relevance_score: float = 0.0
    highly_relevant_goals: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'counts': {
                'total': self.total_goals,
                'active': self.active_goals,
                'completed': self.completed_goals,
                'abandoned': self.abandoned_goals,
                'paused': self.paused_goals
            },
            'progress': {
                'average': self.average_progress,
                'near_completion': self.goals_near_completion,
                'stuck': self.goals_stuck
            },
            'priority': {
                'high': self.high_priority_goals,
                'medium': self.medium_priority_goals,
                'low': self.low_priority_goals
            },
            'velocity': {
                'completed_week': self.goals_completed_this_week,
                'created_week': self.goals_created_this_week,
                'avg_completion_days': self.average_completion_time_days
            },
            'relevance': {
                'average': self.average_relevance_score,
                'highly_relevant': self.highly_relevant_goals
            }
        }


@dataclass
class EmotionMetrics:
    """
    Metrics from the emotion and arousal system.

    Tracks emotional state, trends, and regulation.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Current State
    current_valence: float = 0.0
    current_arousal: float = 0.0
    current_dominance: float = 0.0
    primary_emotion: str = ""
    emotion_confidence: float = 0.0

    # Emotional Trends
    average_valence_24h: float = 0.0
    average_arousal_24h: float = 0.0
    emotional_volatility: float = 0.0
    emotional_complexity: float = 0.0

    # Emotion Distribution (Plutchik's 8)
    joy_count: int = 0
    trust_count: int = 0
    fear_count: int = 0
    surprise_count: int = 0
    sadness_count: int = 0
    disgust_count: int = 0
    anger_count: int = 0
    anticipation_count: int = 0

    # Arousal Zones
    low_arousal_time_percent: float = 0.0
    optimal_arousal_time_percent: float = 0.0
    high_arousal_time_percent: float = 0.0

    # TWASS Metrics
    baseline_arousal: float = 0.0
    arousal_trend: str = "stable"  # rising, falling, stable

    # Regulation
    regulation_effort: float = 0.0
    polyvagal_state: str = "ventral_vagal"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'current': {
                'valence': self.current_valence,
                'arousal': self.current_arousal,
                'dominance': self.current_dominance,
                'primary_emotion': self.primary_emotion,
                'confidence': self.emotion_confidence
            },
            'trends': {
                'avg_valence_24h': self.average_valence_24h,
                'avg_arousal_24h': self.average_arousal_24h,
                'volatility': self.emotional_volatility,
                'complexity': self.emotional_complexity
            },
            'distribution': {
                'joy': self.joy_count,
                'trust': self.trust_count,
                'fear': self.fear_count,
                'surprise': self.surprise_count,
                'sadness': self.sadness_count,
                'disgust': self.disgust_count,
                'anger': self.anger_count,
                'anticipation': self.anticipation_count
            },
            'arousal_zones': {
                'low_percent': self.low_arousal_time_percent,
                'optimal_percent': self.optimal_arousal_time_percent,
                'high_percent': self.high_arousal_time_percent
            },
            'twass': {
                'baseline': self.baseline_arousal,
                'trend': self.arousal_trend
            },
            'regulation': {
                'effort': self.regulation_effort,
                'polyvagal_state': self.polyvagal_state
            }
        }


@dataclass
class BreakthroughMetrics:
    """
    Metrics from the breakthrough detection system.

    Tracks breakthrough moments and their impact.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Breakthrough Counts
    total_breakthroughs: int = 0
    breakthroughs_this_week: int = 0
    breakthroughs_this_month: int = 0

    # Breakthrough Types
    cognitive_breakthroughs: int = 0
    emotional_breakthroughs: int = 0
    belief_breakthroughs: int = 0
    goal_breakthroughs: int = 0
    relational_breakthroughs: int = 0
    identity_breakthroughs: int = 0

    # Breakthrough Quality
    average_confidence: float = 0.0
    average_emotional_shift: float = 0.0
    average_wonder_index: float = 0.0

    # Clinical Metrics
    high_clinical_significance: int = 0
    high_therapeutic_value: int = 0

    # Detection Metrics
    markers_detected_total: int = 0
    average_markers_per_detection: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'counts': {
                'total': self.total_breakthroughs,
                'this_week': self.breakthroughs_this_week,
                'this_month': self.breakthroughs_this_month
            },
            'types': {
                'cognitive': self.cognitive_breakthroughs,
                'emotional': self.emotional_breakthroughs,
                'belief': self.belief_breakthroughs,
                'goal': self.goal_breakthroughs,
                'relational': self.relational_breakthroughs,
                'identity': self.identity_breakthroughs
            },
            'quality': {
                'avg_confidence': self.average_confidence,
                'avg_emotional_shift': self.average_emotional_shift,
                'avg_wonder_index': self.average_wonder_index
            },
            'clinical': {
                'high_significance': self.high_clinical_significance,
                'high_therapeutic': self.high_therapeutic_value
            },
            'detection': {
                'total_markers': self.markers_detected_total,
                'avg_markers': self.average_markers_per_detection
            }
        }


@dataclass
class ContextMetrics:
    """
    Metrics from the intelligent context composer.

    Tracks context quality and composition efficiency.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Token Usage
    average_tokens_used: int = 0
    average_tokens_allocated: int = 0
    token_efficiency: float = 0.0

    # Context Quality
    average_quality_score: float = 0.0
    average_relevance_score: float = 0.0

    # Context Composition
    average_beliefs_included: float = 0.0
    average_goals_included: float = 0.0
    average_memories_included: float = 0.0
    average_interests_included: float = 0.0

    # Priority Distribution
    high_priority_items: int = 0
    medium_priority_items: int = 0
    low_priority_items: int = 0

    # S.I. Interests
    si_interests_included: int = 0
    si_interest_relevance: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'tokens': {
                'avg_used': self.average_tokens_used,
                'avg_allocated': self.average_tokens_allocated,
                'efficiency': self.token_efficiency
            },
            'quality': {
                'avg_score': self.average_quality_score,
                'avg_relevance': self.average_relevance_score
            },
            'composition': {
                'avg_beliefs': self.average_beliefs_included,
                'avg_goals': self.average_goals_included,
                'avg_memories': self.average_memories_included,
                'avg_interests': self.average_interests_included
            },
            'priority': {
                'high': self.high_priority_items,
                'medium': self.medium_priority_items,
                'low': self.low_priority_items
            },
            'si_interests': {
                'included': self.si_interests_included,
                'relevance': self.si_interest_relevance
            }
        }


@dataclass
class ConversationMetrics:
    """
    Metrics from conversation tracking.

    Tracks engagement, session length, and message patterns.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Session Metrics
    total_sessions: int = 0
    active_sessions: int = 0
    average_session_length_minutes: float = 0.0
    average_messages_per_session: float = 0.0

    # Message Metrics
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    average_user_message_length: float = 0.0
    average_assistant_message_length: float = 0.0

    # Engagement Metrics
    average_response_time_ms: float = 0.0
    conversation_depth: float = 0.0  # Follow-up ratio
    topic_diversity: float = 0.0

    # User Patterns
    returning_users: int = 0
    new_users_today: int = 0
    daily_active_users: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'sessions': {
                'total': self.total_sessions,
                'active': self.active_sessions,
                'avg_length_min': self.average_session_length_minutes,
                'avg_messages': self.average_messages_per_session
            },
            'messages': {
                'total': self.total_messages,
                'user': self.user_messages,
                'assistant': self.assistant_messages,
                'avg_user_length': self.average_user_message_length,
                'avg_assistant_length': self.average_assistant_message_length
            },
            'engagement': {
                'avg_response_time_ms': self.average_response_time_ms,
                'depth': self.conversation_depth,
                'topic_diversity': self.topic_diversity
            },
            'users': {
                'returning': self.returning_users,
                'new_today': self.new_users_today,
                'dau': self.daily_active_users
            }
        }


@dataclass
class SystemMetrics:
    """
    Aggregated system-wide metrics.

    Combines all component metrics into a single view.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Component Metrics
    iga: IGAMetrics = field(default_factory=IGAMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    belief: BeliefMetrics = field(default_factory=BeliefMetrics)
    goal: GoalMetrics = field(default_factory=GoalMetrics)
    emotion: EmotionMetrics = field(default_factory=EmotionMetrics)
    breakthrough: BreakthroughMetrics = field(default_factory=BreakthroughMetrics)
    context: ContextMetrics = field(default_factory=ContextMetrics)
    conversation: ConversationMetrics = field(default_factory=ConversationMetrics)

    # System Health
    health_score: float = 0.0  # 0-100
    error_count: int = 0
    warning_count: int = 0
    uptime_seconds: int = 0

    # LLM Usage
    total_tokens_used: int = 0
    total_llm_calls: int = 0
    average_latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'health': {
                'score': self.health_score,
                'errors': self.error_count,
                'warnings': self.warning_count,
                'uptime_seconds': self.uptime_seconds
            },
            'llm': {
                'total_tokens': self.total_tokens_used,
                'total_calls': self.total_llm_calls,
                'avg_latency_ms': self.average_latency_ms,
                'estimated_cost_usd': self.estimated_cost_usd
            },
            'components': {
                'iga': self.iga.to_dict(),
                'memory': self.memory.to_dict(),
                'belief': self.belief.to_dict(),
                'goal': self.goal.to_dict(),
                'emotion': self.emotion.to_dict(),
                'breakthrough': self.breakthrough.to_dict(),
                'context': self.context.to_dict(),
                'conversation': self.conversation.to_dict()
            }
        }
