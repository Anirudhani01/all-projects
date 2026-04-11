# Story Processor

This project implements an automated pipeline for parsing, reviewing, enhancing, and publishing JIRA user stories for telecom products using LLMs, LangGraph, and RAG (Retrieval-Augmented Generation). It processes `.docx` files containing telecom user stories and iteratively improves them until they meet quality criteria.

---

## Features

- Pluggable **Parser layer** – choose `DOCX` or `JIRA` (or add your own)
- Parses telecom user stories from `.docx` files or directly from JIRA issues
- Retrieves contextual information using a custom RAG component
- Uses OpenAI GPT models to review and enhance stories
- Iteratively improves stories based on prior LLM feedback
- Generates structured JSON and formatted DOCX output
- Automatic step-level retry for transient errors (configurable)
- Optional DOCX generation and/or JIRA issue creation – both can be toggled via config
- Produces a visual workflow diagram (LangGraph)

---

## Directory Structure

```
story_processor/
├── __init__.py
├── main.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── core/
│   ├── __init__.py
│   ├── llm_client.py
│   ├── story_processor.py
│   └── workflow_manager.py
├── models/
│   ├── __init__.py
│   └── story_state.py
├── services/
│   ├── __init__.py
│   ├── rag_service.py
│   ├── checker_service.py
│   ├── enhancer_service.py
│   └── file_service.py
├── utils/
│   ├── __init__.py
│   └── routing.py
├── external/
│   ├── __init__.py
│   ├── parser.py
│   ├── prompt.py
│   └── writer.py
└── tests/
    ├── __init__.py
    └── test_story_processor.py

# Root-level files
AdaptiveRag.py
main.py
parser.py
prompt.py
writer.py
requirements.txt
readme.md
```

---

## How It Works

1. **Parsing:**  
   DOCX files are parsed into structured JSON using the `external/parser.py` module.

2. **Context Retrieval (RAG):**  
   The system invokes `AdaptiveRag.py` to fetch relevant domain knowledge using plain text extracted from the input file.

3. **LLM Review & Enhancement:**  
   - The story is reviewed by an OpenAI GPT model using prompt templates.
   - Feedback is provided and the story is enhanced iteratively, incorporating RAG context and previous feedback.

4. **Workflow Management:**  
   - The process is orchestrated as a directed acyclic graph (DAG) using LangGraph.
   - The workflow:  
     `retrieve_context → review → enhance → review → ... → finalize`

5. **Output Generation:**  
   - For each processed `.docx` story, the pipeline generates:
     - Enhanced `.docx`
     - Enhanced `.json`
     - Workflow visualization (`workflow_graph.png`)
     - Optional: JIRA upload

---

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# OpenAI and Model
OPENAI_API_KEY=your_openai_api_key
CHECKER_ENHENCER_MODEL=gpt-4
# Workflow loop limits
MAX_ATTEMPTS=3                 # max enhance iterations per story
MAX_STEP_RETRIES=3             # retries for a single workflow step when an exception occurs
RETRY_BACKOFF_SECONDS=5        # wait time between step retries

# Input/Output Directories
INPUT_DIR=input
OUTPUT_DIR=output

# Redis Caching (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Pipeline Behaviour & Parser Selection

# Core behaviour flags
PARSER_TYPE=DOCX              # DOCX (default) or JIRA – decides where stories are pulled from
ENABLE_DOCX_OUTPUT=true       # When false, no enhanced .docx is written
ENABLE_JIRA_OUTPUT=false      # When true, story is uploaded to Jira (if credentials below present)

# JIRA Integration (needed only when PARSER_TYPE=JIRA or ENABLE_JIRA_OUTPUT=true)
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=YOURPROJECT
ACCEPTANCE_CRITERIA_FIELD_ID=customfield_12345  # custom field for acceptance criteria ADF
# If PARSER_TYPE=JIRA – list issues to process (comma-separated)
JIRA_ISSUES=PROJ-1,PROJ-42
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/story-enhancer.git
cd story-enhancer

# Create a virtual environment
python -m venv .venv
# On Unix/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note on `pygraphviz`**: The dependency `pygraphviz`, used for drawing the workflow graph, was removed from `requirements.txt` as it can cause installation issues on systems without the Graphviz library. If you wish to generate the `workflow_graph.png`, you will need to install Graphviz manually and then `pip install pygraphviz`. Otherwise, the graph generation will be skipped.

---

## Usage

If `PARSER_TYPE=DOCX`

1. Place your `.docx` files in the `input/` directory.

If `PARSER_TYPE=JIRA`

1. Ensure `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` are set and `JIRA_ISSUES` lists the keys to process.

2. Run the main pipeline:

   ```bash
   python main.py
   ```

3. Output files will be available in the `output/` folder:
   - `enhanced_<name>.json`   (always)
   - `enhanced_<name>.docx`   (only when `ENABLE_DOCX_OUTPUT=true`)
   - Story uploaded to JIRA    (only when `ENABLE_JIRA_OUTPUT=true` **and** credentials are present)
   - `workflow_graph.png`     (if `pygraphviz` is installed and `ENABLE_GRAPH_PNG=true`)

Behaviour edge-cases:

* If **both** `ENABLE_DOCX_OUTPUT` and `ENABLE_JIRA_OUTPUT` are `false`, the pipeline still runs and saves the JSON – it just skips DOCX creation and Jira upload.
* If `ENABLE_JIRA_OUTPUT=true` but credentials are missing, the pipeline logs a warning and continues without crashing.

---

## Prompt Templates

All prompt templates are defined in `external/prompt.py`, including:
- `checker_system_prompt1` and `checker_user_prompt1` for initial reviews
- `checker_system_prompt` and `checker_user_prompt` for iterative reviews
- `enhancer_system_prompt` and `enhancer_user_prompt` for story improvements

Each prompt is designed to guide the LLM in reviewing or enhancing stories using RAG context and prior feedback.

---

## Rating and Iteration Logic

- Each field is rated as: `Very Low`, `Low`, `Medium`, `Good`, or `Excellent`.
- The workflow continues enhancing until:
  - All fields are rated `Good` or `Excellent`, or
  - Maximum attempts (`MAX_ATTEMPTS`) is reached.

---

## Output

For every input `.docx`, the system produces:
- A cleaned and improved `.docx`
- A structured `.json` of the story
- A PNG of the LangGraph workflow
- Optional: uploads the story to JIRA

Example:

```
input/
└── user_story_1.docx

output/
├── enhanced_user_story_1.docx
├── enhanced_user_story_1.json
└── workflow_graph.png
```

---

## JIRA Integration

The `create_jira_story()` function in `external/writer.py` is used to create issues in JIRA. Configuration should be handled securely, and the function gracefully handles failure without stopping the workflow.

---

## Caching

This application supports Redis-based caching to allow for resumable processing. If a workflow is interrupted, it can be resumed from the last completed step on the next run, saving time and resources.

- **How it works:** The state of each story processing workflow is saved to Redis after each major step (e.g., after context retrieval, review, or enhancement). When the application starts, it checks for a cached state using the document's filename as a key. If a state is found, the process resumes from there.
- **Fallback:** If Redis is not configured (i.e., `REDIS_HOST` is not set), the application falls back to a temporary in-memory store, and the resumable feature is effectively disabled as the state is lost when the application exits.
- **Configuration:** To enable Redis, add the `REDIS_HOST`, `REDIS_PORT`, and `REDIS_PASSWORD` (if needed) variables to your `.env` file.
- **Cache Cleanup:** Upon successful completion of a document's workflow, its corresponding cache entry is automatically deleted from Redis to save space.

### Running Redis Locally

The easiest way to run Redis locally for development across all platforms is by using Docker.

**Using Docker (All Platforms)**

1.  **Install Docker Desktop:** Download and install it from the [official Docker website](https://www.docker.com/products/docker-desktop/).
2.  **Run Redis Container:** Open your terminal and run the following command to start a Redis container.

    ```bash
    docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
    ```
    This will run a Redis instance on the default port `6379`.

**Platform-Specific Instructions**

If you prefer not to use Docker, you can use the following platform-specific instructions:

**On macOS (using Homebrew)**

1.  **Install Homebrew:** If you don't have it, follow the instructions on [brew.sh](https://brew.sh/).
2.  **Install Redis:**
    ```bash
    brew install redis
    ```
3.  **Start Redis:**
    ```bash
    brew services start redis
    ```

**On Linux (using APT for Debian/Ubuntu)**

1.  **Update and Install Redis:**
    ```bash
    sudo apt-get update
    sudo apt-get install redis-server
    ```
2.  **Start Redis Service:**
    ```bash
    sudo systemctl enable --now redis-server
    ```

**On Windows (using WSL)**

Redis is not officially supported on Windows, but it can be run seamlessly using the Windows Subsystem for Linux (WSL).

1.  **Install WSL:** Follow the official Microsoft guide to [install WSL](https://docs.microsoft.com/en-us/windows/wsl/install).
2.  **Install a Linux distribution:** Install a distribution like Ubuntu from the Microsoft Store.
3.  **Install and run Redis:** Open your Linux terminal and follow the Linux instructions above.

---

## Logging

Logs are configured using `logging.basicConfig()` and include timestamps, log levels, and messages for all major actions such as parsing, LLM calls, enhancement, and JIRA uploads.

---

## Development Notes

- The processing state is tracked using the `StoryState` TypedDict.
- LangGraph manages the workflow transitions.
- LLM responses are expected to be in JSON format and are parsed with error handling.
- Retry mechanism ensures robustness for enhancement cycles.
- `workflow_graph.png` provides a visual overview of the pipeline.
