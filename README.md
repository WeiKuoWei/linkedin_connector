Here is your content reformatted in clean, organized **Markdown**:

---

# 📎 LinkedIn Weak Ties AI Chatbot MVP

This project is a **Minimum Viable Product (MVP)** for an AI-powered chatbot that helps business professionals leverage their *weak ties* on LinkedIn. It identifies relevant connections for specific business goals (e.g., market expansion) using AI-powered reasoning based on LinkedIn data.

---

## 🚀 Features

* **LinkedIn Data Import**: Upload your `connections.csv` from LinkedIn.
* **Mission Description**: Describe your business goal or mission.
* **AI-Powered Suggestions**: Get recommended LinkedIn connections based on your mission.
* **Reasoning**: See why each connection was recommended.
* **Reconnect Link**: Simulate navigating to the LinkedIn profile.
* **Local Data Storage**: LinkedIn data is locally parsed and stored for this MVP.

---

## 🛠️ Technologies Used

### Frontend

* **React.js**: Component-based JavaScript UI library.
* **HTML5**: Base markup language.
* **Tailwind CSS**: Utility-first CSS framework for design.

### Backend

* **Python 3.x**: Core backend language.
* **FastAPI**: High-performance API framework.
* **Pandas**: CSV parsing and data analysis.
* **python-dotenv**: Manage environment variables.
* **httpx / requests**: Make external HTTP requests.

### External Services

* **Azure AI (GPT-4o)**: Used for generating semantic suggestions and reasoning.

---

## 📂 Directory Structure

```
linkedin-ai-chatbot-mvp/
├── .gitignore
├── README.md
│
├── frontend/              
│   ├── public/            
│   │   └── index.html
│   ├── src/               
│   │   ├── App.js         
│   │   ├── index.js       
│   │   └── components/    
│   ├── package.json       
│   ├── package-lock.json  
│   └── tailwind.config.js 
│
├── backend/               
│   ├── main.py
│   ├── requirements.txt
│   ├── data/
│   │   └── connections.json 
│   └── .env               
│
└── .env  # Optional project-wide config
```

---

## ⚙️ Setup Instructions

### ✅ Prerequisites

Make sure the following are installed:

* Python 3.8+
* `pip` (Python package manager)
* Node.js (LTS recommended)
* `npm` or `yarn`
* A modern browser (e.g., Chrome, Firefox)

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/linkedin-ai-chatbot-mvp.git
cd linkedin-ai-chatbot-mvp
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

#### Add Environment Variables

Create a `.env` file in `backend/`:

```env
AZURE_OPENAI_ENDPOINT="https://gateway.ai.cloudflare.com/v1/..."
AZURE_OPENAI_API_KEY="YOUR_AZURE_AI_API_KEY_HERE"
```

> ⚠️ **Do not commit `.env`** — it's already in `.gitignore`.

---

### 3. Frontend Setup

```bash
cd ../frontend
npm install  # or yarn install
```

Ensure `tailwind.config.js` includes:

```js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

---

## 🚀 How to Run

### Start Backend (FastAPI)

```bash
cd backend
source venv/bin/activate  # or activate on Windows
uvicorn main:app --reload
```

> Server usually runs on: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### Start Frontend (React)

```bash
cd frontend
npm start  # or yarn start
```

> App will launch on: [http://localhost:3000](http://localhost:3000)

---

## 💡 Usage

1. **Upload CSV**: Click "Upload LinkedIn Connections CSV" and select your `connections.csv` file.
2. **Describe Mission**: Enter your business objective (e.g., market expansion).
3. **Get Suggestions**: Click "Get Suggestions" to receive AI-generated recommendations.
4. **Reconnect**: Click "Reconnect" next to a suggestion to simulate profile navigation.

---

## ✨ Future Enhancements

* **Persistent Database**: Replace local storage with PostgreSQL, MongoDB, or Firestore.
* **Advanced AI Prompting**: Refined prompts for better suggestions.
* **Semantic Search**: Improved AI matching with vector-based search.
* **User Authentication**: Beyond the current MVP.
* **Robust Error Handling**: Better feedback and fault tolerance.
* **Enhanced UI/UX**: Improve visual design and interaction flow.

---

## 📄 License

This project is licensed under the **MIT License**. See `LICENSE` for full details.

---

Let me know if you'd like a PDF or `.md` file version!
