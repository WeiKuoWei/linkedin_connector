# 📎 LinkedIn Weak Ties AI Chatbot

An AI-powered full-stack application that helps business professionals leverage their *weak ties* on LinkedIn. Upload your LinkedIn connections and get intelligent recommendations for specific business goals using enriched profile data and AI-powered matching.

---

## 🚀 Key Features

* **Smart CSV Import**: Upload LinkedIn `connections.csv` with automatic parsing
* **Profile Enrichment**: Automatically enriches LinkedIn profiles with detailed data (summary, location, industry, company size)
* **Incremental Processing**: Only processes new connections to minimize API costs
* **Real-time Progress**: Live progress tracking during profile enrichment
* **AI-Powered Matching**: GPT-4 analyzes enriched profiles against your mission
* **Intelligent Reasoning**: Detailed explanations for each recommendation
* **Background Processing**: Non-blocking profile enrichment
* **Caching System**: Efficient storage of enriched data

---

## 🛠️ Technology Stack

### Frontend
* **React.js** - Component-based UI with hooks
* **Tailwind CSS** - Utility-first styling
* **Axios** - HTTP client for API communication
* **Real-time polling** - Progress updates during enrichment

### Backend
* **FastAPI** - High-performance Python API framework
* **Pandas** - CSV processing and data manipulation
* **Azure OpenAI (GPT-4)** - AI-powered connection matching
* **RapidAPI LinkedIn Scraper** - Profile enrichment service
* **Async/Background Tasks** - Non-blocking profile processing
* **JSON caching** - Efficient data storage

---

## 📂 Project Structure

```
linkedin-ai-chatbot/
├── README.md
├── .gitignore
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js           # Main React component
│   │   ├── index.js         # App entry point
│   │   └── index.css        # Tailwind imports
│   └── package.json
│
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── data/
│   │   ├── connections.json         # Raw connections
│   │   └── connections_enriched.json # Enriched cache
│   └── .env                 # Environment variables
```

---

## ⚙️ Setup & Installation

### Prerequisites
* Python 3.8+
* Node.js 16+ 
* npm or yarn
* LinkedIn connections CSV export

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
AZURE_OPENAI_ENDPOINT=YOUR_ENDPOINT
AZURE_OPENAI_API_KEY=YOUR_KEY
RAPIDAPI_KEY=YOUR_KEY
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
npm start
```
Frontend runs on: http://localhost:3000

---

## 💡 How to Use

### Step 1: Upload LinkedIn Data
1. Export your LinkedIn connections as CSV
2. Drag & drop or browse to upload the file
3. System automatically parses and identifies new connections
4. Background enrichment begins for new profiles (up to 5 profiles)

### Step 2: Track Enrichment Progress
- Real-time progress bar shows enrichment status
- Each profile takes ~5 seconds to enrich
- System caches enriched data to avoid re-processing

### Step 3: Get AI Recommendations
1. Describe your business mission/goal
2. Click "Get AI Suggestions"
3. Receive top 4 most relevant connections with detailed reasoning
4. Each suggestion includes why they're relevant and how they can help

---

## 🏗️ Architecture Highlights

### Smart Enrichment System
- **Incremental Processing**: Only enriches new connections
- **URL-based Caching**: Efficient storage using LinkedIn URLs as keys
- **Rate Limiting**: Respects API limits with 1-second delays
- **Background Tasks**: Non-blocking async processing

### AI-Powered Matching
- **Enhanced Prompts**: Uses enriched profile data (not just basic CSV)
- **Structured Output**: Consistent JSON responses from GPT-4
- **Context-Aware**: Considers location, industry, company size, summaries
- **Detailed Reasoning**: Specific explanations for each match

### Real-time Experience
- **Progress Polling**: Live updates during enrichment
- **Immediate Feedback**: Instant connection count display
- **Error Handling**: Comprehensive validation and error messages
- **Responsive Design**: Clean, professional interface

---

## 🔧 Configuration

### Enrichment Settings
- **NUMBER_OF_ENRICHMENTS**: Max profiles to enrich per upload (default: 5)
- **RATE_LIMIT_SLEEP_SECONDS**: Delay between API calls (default: 1)

### API Endpoints
- `POST /upload-csv` - Upload and process LinkedIn connections
- `POST /get-suggestions` - Get AI-powered connection recommendations
- `GET /enrichment-progress` - Real-time enrichment progress
- `GET /` - Health check

---

## 📈 Future Enhancements

* **Database Integration**: Replace JSON files with PostgreSQL/MongoDB
* **Batch Enrichment**: Process larger connection lists
* **Advanced Filtering**: Filter by location, industry, company size
* **Custom Prompts**: User-defined matching criteria
* **Email Integration**: Direct outreach templates
* **Analytics Dashboard**: Connection analysis and insights
* **Team Collaboration**: Shared connection pools
* **Mobile App**: Native mobile experience

---

## 🔒 Privacy & Security

* All LinkedIn data processed locally
* No data sent to third parties except for enrichment APIs
* Environment variables for sensitive API keys
* Rate limiting to respect LinkedIn's terms
* Local caching minimizes external API calls

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request