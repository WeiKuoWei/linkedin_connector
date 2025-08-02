# 📎 LinkedIn Weak Ties AI Chatbot

An AI-powered full-stack application that helps business professionals leverage their *weak ties* on LinkedIn. Upload your LinkedIn connections and get intelligent recommendations for specific business goals using enriched profile data, semantic search, and AI-powered matching.

---

## 🚀 Key Features

* **Smart CSV Import**: Upload LinkedIn `connections.csv` with automatic parsing
* **Profile Enrichment**: Automatically enriches LinkedIn profiles with detailed data (summary, location, industry, company size)
* **Semantic Search**: Vector embeddings with ChromaDB for intelligent connection matching
* **Incremental Processing**: Only processes new connections to minimize API costs
* **Real-time Progress**: Live progress tracking during profile enrichment
* **AI-Powered Matching**: GPT-4 analyzes enriched profiles against your mission
* **Personalized Outreach**: Generate custom LinkedIn messages for reconnection
* **Background Processing**: Non-blocking profile enrichment with progress tracking
* **Intelligent Caching**: Efficient storage with vectorization catch-up

---

## 🛠️ Technology Stack

### Frontend
* **React.js** - Component-based UI with custom hooks
* **Tailwind CSS** - Utility-first styling with responsive design
* **Axios** - HTTP client for API communication
* **Real-time polling** - Progress updates during enrichment

### Backend
* **FastAPI** - High-performance Python API with async support
* **ChromaDB** - Vector database for semantic search
* **Sentence Transformers** - Embedding generation (all-mpnet-base-v2)
* **Azure OpenAI (GPT-4)** - AI-powered connection matching and message generation
* **RapidAPI LinkedIn Scraper** - Profile enrichment service
* **Pandas** - CSV processing and data manipulation
* **Background Tasks** - Async processing with concurrent request limiting

---

## 📂 Project Structure

```
linkedin-ai-chatbot/
├── README.md
├── .gitignore
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js                   # Main React component
│   │   ├── components/              # UI components
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── services/                # API integration
│   │   └── styles/
│   └── package.json
│
├── backend/
│   ├── main.py                      # FastAPI application
│   ├── api/                         # API endpoints
│   ├── config/                      # Configuration
│   ├── services/                    # Core business logic
│   ├── data/                        # Data storage
│   ├── chroma_data/                 # ChromaDB persistence
│   └── requirements.txt
```

---

## ⚙️ Setup & Installation

### Prerequisites
* Python 3.8+
* Node.js 16+ 
* npm or yarn
* LinkedIn connections CSV export
* Azure OpenAI API access
* RapidAPI LinkedIn scraper access

### 1. Clone Repository
```bash
git clone <repository-url>
cd linkedin-ai-chatbot
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `backend/.env`:
```env
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_api_key
RAPIDAPI_KEY=your_rapidapi_key
```

### 4. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## 🚀 Running the Application

### Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```
Backend runs on: http://127.0.0.1:8000

### Start Frontend
```bash
cd frontend
npm start run
```
Frontend runs on: http://localhost:3000

---

## 💡 How to Use

### Step 1: Upload LinkedIn Data
1. Export your LinkedIn connections as CSV from LinkedIn Settings
2. Drag & drop or browse to upload the file
3. System automatically parses and identifies new connections
4. Background enrichment begins for new profiles (configurable limit)
5. Real-time progress tracking with vectorization updates

### Step 2: Track Enrichment Progress
- Real-time progress bar shows enrichment status
- Parallel processing with configurable concurrency limits
- Vectorization catch-up for semantic search preparation
- System caches enriched data to avoid re-processing

### Step 3: Get AI Recommendations
1. Describe your business mission or goal in the text area
2. Click "Get AI Suggestions" 
3. AI extracts mission attributes (industry, location, role)
4. Semantic search finds relevant connections using vector similarity
5. Receive top 4 most relevant connections with detailed reasoning

### Step 4: Generate Personalized Messages
1. Click "Generate Message" on any suggested connection
2. AI creates personalized LinkedIn outreach message
3. Edit message as needed in the modal
4. Copy to clipboard or open LinkedIn profile directly
5. Send personalized reconnection message

---

## 🔧 Configuration

### Enrichment Settings (backend/config/settings.py)
- **NUMBER_OF_ENRICHMENTS**: Max profiles to enrich per upload (default: 10)
- **RATE_LIMIT_SLEEP_SECONDS**: Delay between API calls (default: 1)
- **MAX_CONCURRENT_REQUESTS**: Parallel processing limit (default: 10)
- **CHROMA_PERSIST_PATH**: ChromaDB storage location

### Semantic Search Configuration
- **Embedding Model**: all-mpnet-base-v2 (768 dimensions)
- **Search Attributes**: summary, position, location, industry
- **Similarity Metric**: Cosine similarity
- **Top-K Results**: Configurable result limits

### API Endpoints
- `POST /upload-csv` - Upload and process LinkedIn connections
- `GET /enrichment-progress` - Real-time enrichment progress
- `POST /get-suggestions` - Get AI-powered connection recommendations  
- `POST /generate-message` - Generate personalized outreach messages
- `GET /` - Health check

---

## 📄 License

MIT License - See LICENSE file for details