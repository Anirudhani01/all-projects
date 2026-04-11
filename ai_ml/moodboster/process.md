### System Architecture Overview

The proposed system is a **Mood-Aware Diary Companion (MADC)**, a multi-layered AI-driven application that processes user diary entries to detect emotional states and generates personalized, mood-diverting responses. It emphasizes modularity, scalability, and user engagement, using natural language processing (NLP) for mood detection, generative AI for content creation, and a decision engine for adaptive responses.

Key Design Principles:
- **Modularity**: Each layer is independent, allowing easy updates (e.g., swapping NLP models).
- **Personalization**: Incorporates user history (e.g., past moods) in the middle layer for context-aware decisions.
- **Diversion Focus**: Prioritizes non-intrusive, positive diversions for negative moods (e.g., anger → calming stories; sadness → uplifting quotes).
- **Tech Stack** (High-Level):
  - Backend: Python with FastAPI for API orchestration.
  - NLP/Sentiment: Hugging Face Transformers (e.g., BERT for mood classification).
  - Generative AI: OpenAI GPT or Grok API for quotes/stories; Spotify/YouTube APIs for music/videos.
  - Database: SQLite/PostgreSQL for user history; Vector DB (e.g., Pinecone) for embeddings of past entries.
  - Frontend: Streamlit or React for diary input/output interface.
  - Deployment: Docker + AWS/Heroku for scalability.

The system flow:
1. User submits diary text via app/web.
2. Layers process sequentially.
3. Response delivered interactively (e.g., chat-like engagement).

#### Expanded Layer Descriptions
1. **Input Layer**:
   - **Purpose**: Ingests raw diary text and performs initial mood analysis.
   - **Components**:
     - Text Preprocessor: Cleans input (remove noise, tokenize).
     - Mood Detector: Multi-label sentiment classifier (emotions: happy, sad, angry, neutral, etc.) using pre-trained models.
   - **Output**: Raw text + Mood Score (e.g., JSON: `{"mood": "angry", "confidence": 0.85, "key_phrases": ["frustrated at work"]}`).

2. **Middle Layer**:
   - **Purpose**: Enriches mood data with context from user history and thematic analysis for nuanced understanding.
   - **Components**:
     - Context Analyzer: Retrieves past entries via DB query; computes mood trends (e.g., "recurrent anger on Mondays").
     - Theme Extractor: Uses topic modeling (e.g., LDA) to identify triggers (e.g., "work stress").
   - **Output**: Enriched context (e.g., JSON: `{"mood": "angry", "triggers": ["work"], "history_trend": "increasing"}`).

3. **Decision Layer**:
   - **Purpose**: Orchestrates response strategy based on enriched mood; selects and invokes generators.
   - **Components**:
     - Decision Engine: Rule-based + ML (e.g., if mood="angry" and trend="increasing", prioritize story + music).
     - Generators:
       - Quote Generator: Fetches/generates inspirational quotes via API (e.g., ZenQuotes) or LLM prompt.
       - Story Generator: LLM-based short story tailored to mood (e.g., "A tale of overcoming frustration").
       - Music Generator: Recommends tracks via Spotify API (e.g., query "calming instrumental" for anger).
       - Video Generator: Suggests short clips via YouTube API (e.g., "funny cat videos" for sadness).
     - Combiner: Mixes outputs (e.g., quote + music playlist).
   - **Output**: Response Plan (e.g., JSON: `{"actions": ["quote", "story"], "content": {...}}`).

4. **Output Layer**:
   - **Purpose**: Delivers and engages user with the response in an interactive format.
   - **Components**:
     - Renderer: Formats content (text, embeds for music/video).
     - Engagement Handler: Follow-up prompts (e.g., "How does this story make you feel?") to sustain interaction.
     - Feedback Loop: Captures user reaction to refine future moods.
   - **Output**: User-facing response (e.g., chat message with embedded media).

Error Handling: Across layers, implement logging (e.g., ELK stack) and fallbacks (e.g., neutral response if mood detection fails).

Security/Privacy: Encrypt diary entries; GDPR-compliant data storage.

### Architecture Diagram

Below is a textual representation of the architecture diagram using Mermaid syntax (you can copy-paste this into a Mermaid renderer like mermaid.live for visualization). It shows the layered flow, components, and data flow.

```
graph TD
    subgraph "User Interface"
        A[Diary Input<br/>(Text Entry)]
        Z[Engaging Response<br/>(Chat/Embeds)]
    end

    subgraph "Layer 1: Input Layer"
        B[Text Preprocessor]
        C[Mood Detector<br/>(NLP Model)]
    end

    subgraph "Layer 2: Middle Layer"
        D[Context Analyzer<br/>(DB Query)]
        E[Theme Extractor<br/>(Topic Modeling)]
    end

    subgraph "Layer 3: Decision Layer"
        F[Decision Engine<br/>(Rules + ML)]
        G[Quote Generator<br/>(API/LLM)]
        H[Story Generator<br/>(LLM)]
        I[Music Generator<br/>(Spotify API)]
        J[Video Generator<br/>(YouTube API)]
        K[Combiner]
    end

    subgraph "Layer 4: Output Layer"
        L[Renderer<br/>(Format Content)]
        M[Engagement Handler<br/>(Follow-ups)]
        N[Feedback Loop<br/>(Update DB)]
    end

    subgraph "Shared Components"
        O[User DB<br/>(History + Embeddings)]
    end

    A -->|Raw Text| B
    B -->|Cleaned Text| C
    C -->|Mood Score| D
    A -->|Raw Text| D
    D -->|History Context| E
    E -->|Triggers + Trends| F
    F -->|Select Actions| G
    F --> H
    F --> I
    F --> J
    G -->|Content| K
    H --> K
    I --> K
    J --> K
    K -->|Response Plan| L
    L -->|Formatted Output| M
    M --> Z
    M -->|User Feedback| N
    N --> O
    D --> O
    O --> D
    style A fill:#e1f5fe
    style Z fill:#e8f5e8
```

**Diagram Explanation**:
- **Vertical Flow**: Top-to-bottom represents sequential processing.
- **Subgraphs**: Group layers for clarity.
- **Arrows**: Data flow; shared DB connects middle/feedback.
- **Colors**: Light blue for input/output UI; green for response.

### Detailed Action Plan

This is a phased implementation plan, assuming a small team (1-3 developers) with 4-6 weeks total timeline. Each phase includes tasks, tools, milestones, and testing.

#### Phase 1: Planning & Setup (Week 1)
1. **Refine Requirements**:
   - Document edge cases (e.g., ambiguous moods like "mixed emotions").
   - Define mood categories (e.g., 5-7 emotions) and diversion mappings (e.g., angry → 70% music, 30% quotes).
   - Milestone: Requirements doc (Google Docs).

2. **Environment Setup**:
   - Initialize repo (GitHub); set up virtual env (Python 3.10+).
   - Install core libs: `transformers`, `torch`, `fastapi`, `uvicorn`, `pydantic`, `scikit-learn` for LDA.
   - API Keys: Sign up for OpenAI/Grok (LLM), Spotify/YouTube (media).
   - Milestone: Local dev server running "Hello World" endpoint.

3. **Database Design**:
   - Schema: Users table (ID, history JSON); Entries table (user_id, text, mood, timestamp).
   - Implement CRUD with SQLAlchemy.
   - Milestone: Test DB inserts/queries.

#### Phase 2: Implement Input & Middle Layers (Week 2)
1. **Input Layer**:
   - Build preprocessor: Use `nltk` for tokenization/stopwords.
   - Mood Detector: Fine-tune Hugging Face `distilbert-base-uncased-finetuned-sst-2-english` for multi-emotion (train on EmoInt dataset if needed; start with zero-shot via pipeline).
   - Endpoint: POST `/input` → Returns mood JSON.
   - Testing: Unit tests with sample diaries (e.g., "I hate my boss" → angry); accuracy >80%.

2. **Middle Layer**:
   - Context Analyzer: Query DB for last 7 days; compute trends (e.g., simple avg mood score).
   - Theme Extractor: Use `sklearn.decomposition.LatentDirichletAllocation` on tokenized text.
   - Endpoint: POST `/middle` (takes input + mood) → Enriched JSON.
   - Milestone: End-to-end test: Input text → Enriched output.

3. **Integration Testing**:
   - Mock DB; run Pytest suite for layer chaining.

#### Phase 3: Implement Decision & Output Layers (Weeks 3-4)
1. **Decision Layer**:
   - Decision Engine: Use if-else rules + lightweight ML (e.g., RandomForest on mood+triggers for action probs).
   - Generators:
     - Quote/Story: Prompt LLM (e.g., "Generate a 100-word story about overcoming anger at work").
     - Music/Video: API calls (e.g., Spotify `search` endpoint with mood-based queries like "relaxing jazz").
   - Combiner: Logic to limit responses (e.g., max 2 actions per response).
   - Endpoint: POST `/decision` → Response plan JSON.
   - Testing: Mock APIs; validate outputs (e.g., story length 50-200 words).

2. **Output Layer**:
   - Renderer: Use Jinja2 for text; embed media via iframes/URLs.
   - Engagement: Simple stateful chat (e.g., via WebSockets in FastAPI).
   - Feedback: POST `/feedback` to update DB mood accuracy.
   - Endpoint: GET/POST `/output` → Rendered response.
   - Milestone: Full pipeline demo: Diary input → Interactive response.

3. **UI Development**:
   - Backend: FastAPI routes for all layers.
   - Frontend: Streamlit app with text area for input, display for outputs (embeds for media).
   - Testing: E2E with Selenium; user simulation for moods.

#### Phase 4: Polish, Deploy & Iterate (Weeks 5-6)
1. **Enhancements**:
   - Add personalization (e.g., user prefs for preferred diversion type).
   - Multi-modal input (e.g., voice-to-text via Whisper API).
   - Analytics: Track engagement (e.g., response open rates).

2. **Testing & Security**:
   - Load testing: Locust for 100 concurrent users.
   - Security: Input sanitization (OWASP); encrypt DB fields.
   - Bias Audit: Test NLP on diverse datasets (e.g., cultural variations in "anger").



