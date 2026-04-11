            +---------------------+
            |  User Input Layer   |
            |---------------------|
            | - User Story        |
            | - Acceptance Criteria|
            +----------+----------+
                       |
                       v
            +---------------------------+
            | Acceptance Criteria       |
            | Analyzer Layer            |
            |---------------------------|
            | - Input: Acceptance Criteria|
            | - Process: LLM Analysis    |
            | - Output: Structured Criteria|
            +----------+----------------+
                       |
                       v
            +---------------------+
            |  User Story Analyzer|
            |---------------------|
            | - Input: User Story |
            | - Process: LLM      |
            | - Output: Structured|
            |   Story Analysis    |
            +----------+----------+
                       |
                       v
            +---------------------+
            | Knowledge Base Layer|
            |---------------------|
            | - Input: Source Code|
            | - Process: Analyze  |
            | - Output: KB JSON   |
            +----------+----------+
                       |
                       v
            +---------------------+
            | Test Case Generator |
            |---------------------|
            | - Input: Story Anal |
            |   + Knowledge Base  |
            |   + Prompt Template |
            | - Process: LLM      |
            | - Output: Test Cases|
            +----------+----------+
                       |
                       v
            +-------------------------------+
            | Acceptance Criteria Checker   |
            |-------------------------------|
            | - Input: Test Cases + Structured|
            |   Acceptance Criteria          |
            | - Process: Strategy / LLM      |
            | - Output: Annotated Test Cases |
            |   (satisfies_criteria: True/False)|
            +-------------------------------+
                       |
                       v
            +---------------------+
            |  Final Output       |
            |---------------------|
            | - Markdown / JSON   |
            | - Summary Report    |
            +---------------------+
