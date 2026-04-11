from typing import TypedDict, Optional, Dict, Any, List, Literal

FieldRating = Literal["Poor", "Fair", "Good", "Excellent"]
"""A literal type for rating different fields of a story."""

class FieldFeedback(TypedDict):
    """Represents feedback for a single field in a story."""
    rating: FieldRating
    reason: str

class StoryState(TypedDict, total=False):
    """
    Represents the state of a story as it moves through the processing workflow.

    Attributes:
        story (Dict[str, Any]): The current version of the story being processed.
        checker_response (Optional[Dict[str, FieldFeedback]]): Feedback from the checker service.
        rag_chunks (Optional[str]): Context retrieved by the RAG service.
        attempts (int): A counter for the number of processing attempts.
        event_log (List[str]): A log of events that occurred during processing.
        status (Literal["in_progress", "complete", "error"]): The current status of the story.
        cache_key (Optional[str]): The key used for caching the state in Redis.
    """
    story: Dict[str, Any]  # Current version of the story
    checker_response: Optional[Dict[str, FieldFeedback]]  # field -> rating & reason
    rag_chunks: Optional[str]  # Retrieved context used for RAG-enhancement
    attempts: int  # Iteration counter
    event_log: List[str]  # Sequential log of all pipeline messages/events
    status: Literal["in_progress", "complete", "error"]  # For graph control & UI
    cache_key: Optional[str] # Key for caching the state in Redis
