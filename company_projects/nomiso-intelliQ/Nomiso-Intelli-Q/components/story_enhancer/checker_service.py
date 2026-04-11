import json
import logging
from typing import Dict, Any, List, Optional
from components.common.llm_client import LLMClient
from components.common.prompts import (
    get_checker_system_prompt1, get_checker_user_prompt1, 
    get_checker_system_prompt, get_checker_user_prompt,
    get_heading_checker_system_prompt, get_heading_checker_user_prompt,
    get_heading_checker_system_prompt1, get_heading_checker_user_prompt1
)
from pathlib import Path

class CheckerService:
    """
    A service for checking and providing feedback on story content.
    """
    def __init__(self, llm_client, config):
        """Initialize the checker service."""
        self.llm_client = llm_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.enhancement_log = []  # Track all enhancements
    
    def review_story(self, story: Dict[str, Any], rag_chunks: str, 
                    previous_feedback: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Review a story and provide structured feedback.

        Args:
            story (Dict[str, Any]): The story to review
            rag_chunks (str): Context from the RAG service
            previous_feedback (Optional[Dict]): Previous feedback for each heading

        Returns:
            Dict[str, Any]: Dictionary containing feedback and enhancement needs
        """
        # Check if heading mode is enabled
        if hasattr(self.config, 'heading_mode') and self.config.heading_mode:
            # Heading mode: process individual headings
            headings = story.get("headings", [])
            if not headings:
                self.logger.warning("No headings found in story")
                return {
                    'feedback': {},
                    'needs_enhancement': {}
                }
            result = self._review_headings(headings, rag_chunks, previous_feedback)
        else:
            # Non-heading mode: process complete document
            result = self._review_complete_document(story, rag_chunks, previous_feedback)
                    
        return result

    def _review_headings(self, headings: List[Dict[str, Any]], rag_chunks: str,
                        previous_feedback: Optional[Dict] = None, document_summary: str = "") -> Dict[str, Any]:
        """
        Review each heading in the story and provide structured feedback.

        Args:
            headings (List[Dict[str, Any]]): List of headings to review
            rag_chunks (str): RAG context chunks for additional information
            previous_feedback (Optional[Dict]): Previous feedback for each heading
            document_summary (str): Concise summary of the document for context (optional)

        Returns:
            Dict[str, Any]: Dictionary containing feedback and enhancement needs
        """
        feedback = {}
        needs_enhancement = {}

        for i, heading in enumerate(headings):
            heading_id = heading.get("heading_id", f"unknown-{i}")
            title = heading.get("title", "")
            self.logger.debug(f"[CHECKING] Heading Title: '{title}'")

            # Check if this specific heading has previous feedback
            heading_has_previous_feedback = (
                previous_feedback is not None and 
                previous_feedback.get('feedback', {}).get(heading_id) is not None
            )
            
            if not heading_has_previous_feedback:
                self.logger.debug(f"[PROMPT] Generating first-time review for heading {heading_id}")
                system_prompt = get_heading_checker_system_prompt1(self.config.domain)
                user_prompt = get_heading_checker_user_prompt1(
                    self.config.domain,
                    document_summary,
                    rag_chunks,
                    json.dumps(heading, indent=2)
                )
            else:
                self.logger.debug(f"[PROMPT] Generating subsequent review for heading {heading_id}")
                system_prompt = get_heading_checker_system_prompt(self.config.domain)
                user_prompt = get_heading_checker_user_prompt(
                    self.config.domain,
                    document_summary,
                    rag_chunks,
                    json.dumps(heading, indent=2)
                )

            response_obj = self.llm_client.generate_response(system_prompt, user_prompt)

            if "error" in response_obj:
                self.logger.error(f"[LLM ERROR] Heading {heading_id}: {response_obj['error']}")
                feedback[heading_id] = {
                    "rating": "Low",
                    "reason": "Failed to evaluate due to LLM error",
                    "suggestions": ["Retry evaluation"]
                }
                needs_enhancement[heading_id] = True
                continue

            try:
                heading_feedback = response_obj

                required_fields = ["heading_id", "rating", "reason"]
                feedback_keys_lower = {k.lower() for k in heading_feedback.keys()}
                missing_fields = [field for field in required_fields if field.lower() not in feedback_keys_lower]

                if missing_fields:
                    raise ValueError(f"Missing required fields (case-insensitive): {missing_fields}")

                valid_ratings = ["very low", "low", "medium", "good", "excellent"]
                rating = heading_feedback.get("rating", "")
                if rating.lower() not in valid_ratings:
                    raise ValueError(f"Invalid rating value: '{rating}'")

                reason = heading_feedback.get("reason", "")
                suggestions = heading_feedback.get("suggestions", [])

                # Log detailed feedback per heading
                self.logger.info(f"[FEEDBACK] Heading ID: {title}")
                self.logger.info(f"  Rating: {rating}")
                self.logger.info(f"  Reason: {reason}")
                self.logger.info(f"  Suggestions: {suggestions}")
                if rating.lower() != "excellent":
                    if not isinstance(suggestions, list):
                        raise ValueError("Suggestions must be a list for non-Excellent ratings")
                    self.logger.debug(f"  Suggestions: {suggestions}")
                    needs_enhancement[heading_id] = True
                else:
                    self.logger.debug(f"  Suggestions: Skipped (rating is Excellent)")
                    heading_feedback["suggestions"] = []
                    needs_enhancement[heading_id] = False

                feedback[heading_id] = heading_feedback

            except json.JSONDecodeError as e:
                self.logger.error(f"[PARSING ERROR] Invalid JSON for heading {heading_id}: {e}")
                feedback[heading_id] = {
                    "rating": "Low",
                    "reason": "Failed to parse LLM response",
                    "suggestions": ["Retry evaluation"]
                }
                needs_enhancement[heading_id] = True
            except ValueError as e:
                self.logger.error(f"[VALIDATION ERROR] Heading {heading_id}: {e}")
                feedback[heading_id] = {
                    "rating": "Low",
                    "reason": str(e),
                    "suggestions": ["Retry evaluation"]
                }
                needs_enhancement[heading_id] = True
            except Exception as e:
                self.logger.error(f"[UNEXPECTED ERROR] Heading {heading_id}: {e}")
                feedback[heading_id] = {
                    "rating": "Low",
                    "reason": "Unexpected error during evaluation",
                    "suggestions": ["Retry evaluation"]
                }
                needs_enhancement[heading_id] = True

        return {
            "feedback": feedback,
            "needs_enhancement": needs_enhancement
        }




    def _review_complete_document(self, story: Dict[str, Any], rag_chunks: str, 
                                previous_feedback: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Review the complete document and provide structured feedback.

        Args:
            story (Dict[str, Any]): The complete story to review
            rag_chunks (str): Context from the RAG service
            previous_feedback (Optional[Dict]): Previous feedback if this is a subsequent review

        Returns:
            Dict[str, Any]: Dictionary containing feedback and enhancement needs
        """
        self.logger.info("[CHECKING] Starting complete document review")

        # Check if there's previous feedback for the document
        document_has_previous_feedback = (
            previous_feedback is not None and 
            previous_feedback.get('feedback', {}).get('document') is not None
        )
        
        if not document_has_previous_feedback:
            self.logger.info("[CHECKING] Generating First-time review...")
            system_prompt = get_checker_system_prompt1(self.config.domain)
            user_prompt = get_checker_user_prompt1(
                self.config.domain,
                json.dumps(story, indent=2),
                rag_chunks
            )
         
        else:
            self.logger.info("[CHECKING] Generating Subsequent review...")
            system_prompt = get_checker_system_prompt(self.config.domain)
            user_prompt = get_checker_user_prompt(
                self.config.domain,
                json.dumps(story, indent=2),
                json.dumps(previous_feedback, indent=2),
                rag_chunks
            )

        # Get response from LLM
        response_obj = self.llm_client.generate_response(system_prompt, user_prompt)

        if "error" in response_obj:
            self.logger.error(f"[LLM ERROR] Failed to generate feedback: {response_obj['error']}")
            return {
                'feedback': {'document': {
                    "rating": "Low",
                    "reason": "Failed to evaluate due to LLM error",
                    "suggestions": ["Retry evaluation"]
                }},
                'needs_enhancement': {'document': True}
            }

        try:
            document_feedback = response_obj  # Already a dictionary

            self.logger.info("[CHECKING] Document feedback received from LLM")
            self.logger.info(f"[DEBUG] Response type: {type(response_obj)}")
            self.logger.info(f"[DEBUG] Response content: {response_obj}")
            self.logger.debug(f"[RAW_FEEDBACK] {json.dumps(document_feedback, indent=2)}")

            # Log each field's feedback individually
            for field_name, field_info in document_feedback.items():
                if isinstance(field_info, dict):
                    # Try both uppercase and lowercase field names
                    rating = field_info.get("Rating") or field_info.get("rating", "N/A")
                    reason = field_info.get("Reason") or field_info.get("reason", "N/A")
                    self.logger.info(f"[FEEDBACK] Field: '{field_name}' \n Rating: {rating} \n Reason: {reason}")
                else:
                    self.logger.warning(f"[FEEDBACK] Field '{field_name}' is not a dictionary: {type(field_info)} - {field_info}")

            # Determine if any field needs enhancement
            needs_enhancement = any(
                (field_info.get('Rating') or field_info.get('rating', '')).lower() != 'excellent'
                for field_info in document_feedback.values()
                if isinstance(field_info, dict)
            )

            self.logger.info(f"[SUMMARY] Enhancement Needed: {'Yes' if needs_enhancement else 'No'}")

            return {
                'feedback': {'document': document_feedback},
                'needs_enhancement': {'document': needs_enhancement}
            }

        except json.JSONDecodeError as e:
            self.logger.error(f"[PARSING ERROR] Invalid JSON in LLM response: {e}")
            return {
                'feedback': {'document': {
                    "rating": "Low",
                    "reason": "Failed to parse LLM response",
                    "suggestions": ["Retry evaluation"]
                }},
                'needs_enhancement': {'document': True}
            }
        except Exception as e:
            self.logger.error(f"[UNEXPECTED ERROR] Review failed with error: {e}")
            return {
                'feedback': {'document': {
                    "rating": "Low",
                    "reason": "Unexpected error during evaluation",
                    "suggestions": ["Retry evaluation"]
                }},
                'needs_enhancement': {'document': True}
            }
