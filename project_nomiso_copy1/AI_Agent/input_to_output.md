# LLM Input/Output Context Analysis for AI_Agent Project

## 📊 Overview

This document provides a comprehensive analysis of the input context sent to LLM and the output context received from LLM for each file in the AI_Agent project. This helps understand the data flow and context management throughout the system.

## 🔄 System Architecture

The AI_Agent system follows a pipeline architecture where each component processes and enriches the context for the next stage:
```
User Story → User Story Analysis → Test Case Generation → Validation → Gap Analysis → Targeted Generation
```

## 📋 Detailed File Analysis

| **File** | **Function** | **LLM Input Context** | **LLM Output Context** | **Purpose** |
|----------|--------------|----------------------|------------------------|-------------|
| **user_story_analyser.py** | `analyse_user_story()` | • User story (raw text)<br>• System prompt: "You analyze user stories and explain what the user wants"<br>• Instructions: Identify intent, summarize goal, extract requirements | • Structured analysis text<br>• Key requirements list<br>• Main goal summary (2-3 sentences) | Analyze user story to understand intent and requirements |
| **test_case_generator/test_case.py** | `generate_test_cases()` | • User story (raw text)<br>• User story analysis (from analyser)<br>• Knowledge base (JSON from source code)<br>• Prompt template (from file)<br>• Instructions: Generate 6-8 test cases in JSON format | • JSON array of test cases<br>• Each test case: scenario, steps, expected, type, status<br>• 6-8 comprehensive test cases | Generate comprehensive test cases based on story + domain knowledge |
| **acceptance_criteria_checker.py** | `verify_test_cases_batch_with_llm()` | • All test cases (JSON array)<br>• Acceptance criteria (raw text)<br>• Instructions: Return boolean array for each test case<br>• System prompt: "You are a Software Testing Expert" | • JSON array of booleans<br>• [true, false, true, ...] matching test case order<br>• Boolean validation for each test case | Validate if each test case satisfies acceptance criteria |
| **acceptance_criteria_analyser.py** | `analyze_acceptance_criteria()` | • Acceptance criteria (raw text)<br>• Instructions: Extract criteria summary, requirements, expected outcome<br>• System prompt: "You are a software tester" | • JSON with:<br>• criteria_summary<br>• requirements array<br>• expected_outcome | Analyze acceptance criteria to extract structured insights |
| **knowledge_base/generate_knowledge_base.py** | `analyze_file_with_llm()` | • Python file content (raw code)<br>• File path<br>• Instructions: Extract business logic, functions, classes, dependencies<br>• System prompt: "You are a Software Architect and Business Analyst" | • JSON with:<br>• business_logic<br>• functions<br>• classes<br>• dependencies<br>• file_purpose | Analyze source code to build domain knowledge base |
| **knowledge_base/generate_knowledge_base.py** | `analyze_project_structure_with_llm()` | • All file analyses (JSON array)<br>• Instructions: Synthesize into comprehensive project knowledge<br>• System prompt: "You are a Software Architect and Business Analyst" | • Comprehensive JSON knowledge base<br>• Project overview<br>• Integrated business logic<br>• System architecture | Create comprehensive project knowledge base |
| **acceptance_criteria_refinement.py** | `analyze_gaps_with_llm()` | • Test cases (JSON array)<br>• Acceptance criteria (raw text)<br>• Validation results (satisfaction rate, satisfied/unsatisfied)<br>• Instructions: Identify missing criteria and gaps | • JSON with gap analysis:<br>• missing_criteria<br>• weak_coverage<br>• recommendations | Analyze gaps between test cases and acceptance criteria |
| **acceptance_criteria_refinement.py** | `generate_targeted_test_cases_with_llm()` | • Gap analysis (JSON from previous call)<br>• User story (raw text)<br>• Knowledge base (JSON)<br>• Instructions: Generate only missing test cases | • JSON array of new test cases<br>• Each targets specific missing criterion<br>• Focused on gaps identified | Generate targeted test cases to address identified gaps |

##  Data Flow Analysis

### Input Chain:
```
User Story → User Story Analysis → Test Case Generation → Validation → Gap Analysis → Targeted Generation
```

### Context Accumulation:
1. **User Story** (raw) → **Analysis** (structured)
2. **Analysis + Knowledge Base** → **Test Cases** (JSON array)
3. **Test Cases + Acceptance Criteria** → **Validation Results** (booleans)
4. **Validation Results + Test Cases** → **Gap Analysis** (missing criteria)
5. **Gap Analysis + Knowledge Base** → **Targeted Test Cases** (JSON array)

### Output Chain:
```
Structured Analysis → Test Cases → Validation Results → Gap Analysis → Refined Test Cases
```

## 📈 Context Size Growth

| **Stage** | **Input Size** | **Output Size** | **Context Type** |
|-----------|----------------|-----------------|------------------|
| User Story Analysis | ~100-500 chars | ~500-1000 chars | Text |
| Test Generation | ~2000-5000 chars | ~3000-8000 chars | JSON |
| Validation | ~3000-8000 chars | ~50-200 chars | Boolean Array |
| Gap Analysis | ~3000-8000 chars | ~1000-3000 chars | JSON |
| Targeted Generation | ~2000-5000 chars | ~1000-4000 chars | JSON |

## 🎯 Key Insights

### Context Management:
- **Stateless Design**: Each LLM call is independent with no memory between calls
- **Context Duplication**: User story, knowledge base, and acceptance criteria are sent in multiple calls
- **Growing Payloads**: Context size increases significantly through the pipeline

### Optimization Opportunities:
1. **Reduce Redundancy**: User story and knowledge base are sent repeatedly
2. **Context Compression**: Large test case arrays could be summarized
3. **Incremental Updates**: Only send changes instead of full context
4. **Conversation Context**: Maintain LLM conversation history for better continuity

### LLM Call Patterns:
- **Total LLM Calls**: 2-10 calls per complete workflow
- **Largest Payloads**: Test case generation and validation phases
- **Most Frequent**: Validation calls (one per test case in individual mode)

## 📊 Performance Metrics

### Typical Workflow:
- **Initial Generation**: 1-2 LLM calls
- **Validation**: 1 LLM call (batch) or N calls (individual)
- **Refinement Loop**: 2-6 additional LLM calls (if needed)
- **Total**: 4-10 LLM calls per complete workflow


## 🚀 Future Improvements

### Context Optimization:
1. **Smart Summarization**: Compress large contexts while preserving key information
2. **Incremental Context**: Only send changes between iterations
3. **Context Caching**: Cache and reuse common contexts
4. **Conversation Memory**: Maintain LLM conversation history


---

The file has been created with a comprehensive analysis of the LLM input/output context for each file in the AI_Agent project. This document will help you understand:

1. **What data is sent to each LLM call**
2. **What responses are expected from each LLM call**
3. **How context flows through the system**
4. **Performance and optimization opportunities**
5. **Technical challenges and solutions**
