import logging
from ai_core.adaptive_rag.main import AdaptiveRAGPipelineWithState
from test_case_generator.test_case_generator import TestCaseGenerator
import json
import openai
from test_case_generator.utils import safe_json_parse

def retrieve_chunks(query, logger):
    """
    Retrieves relevant chunks using AdaptiveRAGPipelineWithState.

    Args:
        query (str): The query text for RAG.
        logger (logging.Logger): Logger instance for logging.

    Returns:
        list[str]: List of retrieved chunk texts.
    """
    try:
        pipeline = AdaptiveRAGPipelineWithState(query=query)
        chunks = pipeline.run()
        return [doc.page_content for doc in chunks if doc.page_content]
    except Exception as e:
        logger.error(f"Error retrieving chunks for query '{query}': {e}")
        return []


def generate_test_cases_for_flow(flow, business_context, platform, flow_index, total_flows, api_key, logger):
    """
    Generates test cases for a single flow.

    Args:
        flow (dict): Flow details.
        business_context (dict): Business context.
        platform (str): Platform for test cases.
        flow_index (int): Index of the flow in the list.
        total_flows (int): Total number of flows.
        api_key (str): OpenAI API key.
        logger (logging.Logger): Logger instance for logging.

    Returns:
        list[dict]: Generated test cases for the flow.
    """
    try:
        flow_title = flow.get("title", "")
        flow_description = flow.get("description", "")
        steps = flow.get("steps", [])

        query_text = f"""Title: {flow_title}. 
        Description: {flow_description}. 
        Steps:
        {chr(10).join([f"{i+1}. {step}" for i, step in enumerate(steps)])}
        Platform: {platform}
        Rules:{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(flow.get("rules_conditions",[]))])}
        Logic: {flow.get("logic","")}
        Error Exceptions:{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(flow.get("error_exceptions",[]))])}
        transitions: {flow.get("transitions","")}
        """

        logger.info(f"[{platform}_Flow {flow_index}/{total_flows}] Querying Adaptive RAG for Flow: {flow_title}")
        chunks = retrieve_chunks(query=query_text, logger=logger)

        context_knowledge = " ".join(chunks)

        generator = TestCaseGenerator(
            flow=flow,
            business_context=business_context,
            context_knowledge=context_knowledge,
            platform=platform,
            api_key=api_key,
            logger=logger
        )

        test_case_types = ["positive", "negative", "boundary", "error"]
        all_test_cases = []

        for test_case_type in test_case_types:
            logger.info(
                f"[Flow {flow_index}/{total_flows}] Generating test cases for type: {test_case_type}, "
                f"Platform: {platform}"
            )
            test_cases = generator.generate_test_cases_for_type(test_case_type)
            for test_case in test_cases:
                test_case["test_case_type"] = test_case_type
                test_case["flow_index"] = flow_index
            all_test_cases.extend(test_cases)

        return all_test_cases
    except Exception as e:
        logger.error(f"Error generating test cases for flow {flow_index}: {e}")
        return []


import json
import openai

def detect_duplicates_with_llm(test_cases, context, api_key, logger):
    """
    Detects duplicate test cases using an LLM-based approach.

    Args:
        test_cases (list[dict]): List of full test cases to analyze.
        context (str): Additional context or knowledge to consider.
        api_key (str): OpenAI API key.
        logger (logging.Logger): Logger instance for logging.

    Returns:
        list[str]: List of duplicate test case IDs in JSON list format.
    """
    try:
        # Construct the input for the LLM
        test_case_details = [
            f"ID: {test_case['test_case_id']}\nDetails: {json.dumps(test_case, indent=4)}"
            for test_case in test_cases
        ]
        input_text = (
            "The following are full test cases along with additional context. "
            "Identify duplicate test cases based on their steps and descriptions provided. "
            "Two test cases are considered duplicates if they test the same functionality/feature, \n\n"
            f"Context:\n{context}\n\nTest Cases:\n"
        )
        input_text += "\n\n".join(test_case_details)
        input_text += """\n\nReturn the output as a single JSON list containing only the IDs of duplicate test cases.

        Output:
        ```json
        {
        "duplicate_ids":[<all duplicate testcase ids>]

        }
        ```
        """

        # Call the LLM using OpenAI API
        logger.info("Sending test cases to LLM for duplicate detection.")
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert in test case analysis and semantic similarity detection."},
                {"role": "user", "content": input_text},
            ],
            max_tokens=15000,
            temperature=0.2,
        )

        # Extract duplicate IDs from the response
        duplicates_response = response.choices[0].message.content
        logger.info(f"LLM response for duplicate detection: {duplicates_response}")

        # Parse the JSON response to extract duplicate IDs
        try:
            duplicate_ids = safe_json_parse(duplicates_response)
            return duplicate_ids["duplicate_ids"]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return []
    except Exception as e:
        logger.error(f"Error detecting duplicates: {e}")
        return []