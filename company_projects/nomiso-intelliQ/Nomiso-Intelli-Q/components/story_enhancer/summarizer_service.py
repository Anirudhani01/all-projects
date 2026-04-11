import json
import logging
from typing import Dict, Any, List, Optional
from components.common.llm_client import LLMClient
from components.common.prompts import get_summarizer_system_prompt, get_summarizer_user_prompt


class SummarizerService:
    """
    A service for generating concise summaries of documents.
    """
    def __init__(self, llm_client, config):
        """Initialize the summarizer service."""
        self.llm_client = llm_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.total_usage_stats = {
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_tokens': 0,
            'api_calls': 0
        }

    def _generate_plain_text(self, headings: List[Dict[str, Any]]) -> str:
        """Convert headings to plain text for summarization."""
        text_parts = []
        for heading in headings:
            title = heading.get("title", "")
            content = heading.get("content", [])
            if isinstance(content, list):
                content = "\n".join(str(item) for item in content)
            text_parts.append(f"{title}\n{content}")
        return "\n\n".join(text_parts)

    def summarize_document(self, headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a concise summary of the document using optimized cumulative approach.
        
        Args:
            headings: List of document headings and their content
            
        Returns:
            Dict[str, Any]: Contains 'summary' and 'stats' keys
        """
        if not headings:
            return {
                'summary': "No content to summarize",
                'stats': self.total_usage_stats.copy()
            }
        
        # Reset usage stats for this document
        self.total_usage_stats = {
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_tokens': 0,
            'api_calls': 0
        }
        
        # Use improved cumulative summarization approach
        result = self._generate_cumulative_summary(headings)
        return {
            'summary': result,
            'stats': self.total_usage_stats.copy()
        }

    def _generate_cumulative_summary(self, headings: List[Dict[str, Any]]) -> str:
        """
        Generate summary by processing headings cumulatively with improved error handling.
        Each heading summary is combined with previous cumulative summary using a single 
        flexible prompt that handles both first heading and subsequent headings.
        
        Args:
            headings: List of document headings and their content
            
        Returns:
            str: Final cumulative summary
        """
        cumulative_summary = ""
        
        for i, heading in enumerate(headings):
            try:
                self.logger.info(f"Processing heading {i+1}/{len(headings)} for cumulative summary")
                
                # Get plain text of current heading
                current_heading_text = self._get_heading_text(heading)
                
                # Use unified prompt for both first and subsequent headings
                result = self._generate_summary_with_optional_previous(
                    cumulative_summary if i > 0 else None, 
                    current_heading_text, 
                    i + 1,
                    len(headings)
                )
                
                if result['success']:
                    cumulative_summary = result['summary']
                    self._update_usage_stats(result['usage'])
                    self.logger.info(f"Successfully processed heading {i+1}.")
                    self.logger.debug(f"Cumulative Summary {cumulative_summary}")
                    self.logger.debug(f"Successfully processed heading {i+1}. "
                                   f"Tokens used: {result['usage']['total_tokens'] if result['usage'] else 'N/A'}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self.logger.error(f"Failed to process heading {i+1}: {error_msg}")
                    raise Exception(f"Summarization failed for heading {i+1}: {error_msg}")
                        
            except Exception as e:
                self.logger.error(f"Critical error processing heading {i+1}: {str(e)}", exc_info=True)
                raise Exception(f"Critical error processing heading {i+1}: {str(e)}") from e
        
        if not cumulative_summary:
            self.logger.error("No summary was generated")
            raise Exception("No summary was generated - all processing failed")
            
        return cumulative_summary

    def _get_heading_text(self, heading: Dict[str, Any]) -> str:
        """Extract plain text from a single heading."""
        title = heading.get("title", "")
        content = heading.get("content", [])
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)
        return f"{title}\n{content}"

    def _generate_summary_with_optional_previous(self, previous_summary: Optional[str], 
                                                current_heading_text: str, 
                                                heading_number: int,
                                                total_headings: int) -> Dict[str, Any]:
        """
        Generate summary using a single unified prompt that handles both first heading
        and subsequent headings with optional previous summary.
        """
        
        system_prompt = get_summarizer_system_prompt(self.config.domain)

        user_prompt = get_summarizer_user_prompt(
            self.config.domain,
            str(heading_number),
            str(total_headings),
            previous_summary if previous_summary else "",
            current_heading_text
        )
        
        self.logger.debug(f"Summary passed: {previous_summary}")

        try:
            response = self.llm_client.generate_response_text_with_stats(system_prompt, user_prompt)
            
            if 'error' in response:
                return {
                    'success': False,
                    'error': f"LLM API error: {response['error']}",
                    'summary': None,
                    'usage': response.get('usage')
                }
                
            if not response.get('content') or response['content'].strip() == "":
                return {
                    'success': False,
                    'error': "Empty response from LLM",
                    'summary': None,
                    'usage': response.get('usage')
                }
                
            # Get the current section summary from LLM
            current_section_summary = response['content'].strip()
            self.logger.debug(f"Summary generated: {current_section_summary}")
            
            # Combine with previous summary if it exists
            if previous_summary:
                combined_summary = f"{previous_summary}\n\n{current_section_summary}"
            else:
                combined_summary = current_section_summary
                
            return {
                'success': True,
                'summary': combined_summary,
                'usage': response.get('usage'),
                'model': response.get('model'),
                'finish_reason': response.get('finish_reason')
            }
            
        except Exception as e:
            self.logger.error(f"Exception in summary generation: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Exception during LLM call: {str(e)}",
                'summary': None,
                'usage': None
            }


    def _update_usage_stats(self, usage: Optional[Dict[str, int]]) -> None:
        """Update cumulative usage statistics."""
        if usage:
            self.total_usage_stats['total_prompt_tokens'] += usage.get('prompt_tokens', 0)
            self.total_usage_stats['total_completion_tokens'] += usage.get('completion_tokens', 0)
            self.total_usage_stats['total_tokens'] += usage.get('total_tokens', 0)
            self.total_usage_stats['api_calls'] += 1

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return self.total_usage_stats.copy()