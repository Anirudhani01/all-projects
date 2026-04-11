import os
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from models.story_state import StoryState
from services.rag_service import RAGService
from services.checker_service import CheckerService
from services.enhancer_service import EnhancerService
from utils.routing import RoutingLogic
from utils.cache_manager import cache_manager

class WorkflowManager:
    """
    Manages the story processing workflow using a state graph.

    This class is responsible for building and executing a graph-based workflow
    for retrieving context, reviewing, and enhancing stories. It coordinates the
    different services and manages the state of the story throughout the process.
    """
    def __init__(self, rag_service: RAGService, checker_service: CheckerService,
                 enhancer_service: EnhancerService, max_attempts: int,
                 output_dir: str, enable_graph_png: bool = False,
                 max_step_retries: int = 3, retry_backoff_seconds: int = 5):
        """
        Initializes the WorkflowManager.

        Args:
            rag_service (RAGService): An instance of the RAG service.
            checker_service (CheckerService): An instance of the checker service.
            enhancer_service (EnhancerService): An instance of the enhancer service.
            max_attempts (int): The maximum number of attempts for the enhancement loop.
            output_dir (str): The directory to save output files, such as the workflow graph.
            enable_graph_png (bool): If True, a PNG image of the workflow graph will be saved.
            max_step_retries (int): The maximum number of retries for each step in the workflow.
            retry_backoff_seconds (int): The number of seconds to wait between retries.
        """
        self.rag_service = rag_service
        self.checker_service = checker_service
        self.enhancer_service = enhancer_service
        self.max_attempts = max_attempts
        self.output_dir = output_dir
        self.enable_graph_png = enable_graph_png
        self.max_step_retries = max_step_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.logger = logging.getLogger(__name__)
        self.cache_manager = cache_manager
        self.graph_app = self._build_graph()
    
    def _save_state(self, state: StoryState):
        """
        Save the current state to the cache if a cache_key is present.

        This method checks if Redis caching is enabled and if a cache key exists in the
        current state. If so, it serializes and saves the state to Redis.

        Args:
            state (StoryState): The current state of the workflow to be cached.
        """
        if self.cache_manager.is_redis and state.get("cache_key"):
            self.cache_manager.set(state["cache_key"], state)
            self.logger.info("[CACHE] Saved state to cache with key: %s", state['cache_key'])
    
    def _retrieve_context(self, state: StoryState) -> StoryState:
        """
        Node for retrieving context using the RAG service.

        This node in the workflow graph uses the RAG service to fetch relevant context
        for the story based on its source path. The retrieved context is added to the state.

        Args:
            state (StoryState): The current state of the workflow.

        Returns:
            StoryState: The updated state with the retrieved RAG context.
        """
        source_path = state["story"]["metadata"]["source_path"]
        rag_context = self.rag_service.retrieve_context(source_path)
        new_state = {**state, "rag_chunks": rag_context}
        self._save_state(new_state)
        return new_state
    
    def _review_story(self, state: StoryState) -> StoryState:
        """
        Node for reviewing the story using the checker service.

        This node uses the checker service to review the current story. It considers
        RAG context, previous feedback, and the number of attempts to generate new feedback.

        Args:
            state (StoryState): The current state of the workflow.

        Returns:
            StoryState: The updated state with the checker's feedback.
        """
        story = state["story"]
        rag_chunks = state.get("rag_chunks", "")
        previous_feedback = state.get("checker_response")
        attempts = state.get("attempts", 0)
        
        feedback = self.checker_service.review_story(
            story, rag_chunks, previous_feedback, attempts
        )
        
        new_state = {**state, "checker_response": feedback}
        self._save_state(new_state)
        return new_state
    
    def _enhance_story(self, state: StoryState) -> StoryState:
        """
        Node for enhancing the story using the enhancer service.

        This node uses the enhancer service to improve the story based on the feedback
        from the checker. It updates the story and increments the attempt counter.

        Args:
            state (StoryState): The current state of the workflow.

        Returns:
            StoryState: The updated state with the enhanced story.
        """
        story = state["story"]
        checker_response = state.get("checker_response", {})
        rag_chunks = state.get("rag_chunks", "")
        
        enhanced_story = self.enhancer_service.enhance_story(
            story, checker_response, rag_chunks
        )
        
        if enhanced_story:
            new_state = {
                **state,
                "story": enhanced_story,
                "attempts": state.get("attempts", 0) + 1
            }
        else:
            new_state = {**state, "attempts": state.get("attempts", 0) + 1}

        self._save_state(new_state)
        return new_state
    
    def _finalize(self, state: StoryState) -> StoryState:
        """
        Node for finalizing the workflow.

        This node represents the end of the workflow. It saves the final state
        before the process concludes.

        Args:
            state (StoryState): The final state of the workflow.

        Returns:
            StoryState: The final state, unchanged.
        """
        self._save_state(state)
        return state
    
    def _routing_logic(self, state: StoryState) -> str:
        """
        Determines the next step in the workflow based on the current state.

        This method implements the conditional logic for the graph's edges. It decides
        whether to continue with another enhancement attempt or to finalize the process.

        Args:
            state (StoryState): The current state of the workflow.

        Returns:
            str: A string indicating the next node to transition to ('regenerate' or 'finalize').
        """
        return RoutingLogic.should_continue(state, self.max_attempts)
    
    def _build_graph(self):
        """
        Build and compile the workflow graph using StateGraph.

        This method defines the structure of the story processing workflow by adding nodes
        for each step (retrieve context, review, enhance, finalize) and setting up the
        edges and conditional routing logic between them.

        Returns:
            CompiledGraph: The compiled workflow graph application.
        """
        workflow = StateGraph(StoryState)

        # Add nodes
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("review", self._review_story)
        workflow.add_node("enhance", self._enhance_story)
        workflow.add_node("finalize", self._finalize)

        # Set entry point and edges
        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "review")
        workflow.add_edge("enhance", "review")
        workflow.add_conditional_edges("review", self._routing_logic, {
            "regenerate": "enhance",
            "finalize": "finalize"
        })
        workflow.add_edge("finalize", END)

        graph_app = workflow.compile()

        # Save graph PNG only if enabled
        if self.enable_graph_png:
            try:
                png_path = os.path.join(self.output_dir, "workflow_graph.png")
                image_bytes = graph_app.get_graph().draw_mermaid_png()
                with open(png_path, "wb") as f:
                    f.write(image_bytes)
                self.logger.info(f"Workflow graph saved to {png_path}")
            except Exception as e:
                self.logger.warning(f"Could not save workflow graph: {e}")

        return graph_app

    def execute(self, initial_state: StoryState) -> StoryState:
        """
        Executes the workflow graph for a given initial state.

        This method invokes the compiled graph with an initial story state and manages
        the execution loop, respecting the maximum number of attempts.

        Args:
            initial_state (StoryState): The starting state for the workflow execution.

        Returns:
            StoryState: The final state of the story after the workflow has completed.

        Raises:
            Exception: Propagates any exceptions that occur during graph execution.
        """
        state = initial_state

        try:
            for attempt in range(self.max_attempts):
                self.logger.info("[WORKFLOW] Attempt %s of %s", attempt + 1, self.max_attempts)
                state["attempts"] = attempt

                # Run the graph with retry on transient failures
                retry = 0
                while True:
                    try:
                        state = self.graph_app.invoke(state)
                        break  # success
                    except Exception:
                        retry += 1
                        self.logger.exception("[WORKFLOW] Error during graph execution (attempt %s, retry %s)", attempt + 1, retry)
                        if retry >= self.max_step_retries:
                            self.logger.error("[WORKFLOW] Exceeded max retries (%s) for attempt %s", self.max_step_retries, attempt + 1)
                            raise
                        self.logger.info("[WORKFLOW] Retrying in %s seconds...", self.retry_backoff_seconds)
                        import time
                        time.sleep(self.retry_backoff_seconds)

                # Decide if the loop should stop
                route = RoutingLogic.should_continue(state, self.max_attempts)
                self.logger.info("[WORKFLOW] Routing decision after attempt %s: %s", attempt + 1, route)

                if route == "finalize":
                    self.logger.info("[WORKFLOW] Finalization condition met.")
                    break
                else:
                    self.logger.info("[WORKFLOW] Regenerating story...")

            return state

        except Exception as e:
            self.logger.exception("[WORKFLOW] Workflow aborted due to unrecoverable error.")
            raise

