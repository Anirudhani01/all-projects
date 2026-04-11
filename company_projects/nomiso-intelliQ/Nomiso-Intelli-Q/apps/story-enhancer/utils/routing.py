from typing import Dict, Any
from models.story_state import StoryState

class RoutingLogic:
    """
    A class containing static methods for routing logic in the workflow.
    """
    @staticmethod
    def should_continue(state: StoryState, max_attempts: int) -> str:
        """
        Determine the next step in the workflow.

        This method evaluates the current state of the story to decide whether to
        continue with another iteration of enhancement or to finalize the process.
        The decision is based on the feedback from the checker service and the
        number of attempts made.

        Args:
            state (StoryState): The current state of the story.
            max_attempts (int): The maximum number of enhancement attempts allowed.

        Returns:
            str: 'finalize' if the story is considered complete or if the max
                 attempts have been reached, otherwise 'regenerate'.
        """
        checker = state.get("checker_response", {})
        acceptable = {"good", "excellent"}
        
        all_fields_good = all(
            isinstance(field, dict) and
            field.get("Rating", "").strip().lower() in acceptable
            for field in checker.values()
        )
        
        if all_fields_good or state.get("attempts", 0) >= max_attempts:
            return "finalize"
        return "regenerate"
