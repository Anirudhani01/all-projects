Below is a detailed prompt for developing the frontend of the **Mood-Aware Diary Companion (MADC)** application, based on the architecture previously outlined. The prompt is designed to guide a frontend developer (or team) in building an intuitive, user-friendly interface that aligns with the system's goal of analyzing diary entries, detecting moods, and delivering personalized mood-diverting content (quotes, stories, music, videos). The prompt assumes a modern JavaScript framework (React recommended) and focuses on usability, responsiveness, and seamless integration with the backend.

---

### Frontend Development Prompt for Mood-Aware Diary Companion (MADC)

**Objective**:  
Design and implement a responsive, engaging, and user-friendly frontend for the Mood-Aware Diary Companion, a web-based application that allows users to input diary entries, processes their emotional state, and provides mood-diverting content (e.g., quotes, stories, music, videos) to improve their mood. The frontend should integrate seamlessly with a FastAPI backend, providing an interactive and visually appealing experience across devices.

**Target Audience**:  
Users seeking a digital diary with emotional support, ranging from casual users to those with mental health awareness. Assume moderate tech literacy; prioritize simplicity and emotional resonance.

**Tech Stack Requirements**:  
- **Framework**: React (preferred for component-based architecture) or Vue.js.  
- **State Management**: Redux Toolkit or React Context for managing user inputs and responses.  
- **Styling**: Tailwind CSS or Material-UI for responsive, modern design.  
- **API Integration**: Axios or Fetch for RESTful communication with FastAPI backend.  
- **Media Embedding**: Support for Spotify/YouTube embeds (iframes or SDKs).  
- **Build Tool**: Vite or Create React App.  
- **Deployment**: Vercel or Netlify for hosting.  

**Backend API Endpoints (Provided for Reference)**:  
- `POST /input`: Submits diary text; returns `{mood: string, confidence: float, key_phrases: string[]}`.  
- `POST /middle`: Sends mood + text; returns enriched context `{mood: string, triggers: string[], history_trend: string}`.  
- `POST /decision`: Sends enriched context; returns response plan `{actions: string[], content: {quotes?: string[], stories?: string[], music?: {url: string, title: string}[], videos?: {url: string, title: string}[]}}`.  
- `POST /output`: Sends response plan; returns formatted response for display.  
- `POST /feedback`: Submits user feedback (e.g., mood change or content rating).  
- Base URL (e.g., `https://madc-api.herokuapp.com`).

**Functional Requirements**:  
1. **Diary Input Interface**:  
   - A clean text area for users to write diary entries (min 50, max 2000 characters).  
   - Optional: Voice input button (integrate Web Speech API or Whisper API for transcription).  
   - Submit button to send entry to `/input` endpoint.  
   - Display loading state during processing.  
   - Error handling: Show user-friendly messages for failed submissions (e.g., "Please try again").  

2. **Response Display**:  
   - Chat-like interface to present mood-diverting content (quotes, stories, music, videos).  
   - Support dynamic rendering:  
     - Text (quotes/stories): Styled as cards or conversational bubbles.  
     - Music/Videos: Embedded players (Spotify/YouTube iframes or links).  
   - Follow-up prompts (e.g., "Did this story help? Write more or try another!").  
   - Feedback buttons (e.g., thumbs up/down or "How do you feel now?").  

3. **User Profile & History**:  
   - Simple profile page: Display user’s past entries (fetch from `/middle` with history).  
   - Visualize mood trends (e.g., pie chart of moods over last 7 days).  
   - Option to delete entries (GDPR compliance).  

4. **Accessibility & Responsiveness**:  
   - Responsive design: Mobile-first (works on screens ≥320px).  
   - Accessibility: ARIA labels, keyboard navigation, high-contrast mode option.  
   - Smooth animations (e.g., fade-in for responses) using Framer Motion or CSS.  

**Non-Functional Requirements**:  
- **Performance**: Page load <2s; API response rendering <1s (use lazy loading for media).  
- **Security**: Sanitize user inputs (e.g., prevent XSS with DOMPurify).  
- **Privacy**: No client-side storage of sensitive diary data; use secure HTTPS for API calls.  
- **Theming**: Light/dark mode toggle (store preference in localStorage).  
- **Error Handling**: Graceful fallback for API failures (e.g., cached quote if network fails).  

**UI/UX Design Guidelines**:  
- **Tone**: Empathetic, warm, non-clinical (e.g., use phrases like "Let’s brighten your day!").  
- **Colors**:  
  - Primary: Soft blues (#4FC3F7) for calmness.  
  - Secondary: Warm yellows (#FFD54F) for positivity.  
  - Neutral: Gray (#424242) for dark mode; white (#F5F5F5) for light.  
- **Typography**: Sans-serif fonts (e.g., Inter or Roboto) for readability; min 16px base size.  
- **Layout**:  
  - Mobile: Single-column, sticky footer for navigation.  
  - Desktop: Two-column (input left, responses right).  
  - Navigation: Simple top bar or hamburger menu (Home, Profile, Settings).  
- **Inspiration**: Apps like Notion (clean text input), Replika (chat-like interaction), or Calm (mood-based content).  

**Key Features & User Flow**:  
1. **Landing Page**:  
   - Welcome message: "Write your thoughts, and let us lift your spirits!"  
   - Call-to-action: Button to start diary entry or view profile.  
   - Minimalist design with subtle animations (e.g., fading hero text).  

2. **Diary Entry Page**:  
   - Textarea with placeholder: "How was your day? Share your thoughts…"  
   - Voice input button (optional).  
   - Submit triggers API call to `/input` → `/middle` → `/decision` → `/output`.  
   - Loading spinner with message: "Understanding your mood…"  

3. **Response Page**:  
   - Chat-style layout: Bot message with mood summary (e.g., "Sounds like you’re feeling frustrated.").  
   - Render content based on API response:  
     - Quote: Card with bold text (e.g., "‘Stay calm, you’ve got this!’ — Anonymous").  
     - Story: Scrollable text box (100-200 words).  
     - Music/Video: Embedded player or clickable thumbnail.  
   - Feedback buttons: "This helped!" or "Try something else."  
   - Prompt to continue writing or view history.  

4. **Profile/History Page**:  
   - List past entries (date, snippet, mood).  
   - Mood chart (e.g., pie chart: 40% happy, 30% sad, etc.).  
   - Delete entry button (confirm dialog).  

**Development Tasks**:  
1. **Setup (Days 1-2)**:  
   - Initialize project with Vite/React, Tailwind CSS, and Axios.  
   - Set up routing (React Router) for Home, Diary, Profile, Settings.  
   - Configure ESLint + Prettier for code quality.  
   - Milestone: Boilerplate app running locally.  

2. **Core UI Components (Days 3-5)**:  
   - Build reusable components:  
     - `DiaryInput`: Textarea + voice button + submit.  
     - `ResponseCard`: Dynamic renderer for quotes/stories/media.  
     - `FeedbackButton`: Thumbs up/down with API call to `/feedback`.  
     - `MoodChart`: Chart.js pie chart for mood trends.  
   - Style with Tailwind; ensure mobile responsiveness.  
   - Milestone: Static UI prototype (no API integration).  

3. **API Integration (Days 6-8)**:  
   - Implement API calls for each endpoint using Axios.  
   - Handle loading/error states (e.g., Skeleton UI for loading).  
   - Test with mock API responses (use MSW for local testing).  
   - Milestone: Diary input → Mood response flow working.  

4. **Media & Interactivity (Days 9-11)**:  
   - Embed Spotify/YouTube players (use official SDKs or iframes).  
   - Add chat-like animations (e.g., typewriter effect for text).  
   - Implement feedback loop: POST to `/feedback` on button click.  
   - Milestone: Full response rendering with media.  

5. **Profile & History (Days 12-13)**:  
   - Fetch and display entry history from `/middle`.  
   - Create `MoodChart` component using Chart.js (pie chart).  
   - Add delete functionality with confirmation modal.  
   - Milestone: Profile page fully functional.  

6. **Polish & Testing (Days 14-15)**:  
   - Add light/dark mode toggle (Tailwind `dark:` classes).  
   - Ensure accessibility (screen reader tests with axe DevTools).  
   - Test responsiveness (Chrome DevTools device mode).  
   - Write unit tests for components (React Testing Library).  

**Deliverables**:  
  
- Documentation: README with setup, API integration, and testing instructions.  
- Optional: Figma mockup (if designer available) or screenshots of UI.  

**Success Metrics**:  
- Usability: 90% of test users can submit a diary entry and receive a response in <5s.  
- Engagement: Users interact with at least one response (click media or submit feedback).  
- Accessibility: No critical WCAG violations (Level AA).  

**Constraints & Risks**:  
- **API Latency**: Mitigate with client-side caching (e.g., useSWR).  
- **Media Embed Limits**: Fallback to URLs if Spotify/YouTube SDKs fail.  
 

**Future Enhancements**:  
- Mobile app (React Native).  
- Push notifications for daily diary reminders.  
- Customizable themes or avatars for personalization.  

**Sample Wireframe (Text-Based)**:  
```
[Header: Logo | Profile | Settings (Dark Mode Toggle)]
[Diary Page]
  "Write your thoughts..."
  [Textarea: 5 rows, full-width on mobile]
  [Voice Input Button] [Submit Button]
  [Loading: Spinner + "Analyzing your mood..."]
[Response Page]
  [Chat Bubble: "You seem frustrated. Here's something to lift you up!"]
  [Card: Quote - "Stay calm, you've got this!"]
  [Card: Story - "Once, Alex faced a tough day..."]
  [Embed: Spotify Playlist - "Calm Vibes"]
  [Buttons: Thumbs Up | Thumbs Down | Write More]
[Profile Page]
  [List: Entry 1 (Sep 15, "Angry", "Work stress...")]
  [Chart: Pie - 40% Happy, 30% Sad, 30% Angry]
  [Button: Delete Entry]
```

**Acceptance Criteria**:  
- Users can submit diary entries and receive mood-based responses.  
- Responses render correctly (text, media embeds) on mobile and desktop.  
- Feedback submission updates backend.  
- Profile shows accurate history and mood trends.  
- App is responsive, accessible, and deployed live.  

