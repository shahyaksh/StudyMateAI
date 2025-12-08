# Lecture RAG Frontend

An intelligent lecture learning platform with AI-powered chatbot, interactive quizzes, and flashcards. Built with React, TypeScript, and Vite for a modern, responsive user experience.

## Overview

This application provides an interactive interface for students to engage with lecture content through multiple learning modalities:

- **AI Chatbot**: Ask questions about lecture slides, transcripts, and research papers
- **Interactive Quizzes**: Test knowledge with AI-generated multiple-choice questions
- **Flashcards**: Study key concepts with spaced repetition
- **Video Player**: Watch lectures with synchronized content
- **Content Navigation**: Browse slides, transcripts, and notes

## Features

### 1. AI-Powered Chatbot

- **Natural Language Queries**: Ask questions in plain English
- **Multi-Source Answers**: Retrieves information from slides, transcripts, and papers
- **Contextual Understanding**: Maintains conversation history for follow-up questions
- **Slide References**: Answers include specific slide numbers and titles
- **Academic Citations**: Research paper answers include proper citations

**Example Interactions:**
```
Q: "What is instruction tuning?"
A: According to Slide 12 "Instruction Tuning":
   Instruction tuning is a technique to fine-tune language models...
   
Q: "How does it compare to RLHF?"
A: [Contextual follow-up using conversation history]
```

### 2. Quiz Generation

- **AI-Generated Questions**: Creates exam-appropriate multiple-choice questions
- **Customizable**: Choose number of questions (1-20)
- **Difficulty Levels**: Questions span easy, medium, and hard
- **Instant Feedback**: See correct answers and explanations
- **Score Tracking**: Track performance across quizzes

**Features:**
- Multiple-choice format (A/B/C/D options)
- Detailed explanations for each answer
- Topic categorization
- Progress tracking

### 3. Flashcard System

- **Spaced Repetition**: Mark cards as "known" or "unknown"
- **Flip Animation**: Interactive card flipping
- **Progress Tracking**: Visual progress bar
- **Keyboard Navigation**: Arrow keys for quick navigation
- **Comprehensive Coverage**: Covers all lecture topics

### 4. Lecture Browser

- **Lecture List**: Browse all available lectures
- **Search Functionality**: Find lectures by title or topic
- **Metadata Display**: View lecture duration, topics, and reading time
- **Quick Access**: Jump directly to specific lectures

### 5. Content Tabs

- **Notes**: View lecture notes and key points
- **Description**: Read lecture overview and objectives
- **Transcript**: Full searchable transcript with timestamps

## Project Structure

```
src/
├── main.tsx                    # Application entry point
├── App.tsx                     # Main application component
├── index.css                   # Global styles and Tailwind config
│
├── components/                 # React components
│   ├── Chatbot.tsx            # AI chatbot interface
│   ├── Quiz.tsx               # Quiz component
│   ├── FlashCards.tsx         # Flashcard system
│   ├── VideoPlayer.tsx        # Video player
│   ├── ContentTabs.tsx        # Content navigation tabs
│   ├── SidePanel.tsx          # Lecture list sidebar
│   └── FormattedMessage.tsx   # Message formatting
│
├── services/                   # API services
│   └── api.ts                 # Backend API integration
│
└── data/                       # Data and types
    ├── lectures.ts            # Lecture data loader
    └── lectureData.ts         # Lecture metadata
```

## Technology Stack

- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client for API calls

## Setup

You can run the application using either **Docker** (recommended for production and full-stack deployment) or **local development** (recommended for frontend development with hot reload).

### Option 1: Docker (Recommended for Production/Full Stack)

**Prerequisites:**
- Docker and Docker Compose installed
- `.env` file with required API keys (see root directory)

**Quick Start:**

```bash
# Run entire application (frontend + backend)
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

**Access:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Advantages:**
- ✅ Complete stack with one command
- ✅ Production-ready environment
- ✅ Consistent across different machines
- ✅ Isolated dependencies
- ✅ Easy deployment

**Docker Commands:**

```bash
# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build

# Remove containers and volumes
docker-compose down -v
```

---

### Option 2: Local Development (Recommended for Frontend Development)

**Prerequisites:**
- Node.js 18+ and npm
- Backend server running (see `backend/README.md`)

**Installation:**

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure API endpoint** (if needed):
   
   The frontend connects to `http://localhost:5000` by default. To change:
   
   Edit `src/services/api.ts`:
   ```typescript
   const API_BASE_URL = 'http://your-backend-url:5000';
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

   Application will be available at `http://localhost:3000`

**Advantages:**
- ✅ Hot Module Replacement (instant updates)
- ✅ Faster iteration cycle
- ✅ Better debugging with source maps
- ✅ Direct access to Vite dev tools

**Production Build:**

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Capabilities

### Current Features

✅ **Multi-Modal Learning**
- Text-based Q&A with AI
- Visual learning with slides
- Audio/video content
- Interactive quizzes
- Flashcard study system

✅ **Intelligent Interactions**
- Context-aware chatbot
- Conversation history
- Follow-up questions
- Multi-source retrieval

✅ **User Experience**
- Responsive design (desktop/tablet/mobile)
- Dark mode support
- Keyboard shortcuts
- Loading states and error handling
- Smooth animations

✅ **Content Organization**
- Lecture browsing
- Topic categorization
- Search functionality
- Timestamp navigation

### Performance

- **Fast Load Times**: Vite-optimized builds
- **Responsive UI**: Smooth 60fps animations
- **Efficient API Calls**: Request caching and deduplication
- **Lazy Loading**: Components loaded on demand

## User Interface

### Layout

```
┌─────────────────────────────────────────────────────┐
│  Header: Lecture RAG Platform                       │
├──────────┬──────────────────────────────────────────┤
│          │  Video Player                            │
│ Lecture  │                                          │
│  List    ├──────────────────────────────────────────┤
│          │  Content Tabs (Notes/Description/Trans)  │
│ (Sidebar)│                                          │
│          ├──────────────────────────────────────────┤
│          │  AI Chatbot                              │
│          │  [Quiz] [Flashcards] buttons             │
└──────────┴──────────────────────────────────────────┘
```

### Color Scheme

- **Primary**: Blue (#3B82F6) - Interactive elements
- **Secondary**: Purple (#8B5CF6) - Highlights
- **Success**: Green (#10B981) - Correct answers
- **Error**: Red (#EF4444) - Incorrect answers
- **Background**: White/Gray - Clean, readable

### Typography

- **Headings**: Inter font, bold
- **Body**: Inter font, regular
- **Code**: Monospace for technical content

## Future Scope

### Planned Features

#### 1. Enhanced Learning Tools

- **📊 Progress Dashboard**
  - Track quiz scores over time
  - Flashcard mastery metrics
  - Study time analytics
  - Topic proficiency heatmap

- **🎯 Personalized Learning**
  - Adaptive quiz difficulty
  - Recommended study topics
  - Weak area identification
  - Custom study plans

- **📝 Note-Taking System**
  - In-app note editor
  - Timestamp-linked notes
  - Highlight and annotate slides
  - Export notes to PDF/Markdown

#### 2. Collaboration Features

- **👥 Study Groups**
  - Shared quiz sessions
  - Group chat rooms
  - Collaborative flashcard decks
  - Peer Q&A forums

- **📢 Discussion Boards**
  - Lecture-specific discussions
  - Upvote/downvote answers
  - Expert verification
  - Tag system for topics

#### 3. Advanced AI Features

- **🤖 Smart Recommendations**
  - Related lecture suggestions
  - Prerequisite identification
  - Learning path generation
  - Content gap detection

- **🎨 Multimodal Understanding**
  - Diagram explanation
  - Image-based Q&A
  - Video clip retrieval
  - Interactive visualizations

- **🗣️ Voice Interaction**
  - Voice-to-text queries
  - Text-to-speech responses
  - Audio flashcards
  - Pronunciation help

#### 4. Content Enhancements

- **📚 Extended Content Types**
  - Textbook integration
  - Lab materials
  - Assignment helpers
  - Practice problems

- **🌐 Multi-Language Support**
  - Interface localization
  - Content translation
  - Cross-language search
  - Multilingual chatbot

#### 5. Mobile Experience

- **📱 Mobile Apps**
  - Native iOS app
  - Native Android app
  - Offline mode
  - Push notifications

- **⚡ Progressive Web App (PWA)**
  - Install to home screen
  - Offline access
  - Background sync
  - App-like experience

#### 6. Gamification

- **🏆 Achievement System**
  - Badges for milestones
  - Leaderboards
  - Streak tracking
  - XP and levels

- **🎮 Learning Games**
  - Quiz competitions
  - Flashcard battles
  - Timed challenges
  - Team tournaments

#### 7. Accessibility

- **♿ Enhanced Accessibility**
  - Screen reader optimization
  - Keyboard-only navigation
  - High contrast mode
  - Adjustable font sizes
  - Closed captions

#### 8. Integration & Export

- **🔗 Platform Integration**
  - LMS integration (Canvas, Blackboard)
  - Google Classroom sync
  - Calendar integration
  - Email notifications

- **📤 Export Options**
  - Export quiz results
  - Download flashcard decks (Anki format)
  - Print study guides
  - Share progress reports

#### 9. Analytics & Insights

- **📈 Learning Analytics**
  - Time spent per topic
  - Question difficulty analysis
  - Retention rate tracking
  - Optimal study time suggestions

- **🔍 Content Analytics**
  - Most asked questions
  - Popular topics
  - Confusion points
  - Content effectiveness

#### 10. Performance Optimization

- **⚡ Speed Improvements**
  - Server-side rendering (SSR)
  - Edge caching
  - Image optimization
  - Code splitting

## Development

### Running Locally

```bash
# Development mode with hot reload
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

### Building for Production

```bash
# Create optimized build
npm run build

# Preview production build locally
npm run preview
```

### Environment Variables

Create `.env` file:

```ini
VITE_API_URL=http://localhost:5000
VITE_APP_NAME=Lecture RAG Platform
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

### Code Style

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries
- Add loading states for async operations

### Component Guidelines

- Keep components focused and single-purpose
- Use props for configuration
- Implement proper TypeScript interfaces
- Add JSDoc comments for complex logic
- Handle edge cases gracefully

## License

MIT License

## Support

For issues or questions:
- Backend API: See `backend/README.md`
- Agent workflow: See `backend/agents/README.md`
- Evaluation: See `backend/evaluation/README.md`

---

**Built with ❤️ for enhanced learning experiences**
