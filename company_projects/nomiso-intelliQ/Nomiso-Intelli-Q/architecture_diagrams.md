# Nomiso IntelliQ - Architecture Diagrams

This document contains comprehensive Mermaid diagrams that visualize the system architecture, data flows, and component interactions of the Nomiso IntelliQ platform.

## 1. System Architecture Overview

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

## 2. Component Interaction Diagram

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

## 3. Primary Story Processing Flow

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

## 4. Test Case Generation Flow

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

## 5. RAG Context Retrieval Flow

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

## 6. Detailed Workflow State Machine

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

## 7. Service Dependency Graph

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

## 8. Technology Stack Diagram

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

## 9. Deployment Architecture Diagram

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

## 10. Security Architecture Diagram

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

## 11. Performance Architecture Diagram

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

## 12. Knowledge Base Architecture Diagram

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

## 13. API Architecture Diagram

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

## 14. Configuration Management Diagram

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

## 15. Complete System Integration Diagram

```mermaid
graph TB
    subgraph "User Interface"
        UI1[Web Dashboard]
        UI2[API Clients]
        UI3[CLI Interface]
    end
    
    subgraph "API Gateway"
        GW1[Load Balancer]
        GW2[Authentication]
        GW3[Rate Limiting]
    end
    
    subgraph "Core Application"
        APP1[Story Processor]
        APP2[Workflow Manager]
        APP3[Service Orchestrator]
    end
    
    subgraph "AI Services"
        AI1[LLM Client]
        AI2[Enhancer Service]
        AI3[Checker Service]
        AI4[Test Generator]
    end
    
    subgraph "Data Processing"
        DP1[RAG Service]
        DP2[Parser Services]
        DP3[Validation Services]
    end
    
    subgraph "Storage Layer"
        ST1[PostgreSQL + pgvector]
        ST2[Redis Cache]
        ST3[File System]
        ST4[Vector Database]
    end
    
    subgraph "External Integrations"
        EXT1[OpenAI API]
        EXT2[JIRA API]
        EXT3[Monitoring Services]
    end
    
    UI1 --> GW1
    UI2 --> GW1
    UI3 --> GW1
    
    GW1 --> GW2
    GW2 --> GW3
    GW3 --> APP1
    
    APP1 --> APP2
    APP2 --> APP3
    
    APP3 --> AI1
    APP3 --> AI2
    APP3 --> AI3
    APP3 --> AI4
    
    APP3 --> DP1
    APP3 --> DP2
    APP3 --> DP3
    
    AI1 --> EXT1
    DP1 --> ST4
    DP2 --> ST3
    DP3 --> ST1
    
    APP3 --> ST2
    APP3 --> ST1
    
    AI1 --> AI2
    AI1 --> AI3
    AI1 --> AI4
    
    AI2 --> DP3
    AI3 --> DP3
    AI4 --> DP3
    
    DP1 --> EXT2
    APP3 --> EXT3
```

---

## Diagram Usage Instructions

These Mermaid diagrams can be rendered in:

1. **GitHub**: GitHub supports Mermaid diagrams natively in markdown files
2. **GitLab**: GitLab also supports Mermaid diagrams
3. **VS Code**: Use the Mermaid Preview extension
4. **Online Mermaid Editor**: https://mermaid.live/
5. **Documentation Tools**: Many documentation platforms support Mermaid

## Key Architecture Patterns

1. **Layered Architecture**: Clear separation between input, processing, and output layers
2. **Service-Oriented Design**: Modular services with well-defined responsibilities
3. **Event-Driven Workflow**: State-based workflow management using LangGraph
4. **AI-First Integration**: LLM services integrated at multiple layers
5. **RAG-Powered Context**: Retrieval-augmented generation for domain knowledge
6. **Microservices Pattern**: Independent services that can be scaled and deployed separately

## Component Relationships

- **Story Processor**: Central orchestrator coordinating all services
- **Workflow Manager**: Manages state transitions and retry logic
- **RAG Service**: Provides context-aware information retrieval
- **AI Services**: Handle intelligent processing and generation
- **Validation Pipeline**: Ensures quality and accuracy of outputs
- **Knowledge Base**: Stores domain-specific context and templates
