# Nomiso IntelliQ - System Architecture Document

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [High-Level Architecture](#high-level-architecture)
4. [Component Architecture](#component-architecture)
5. [Data Flow Architecture](#data-flow-architecture)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)
8. [Security Architecture](#security-architecture)
9. [Performance & Scalability](#performance--scalability)
10. [Domain Knowledge Documentation](#domain-knowledge-documentation)
11. [API Documentation](#api-documentation)
12. [Configuration Management](#configuration-management)

## System Overview

Nomiso IntelliQ is an intelligent test case generation and story enhancement platform that leverages AI/ML capabilities to automate the process of creating, validating, and enhancing user stories and test cases. The system integrates multiple AI services, RAG (Retrieval-Augmented Generation) capabilities, and domain-specific knowledge to deliver high-quality, testable user stories and comprehensive test cases.

### Key Capabilities
- **Story Enhancement**: AI-powered enhancement of user stories with domain-specific context
- **Test Case Generation**: Automated generation of comprehensive test cases from enhanced stories
- **Validation & Quality Assurance**: Multi-iteration validation pipeline with accuracy measurement
- **RAG Integration**: Context-aware retrieval from knowledge bases
- **Multi-format Support**: DOCX, JIRA, and plain text parsing capabilities
- **Image Parsing**: UI structure extraction from screenshots for test case generation

## Architecture Principles

1. **Modular Design**: Loosely coupled, highly cohesive components
2. **Service-Oriented Architecture**: Clear separation of concerns with dedicated services
3. **AI-First Approach**: LLM integration at multiple layers for intelligent processing
4. **Extensibility**: Plugin-based architecture for new parsers and output formats
5. **Fault Tolerance**: Retry mechanisms and graceful degradation
6. **Observability**: Comprehensive logging and monitoring throughout the system

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Nomiso IntelliQ Platform                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │
│  │   Input Layer   │    │  Processing     │    │     Output Layer        │ │
│  │                 │    │    Pipeline     │    │                         │ │
│  │ • DOCX Parser  │───▶│ • Story         │───▶│ • Enhanced Stories     │ │
│  │ • JIRA Parser  │    │   Processor     │    │ • Test Cases           │ │
│  │ • Image Parser │    │ • Workflow      │    │ • Validation Reports   │ │
│  │ • Plain Text   │    │   Manager       │    │ • DOCX Output         │ │
│  └─────────────────┘    │ • RAG Service   │    │ • JIRA Integration    │ │
│                          └─────────────────┘    └─────────────────────────┘ │
│                                   │                                          │
│                          ┌─────────────────┐                                │
│                          │   AI Services   │                                │
│                          │                 │                                │
│                          │ • LLM Client    │                                │
│                          │ • Enhancer      │                                │
│                          │ • Validator     │                                │
│                          │ • Test Generator│                                │
│                          └─────────────────┘                                │
│                                   │                                          │
│                          ┌─────────────────┐                                │
│                          │  Knowledge      │                                │
│                          │   Base          │                                │
│                          │                 │                                │
│                          │ • RAG Pipeline  │                                │
│                          │ • Domain        │                                │
│                          │   Context       │                                │
│                          │ • Templates     │                                │
│                          └─────────────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Input Layer"
        A1[DOCX Parser]
        A2[JIRA Parser]
        A3[Image Parser]
        A4[Plain Text Parser]
    end
    
    subgraph "Processing Pipeline"
        B1[Story Processor]
        B2[Workflow Manager]
        B3[RAG Service]
        B4[File Service]
    end
    
    subgraph "AI Services"
        C1[LLM Client]
        C2[Enhancer Service]
        C3[Checker Service]
        C4[Summarizer Service]
        C5[Validator Service]
        C6[Test Case Generator]
    end
    
    subgraph "Knowledge Base"
        D1[Vector Database]
        D2[Adaptive RAG Pipeline]
        D3[Domain Context]
        D4[Template Library]
    end
    
    subgraph "Output Layer"
        E1[Enhanced Stories]
        E2[Test Cases]
        E3[Validation Reports]
        E4[DOCX Output]
        E5[JIRA Integration]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    
    B1 --> B2
    B1 --> B3
    B1 --> B4
    
    B2 --> C2
    B2 --> C3
    B2 --> C4
    
    B3 --> D2
    D2 --> D1
    D2 --> D3
    D2 --> D4
    
    C1 --> C2
    C1 --> C3
    C1 --> C4
    C1 --> C5
    C1 --> C6
    
    C2 --> E1
    C3 --> E1
    C4 --> E1
    
    E1 --> C6
    C6 --> E2
    
    C5 --> E3
    E2 --> E3
    
    E1 --> E4
    E2 --> E4
    E1 --> E5
```

## Component Architecture

### Core Components

#### 1. Story Processor (`components/common/story_processor.py`)
- **Purpose**: Central orchestrator for the entire story processing pipeline
- **Responsibilities**:
  - Coordinate all services and workflows
  - Manage document processing lifecycle
  - Handle parallel processing and error recovery
  - Integrate test case generation and validation

#### 2. Workflow Manager (`components/common/workflow_manager.py`)
- **Purpose**: Manages the state-based workflow using LangGraph
- **Responsibilities**:
  - Build and execute workflow graphs
  - Manage state transitions between workflow steps
  - Handle retry logic and error recovery
  - Coordinate RAG, checker, and enhancer services

#### 3. LLM Client (`components/common/llm_client.py`)
- **Purpose**: Centralized interface for OpenAI API interactions
- **Responsibilities**:
  - Handle authentication and API calls
  - Manage model selection and configuration
  - Provide consistent response formatting
  - Handle rate limiting and error recovery

#### 4. RAG Service (`components/common/rag_service.py`)
- **Purpose**: Retrieval-Augmented Generation for context-aware processing
- **Responsibilities**:
  - Extract text from source documents
  - Query knowledge base for relevant context
  - Integrate with AdaptiveRAG pipeline
  - Provide domain-specific context for enhancement

### Enhancement Components

#### 1. Enhancer Service (`components/story_enhancer/enhancer_service.py`)
- **Purpose**: AI-powered story enhancement based on feedback
- **Responsibilities**:
  - Process checker feedback
  - Generate enhanced story content
  - Apply domain-specific improvements
  - Maintain story structure and consistency

#### 2. Checker Service (`components/story_enhancer/checker_service.py`)
- **Purpose**: Quality assessment and feedback generation
- **Responsibilities**:
  - Evaluate story quality and completeness
  - Provide structured feedback for each field
  - Assess domain-specific requirements
  - Generate improvement recommendations

#### 3. Summarizer Service (`components/story_enhancer/summarizer_service.py`)
- **Purpose**: Generate concise summaries of enhanced stories
- **Responsibilities**:
  - Create executive summaries
  - Highlight key changes and improvements
  - Maintain traceability to original content

### Test Case Generation Components

#### 1. Test Case Pipeline (`components/test_case_generator/pipeline.py`)
- **Purpose**: Orchestrate test case generation workflow
- **Responsibilities**:
  - Load and parse input documents
  - Coordinate parallel test case generation
  - Manage business context integration
  - Handle duplicate detection and resolution

#### 2. Test Case Generator (`components/test_case_generator/test_case_generator.py`)
- **Purpose**: Core logic for test case creation
- **Responsibilities**:
  - Generate test scenarios from user stories
  - Apply testing best practices
  - Ensure coverage of acceptance criteria
  - Generate platform-specific test cases

### Validation Components

#### 1. Validator Service (`components/story_validator/validator_service.py`)
- **Purpose**: Validate generated test cases against stories
- **Responsibilities**:
  - Assess test case quality and relevance
  - Validate coverage of story requirements
  - Generate validation reports
  - Identify gaps and inconsistencies

#### 2. Accuracy Measure Service (`components/story_validator/accuracy_measure_service.py`)
- **Purpose**: Measure and report test case accuracy
- **Responsibilities**:
  - Calculate accuracy metrics
  - Generate performance reports
  - Track improvement over iterations
  - Provide actionable insights

#### 3. Failed Test Cases Regeneration Service (`components/story_validator/failed_testcases_regeneration_service.py`)
- **Purpose**: Regenerate failed test cases with improvements
- **Responsibilities**:
  - Analyze validation failures
  - Generate improved test cases
  - Maintain consistency with original requirements
  - Track regeneration success rates

### Parser Components

#### 1. DOCX Parser (`components/parser/parser.py`)
- **Purpose**: Extract content from Microsoft Word documents
- **Responsibilities**:
  - Parse DOCX file structure
  - Extract text and formatting
  - Handle complex document layouts
  - Preserve document hierarchy

#### 2. JIRA Parser (`components/parser/jira_parser.py`)
- **Purpose**: Extract user stories from JIRA
- **Responsibilities**:
  - Connect to JIRA API
  - Extract story metadata and content
  - Handle JIRA-specific formatting
  - Support bulk story processing

#### 3. Image Parser (`components/image_parser/`)
- **Purpose**: Extract UI structure from screenshots
- **Responsibilities**:
  - Analyze image layouts
  - Detect UI components
  - Generate structured representations
  - Support test case generation for UI flows

### Adaptive RAG Components

#### 1. Adaptive RAG Pipeline (`components/adaptive_rag/main.py`)
- **Purpose**: Intelligent document retrieval and context generation
- **Responsibilities**:
  - Query vector database
  - Retrieve relevant document chunks
  - Adapt retrieval based on user type
  - Provide context for story enhancement

#### 2. Retriever Node (`components/adaptive_rag/retriever.py`)
- **Purpose**: Core retrieval logic for RAG operations
- **Responsibilities**:
  - Execute vector similarity search
  - Filter results by relevance
  - Handle metadata-based filtering
  - Optimize retrieval parameters

### Component Interaction Diagram

```mermaid
graph LR
    subgraph "Input Processing"
        IP[Input Parser]
        SP[Story Processor]
        FS[File Service]
    end
    
    subgraph "Core Services"
        WM[Workflow Manager]
        RS[RAG Service]
        LS[LLM Service]
    end
    
    subgraph "Enhancement Pipeline"
        CS[Checker Service]
        ES[Enhancer Service]
        SS[Summarizer Service]
    end
    
    subgraph "Test Generation"
        TCP[Test Case Pipeline]
        TCG[Test Case Generator]
        VS[Validator Service]
        AMS[Accuracy Measure Service]
        FTRS[Failed Test Cases Regeneration Service]
    end
    
    subgraph "Output Generation"
        TDGS[Test Case DOCX Generator Service]
        OS[Output Service]
    end
    
    IP --> SP
    SP --> FS
    SP --> WM
    WM --> RS
    WM --> LS
    
    WM --> CS
    CS --> ES
    ES --> SS
    
    SS --> TCP
    TCP --> TCG
    TCG --> VS
    VS --> AMS
    VS --> FTRS
    FTRS --> VS
    
    TCG --> TDGS
    TDGS --> OS
```

## Data Flow Architecture

### Primary Story Processing Flow

```mermaid
graph TD
    A[Input Document] --> B[Parser Selection]
    B --> C{DOCX or JIRA?}
    C -->|DOCX| D[DOCX Parser]
    C -->|JIRA| E[JIRA Parser]
    D --> F[Text Extraction]
    E --> F
    F --> G[RAG Service]
    G --> H[Knowledge Base Query]
    H --> I[Context Retrieval]
    I --> J[Story Processor]
    J --> K[Workflow Manager]
    K --> L[Checker Service]
    L --> M[Quality Assessment]
    M --> N{Quality Acceptable?}
    N -->|No| O[Enhancer Service]
    N -->|Yes| P[Story Enhancement Complete]
    O --> Q[Enhanced Story]
    Q --> R[Re-evaluation]
    R --> M
    P --> S[Test Case Generation]
    S --> T[Validation Pipeline]
    T --> U[Final Output]
```

### Test Case Generation Flow

```mermaid
graph TD
    A[Enhanced Story] --> B[Test Case Pipeline]
    B --> C[Load Flows & Context]
    C --> D[Parallel Processing]
    D --> E[Generate Test Cases]
    E --> F[Duplicate Detection]
    F --> G[Test Case Validation]
    G --> H{Validation Passed?}
    H -->|No| I[Failed Test Cases]
    H -->|Yes| J[Test Cases Complete]
    I --> K[Regeneration Service]
    K --> L[Improved Test Cases]
    L --> G
    J --> M[DOCX Generation]
    M --> N[Final Output]
```

### RAG Context Retrieval Flow

```mermaid
graph TD
    A[Story Text] --> B[RAG Service]
    B --> C[Adaptive RAG Pipeline]
    C --> D[Query Processing]
    D --> E[Vector Database Search]
    E --> F[Chunk Retrieval]
    F --> G[Relevance Scoring]
    G --> H[Context Assembly]
    H --> I[Domain Context Integration]
    I --> J[Enhanced Context]
    J --> K[Story Enhancement]
```

### Detailed Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> Initialized
    Initialized --> Parsing
    Parsing --> RAGRetrieval
    RAGRetrieval --> QualityCheck
    QualityCheck --> Enhancement
    Enhancement --> ReEvaluation
    ReEvaluation --> QualityCheck
    QualityCheck --> TestCaseGeneration
    TestCaseGeneration --> Validation
    Validation --> Regeneration
    Regeneration --> Validation
    Validation --> FinalOutput
    FinalOutput --> [*]
    
    Enhancement --> Error
    RAGRetrieval --> Error
    TestCaseGeneration --> Error
    Error --> [*]
```

### Service Dependency Graph

```mermaid
graph TD
    subgraph "External Dependencies"
        OA[OpenAI API]
        JA[JIRA API]
        VD[Vector Database]
        RD[Redis Cache]
    end
    
    subgraph "Core Services"
        SP[Story Processor]
        WM[Workflow Manager]
        LC[LLM Client]
        RS[RAG Service]
    end
    
    subgraph "Enhancement Services"
        CS[Checker Service]
        ES[Enhancer Service]
        SS[Summarizer Service]
    end
    
    subgraph "Test Generation Services"
        TCP[Test Case Pipeline]
        TCG[Test Case Generator]
        VS[Validator Service]
        AMS[Accuracy Measure Service]
        FTRS[Failed Test Cases Regeneration Service]
    end
    
    subgraph "Output Services"
        TDGS[Test Case DOCX Generator Service]
        FS[File Service]
    end
    
    OA --> LC
    JA --> SP
    VD --> RS
    RD --> SP
    
    SP --> WM
    SP --> RS
    WM --> LC
    WM --> CS
    WM --> ES
    
    LC --> CS
    LC --> ES
    LC --> SS
    LC --> TCG
    LC --> VS
    LC --> AMS
    LC --> FTRS
    
    RS --> CS
    RS --> ES
    RS --> VS
    
    CS --> ES
    ES --> SS
    SS --> TCP
    TCP --> TCG
    TCG --> VS
    VS --> AMS
    VS --> FTRS
    FTRS --> VS
    
    TCG --> TDGS
    TDGS --> FS
```

## Technology Stack

### Backend Technologies
- **Python 3.8+**: Core application language
- **Flask**: Web framework for API endpoints
- **LangGraph**: Workflow orchestration and state management
- **OpenAI API**: LLM integration for AI-powered processing
- **PostgreSQL + pgvector**: Vector database for RAG operations
- **Redis**: Caching and session management

### AI/ML Technologies
- **OpenAI GPT Models**: Text generation and analysis
- **Vector Embeddings**: Semantic search and retrieval
- **RAG Pipeline**: Context-aware generation
- **Prompt Engineering**: Structured AI interactions

### Data Processing
- **python-docx**: DOCX document parsing
- **JIRA API**: Issue tracking integration
- **Pillow/OpenCV**: Image processing and analysis
- **JSON**: Data serialization and storage

### Infrastructure
- **Docker**: Containerization
- **WSL2**: Windows Subsystem for Linux compatibility
- **File System**: Local storage for documents and outputs
- **Logging**: Centralized logging with rotation

### Technology Stack Diagram

```mermaid
graph TB
    subgraph "Frontend/API Layer"
        F1[Flask Web Framework]
        F2[REST API Endpoints]
        F3[WebSocket Support]
    end
    
    subgraph "Application Layer"
        A1[Python 3.8+]
        A2[LangGraph Workflow]
        A3[Service Orchestration]
    end
    
    subgraph "AI/ML Layer"
        M1[OpenAI GPT Models]
        M2[Vector Embeddings]
        M3[RAG Pipeline]
        M4[Prompt Engineering]
    end
    
    subgraph "Data Layer"
        D1[PostgreSQL + pgvector]
        D2[Redis Cache]
        D3[File System]
        D4[Vector Database]
    end
    
    subgraph "External APIs"
        E1[OpenAI API]
        E2[JIRA API]
        E3[Image Processing APIs]
    end
    
    subgraph "Infrastructure"
        I1[Docker Containers]
        I2[WSL2 Environment]
        I3[Logging & Monitoring]
    end
    
    F1 --> A1
    F2 --> A2
    A2 --> M1
    A2 --> M2
    A2 --> M3
    
    M1 --> E1
    M2 --> D4
    M3 --> D1
    
    A3 --> D2
    A3 --> D3
    
    F3 --> A3
    A3 --> I1
    A3 --> I2
    A3 --> I3
```

## Deployment Architecture

### Development Environment
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Development Environment                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │
│  │   Local IDE     │    │   WSL2 Ubuntu   │    │    File System          │ │
│  │                 │    │                 │    │                         │
│  │ • VS Code       │◄──▶│ • Python 3.8+  │◄──▶│ • Input Documents      │ │
│  │ • Python        │    │ • Dependencies  │    │ • Output Files         │ │
│  │ • Git           │    │ • Services      │    │ • Logs                 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │
│                                   │                                          │
│                          ┌─────────────────┐                                │
│                          │   External      │                                │ │
│                          │   Services      │                                │ │
│                          │                 │                                │ │
│                          │ • OpenAI API    │                                │ │
│                          │ • JIRA API      │                                │ │
│                          │ • Vector DB     │                                │ │
│                          └─────────────────┘                                │ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Production Deployment
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Production Environment                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐ │
│  │   Load          │    │   Application   │    │    Data Layer           │ │
│  │   Balancer      │    │   Servers       │    │                         │ │
│  │                 │    │                 │    │                         │ │
│  │ • Nginx         │───▶│ • Docker        │───▶│ • PostgreSQL           │ │
│  │ • SSL/TLS       │    │   Containers    │    │ • Redis                │ │
│  │ • Health Checks │    │ • Auto-scaling  │    │ • File Storage         │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────────────┘ │
│                                   │                                          │
│                          ┌─────────────────┐                                │
│                          │   Monitoring    │                                │ │
│                          │   & Logging     │                                │ │
│                          │                 │                                │ │
│                          │ • Prometheus    │                                │ │
│                          │ • Grafana       │                                │ │
│                          │ • ELK Stack     │                                │ │
│                          └─────────────────┘                                │ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Deployment Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        C1[Web Browser]
        C2[Mobile App]
        C3[API Clients]
    end
    
    subgraph "Load Balancer Layer"
        LB1[Nginx Load Balancer]
        LB2[SSL Termination]
        LB3[Health Checks]
    end
    
    subgraph "Application Layer"
        A1[Docker Container 1]
        A2[Docker Container 2]
        A3[Docker Container N]
        A4[Auto-scaling Group]
    end
    
    subgraph "Data Layer"
        D1[PostgreSQL Primary]
        D2[PostgreSQL Replica]
        D3[Redis Cluster]
        D4[Vector Database]
        D5[File Storage]
    end
    
    subgraph "External Services"
        E1[OpenAI API]
        E2[JIRA API]
        E3[Monitoring Services]
    end
    
    C1 --> LB1
    C2 --> LB1
    C3 --> LB1
    
    LB1 --> A1
    LB1 --> A2
    LB1 --> A3
    LB1 --> A4
    
    A1 --> D1
    A1 --> D3
    A1 --> D4
    A2 --> D2
    A2 --> D3
    A2 --> D4
    A3 --> D1
    A3 --> D3
    A3 --> D4
    
    A1 --> E1
    A1 --> E2
    A2 --> E1
    A2 --> E2
    
    A4 --> E3
```

## Security Architecture

### Authentication & Authorization
- **API Key Management**: Secure storage of OpenAI and JIRA API keys
- **Environment Variables**: Sensitive configuration via .env files
- **Access Control**: Role-based access for different user types
- **Session Management**: Secure session handling with Redis

### Data Security
- **Input Validation**: Comprehensive input sanitization
- **Output Sanitization**: Safe handling of generated content
- **File Upload Security**: Validation of document formats and content
- **Data Encryption**: Encryption at rest and in transit

### API Security
- **Rate Limiting**: Protection against API abuse
- **CORS Configuration**: Controlled cross-origin access
- **Input Validation**: Schema validation for all inputs
- **Error Handling**: Secure error messages without information leakage

### Security Architecture Diagram

```mermaid
graph TB
    subgraph "Client Security"
        CS1[HTTPS/TLS 1.3]
        CS2[Input Validation]
        CS3[Rate Limiting]
    end
    
    subgraph "API Gateway Security"
        AG1[API Key Validation]
        AG2[CORS Policy]
        AG3[Request Sanitization]
        AG4[Authentication Middleware]
    end
    
    subgraph "Application Security"
        AS1[Environment Variable Protection]
        AS2[Input Sanitization]
        AS3[Output Encoding]
        AS4[Session Management]
    end
    
    subgraph "Data Security"
        DS1[Database Encryption]
        DS2[File System Security]
        DS3[Cache Security]
        DS4[Backup Encryption]
    end
    
    subgraph "Infrastructure Security"
        IS1[Container Security]
        IS2[Network Security]
        IS3[Monitoring & Alerting]
        IS4[Vulnerability Scanning]
    end
    
    CS1 --> AG1
    CS2 --> AG2
    CS3 --> AG3
    
    AG1 --> AS1
    AG2 --> AS2
    AG3 --> AS3
    AG4 --> AS4
    
    AS1 --> DS1
    AS2 --> DS2
    AS3 --> DS3
    AS4 --> DS4
    
    DS1 --> IS1
    DS2 --> IS2
    DS3 --> IS3
    DS4 --> IS4
```

## Performance & Scalability

### Performance Optimizations
- **Parallel Processing**: Multi-threaded test case generation
- **Caching Strategy**: Redis-based caching for RAG results
- **Batch Processing**: Efficient handling of multiple documents
- **Async Operations**: Non-blocking I/O operations

### Scalability Features
- **Horizontal Scaling**: Docker container orchestration
- **Load Balancing**: Distribution of processing load
- **Database Optimization**: Vector indexing for fast retrieval
- **Resource Management**: Efficient memory and CPU utilization

### Monitoring & Metrics
- **Performance Metrics**: Response times and throughput
- **Resource Utilization**: CPU, memory, and disk usage
- **Error Rates**: Failure tracking and alerting
- **Business Metrics**: Processing success rates and quality scores

### Performance Architecture Diagram

```mermaid
graph TB
    subgraph "Performance Monitoring"
        PM1[Response Time Tracking]
        PM2[Throughput Monitoring]
        PM3[Resource Utilization]
        PM4[Error Rate Tracking]
    end
    
    subgraph "Caching Layer"
        CL1[Redis Cache]
        CL2[In-Memory Cache]
        CL3[File System Cache]
        CL4[Database Query Cache]
    end
    
    subgraph "Parallel Processing"
        PP1[Thread Pool Executor]
        PP2[Async I/O Operations]
        PP3[Batch Processing]
        PP4[Load Balancing]
    end
    
    subgraph "Database Optimization"
        DO1[Vector Indexing]
        DO2[Query Optimization]
        DO3[Connection Pooling]
        DO4[Read Replicas]
    end
    
    subgraph "Auto-scaling"
        AS1[Container Orchestration]
        AS2[Load-based Scaling]
        AS3[Resource Monitoring]
        AS4[Performance Alerts]
    end
    
    PM1 --> CL1
    PM2 --> PP1
    PM3 --> AS1
    PM4 --> AS4
    
    CL1 --> PP1
    CL2 --> PP2
    CL3 --> PP3
    CL4 --> DO1
    
    PP1 --> DO2
    PP2 --> DO3
    PP3 --> DO4
    
    DO1 --> AS2
    DO2 --> AS3
    DO3 --> AS4
```

## Domain Knowledge Documentation

### Knowledge Base Structure

The system maintains a comprehensive knowledge base that serves as the foundation for domain-specific story enhancement and test case generation.

#### 1. Vector Database (`knowledgebase/`)
- **Purpose**: Store document chunks with vector embeddings for semantic search
- **Content**: Domain-specific documents, templates, and best practices
- **Technology**: PostgreSQL with pgvector extension
- **Access**: Via AdaptiveRAG pipeline for context retrieval

#### 2. Domain Context Integration
- **Business Rules**: Domain-specific business logic and constraints
- **System Integration**: API specifications and system dependencies
- **Compliance Requirements**: Regulatory and industry standards
- **Testing Standards**: Quality assurance and testing methodologies

#### 3. Template Library
- **Story Templates**: Pre-defined structures for different story types
- **Test Case Templates**: Standardized test case formats
- **Validation Templates**: Quality assessment frameworks
- **Output Templates**: Standardized output formats (DOCX, JIRA, JSON)

### Knowledge Base Components

#### 1. Adaptive RAG Pipeline
- **Retriever Node**: Core retrieval logic with vector similarity search
- **Context Assembly**: Intelligent combination of retrieved chunks
- **Domain Filtering**: Relevance-based filtering for domain context
- **Dynamic Adaptation**: Query-specific retrieval optimization

#### 2. Domain-Specific Prompts
- **Enhanced Prompts**: Domain-aware prompt engineering
- **Context Integration**: RAG context integration in prompts
- **Quality Standards**: Domain-specific quality criteria
- **Validation Rules**: Domain-relevant validation logic

#### 3. Business Context Management
- **Actor Definitions**: User roles and permissions
- **System Dependencies**: Integration points and dependencies
- **Business Rules**: Domain-specific business logic
- **Compliance Requirements**: Regulatory and industry standards

### Knowledge Base Integration

The knowledge base integrates with the main system through:

1. **RAG Service**: Primary interface for context retrieval
2. **Prompt Engineering**: Domain-specific prompt generation
3. **Validation Logic**: Quality assessment based on domain knowledge
4. **Test Case Generation**: Domain-aware test scenario creation

### Knowledge Base Architecture Diagram

```mermaid
graph TB
    subgraph "Knowledge Sources"
        KS1[Domain Documents]
        KS2[Business Rules]
        KS3[Compliance Standards]
        KS4[Testing Templates]
    end
    
    subgraph "Processing Pipeline"
        PP1[Document Chunking]
        PP2[Vector Embedding]
        PP3[Metadata Extraction]
        PP4[Indexing]
    end
    
    subgraph "Storage Layer"
        SL1[PostgreSQL Database]
        SL2[pgvector Extension]
        SL3[Vector Indexes]
        SL4[Metadata Store]
    end
    
    subgraph "Retrieval System"
        RS1[Query Processing]
        RS2[Vector Similarity Search]
        RS3[Relevance Scoring]
        RS4[Context Assembly]
    end
    
    subgraph "Integration Layer"
        IL1[RAG Service]
        IL2[Prompt Engineering]
        IL3[Domain Context]
        IL4[Quality Validation]
    end
    
    KS1 --> PP1
    KS2 --> PP2
    KS3 --> PP3
    KS4 --> PP4
    
    PP1 --> SL1
    PP2 --> SL2
    PP3 --> SL3
    PP4 --> SL4
    
    SL1 --> RS1
    SL2 --> RS2
    SL3 --> RS3
    SL4 --> RS4
    
    RS1 --> IL1
    RS2 --> IL2
    RS3 --> IL3
    RS4 --> IL4
```

## API Documentation

### Core API Endpoints

#### 1. Story Processing API
- **POST /process-story**: Process a single story document
- **POST /process-batch**: Process multiple stories in batch
- **GET /status/{job_id}**: Get processing status

#### 2. Test Case Generation API
- **POST /generate-testcases**: Generate test cases from enhanced story
- **POST /validate-testcases**: Validate generated test cases
- **POST /regenerate-failed**: Regenerate failed test cases

#### 3. JIRA Integration API
- **POST /jira/import**: Import stories from JIRA
- **POST /jira/export**: Export enhanced stories to JIRA
- **GET /jira/status**: Get JIRA integration status

### API Response Formats

#### Standard Response Structure
```json
{
  "status": "success|error|processing",
  "message": "Human readable message",
  "data": {
    "job_id": "unique_identifier",
    "result": "processing_result",
    "metadata": "additional_information"
  },
  "timestamp": "ISO_8601_timestamp"
}
```

#### Error Response Structure
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": "Additional error information"
  },
  "timestamp": "ISO_8601_timestamp"
}
```

### API Architecture Diagram

```mermaid
graph TB
    subgraph "Client Applications"
        CA1[Web Application]
        CA2[Mobile App]
        CA3[Third-party Integrations]
        CA4[CLI Tools]
    end
    
    subgraph "API Gateway"
        AG1[Authentication]
        AG2[Rate Limiting]
        AG3[Request Routing]
        AG4[Response Caching]
    end
    
    subgraph "API Endpoints"
        EP1[Story Processing]
        EP2[Test Case Generation]
        EP3[JIRA Integration]
        EP4[Validation Services]
        EP5[File Management]
    end
    
    subgraph "Service Layer"
        SL1[Story Processor]
        SL2[Test Case Generator]
        SL3[Validator Service]
        SL4[File Service]
    end
    
    subgraph "Data Layer"
        DL1[Database]
        DL2[File Storage]
        DL3[Cache]
        DL4[External APIs]
    end
    
    CA1 --> AG1
    CA2 --> AG1
    CA3 --> AG1
    CA4 --> AG1
    
    AG1 --> AG2
    AG2 --> AG3
    AG3 --> AG4
    
    AG4 --> EP1
    AG4 --> EP2
    AG4 --> EP3
    AG4 --> EP4
    AG4 --> EP5
    
    EP1 --> SL1
    EP2 --> SL2
    EP3 --> SL1
    EP4 --> SL3
    EP5 --> SL4
    
    SL1 --> DL1
    SL2 --> DL1
    SL3 --> DL1
    SL4 --> DL2
    
    SL1 --> DL3
    SL2 --> DL3
    SL3 --> DL3
    SL4 --> DL3
    
    SL1 --> DL4
    SL2 --> DL4
    SL3 --> DL4
```

## Configuration Management

### Environment Configuration

The system uses a hierarchical configuration approach:

#### 1. Environment Variables (.env)
- **API Keys**: OpenAI, JIRA, and other external service credentials
- **Database Configuration**: Connection strings and credentials
- **Feature Flags**: Enable/disable specific functionality
- **Performance Tuning**: Parallel processing and caching parameters

#### 2. Application Settings (`components/common/settings.py`)
- **Default Values**: Fallback configuration values
- **Validation Logic**: Configuration validation and error handling
- **Dynamic Configuration**: Runtime configuration updates
- **Environment-Specific Settings**: Development vs. production configurations

#### 3. Component-Specific Configuration
- **Service Configuration**: Individual service settings
- **Parser Configuration**: Document parser specific settings
- **Output Configuration**: Format and structure preferences
- **Validation Configuration**: Quality assessment parameters

### Configuration Categories

#### 1. Core System Configuration
- **Model Selection**: LLM model selection and parameters
- **Processing Limits**: Maximum attempts and retry configurations
- **Output Directories**: File storage and organization
- **Logging Configuration**: Log levels and file management

#### 2. Feature Configuration
- **Service Enablement**: Enable/disable specific services
- **Output Formats**: Supported output format selection
- **Integration Settings**: External service configurations
- **Quality Thresholds**: Validation and quality criteria

#### 3. Performance Configuration
- **Parallel Processing**: Worker thread configuration
- **Caching Settings**: Cache TTL and storage configuration
- **Batch Processing**: Batch size and processing limits
- **Resource Limits**: Memory and CPU utilization limits

### Configuration Validation

The system includes comprehensive configuration validation:

1. **Required Parameters**: Validation of mandatory configuration
2. **Type Validation**: Data type and format validation
3. **Range Validation**: Numeric parameter range checking
4. **Dependency Validation**: Inter-parameter dependency validation
5. **Environment Validation**: Runtime environment compatibility checking

### Configuration Management Diagram

```mermaid
graph TB
    subgraph "Configuration Sources"
        CS1[Environment Variables]
        CS2[Configuration Files]
        CS3[Database Settings]
        CS4[Runtime Configuration]
    end
    
    subgraph "Configuration Processing"
        CP1[Environment Loading]
        CP2[File Parsing]
        CP3[Validation Logic]
        CP4[Default Values]
    end
    
    subgraph "Configuration Storage"
        CS5[Settings Class]
        CS6[Component Configs]
        CS7[Feature Flags]
        CS8[Performance Tuning]
    end
    
    subgraph "Configuration Distribution"
        CD1[Service Initialization]
        CD2[Runtime Updates]
        CD3[Hot Reloading]
        CD4[Configuration Monitoring]
    end
    
    CS1 --> CP1
    CS2 --> CP2
    CS3 --> CP3
    CS4 --> CP4
    
    CP1 --> CS5
    CP2 --> CS6
    CP3 --> CS7
    CP4 --> CS8
    
    CS5 --> CD1
    CS6 --> CD2
    CS7 --> CD3
    CS8 --> CD4
    
    CD1 --> CD4
    CD2 --> CD4
    CD3 --> CD4
```

---

## Conclusion

This architecture document provides a comprehensive overview of the Nomiso IntelliQ platform, detailing its component structure, data flows, technology stack, and deployment considerations. The system is designed with modularity, scalability, and extensibility in mind, leveraging AI/ML capabilities to deliver intelligent story enhancement and test case generation.

The architecture supports both development and production environments, with robust error handling, comprehensive logging, and performance optimization features. The knowledge base integration ensures domain-specific quality and relevance, while the modular design allows for easy extension and customization.

For implementation details, refer to the individual component documentation and code comments throughout the codebase.
