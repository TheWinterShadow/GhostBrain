"""LLM Context and VAD factory."""

from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMAssistantAggregator,
    LLMContextAggregatorPair,
    LLMUserAggregator,
    LLMUserAggregatorParams,
)

from ghost_brain.tools.search import search_web


def create_context_and_aggregators(
    sample_rate: int = 8000,
) -> tuple[LLMContext, LLMUserAggregator, LLMAssistantAggregator]:
    """
    Create shared LLM context and user/assistant context aggregators with VAD.

    Args:
        sample_rate: Audio sample rate (8000 for Twilio). Silero supports 8000 or 16000.

    Returns:
        Tuple of (context, user_aggregator, assistant_aggregator).
    """
    context = LLMContext(tools=ToolsSchema(standard_tools=[search_web]))  # type: ignore[arg-type]
    vad_analyzer = SileroVADAnalyzer(
        sample_rate=sample_rate,
        params=VADParams(stop_secs=0.2),
    )
    user_params = LLMUserAggregatorParams(vad_analyzer=vad_analyzer)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=user_params,
    )
    return context, user_aggregator, assistant_aggregator  # type: ignore[return-value]
