import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [connectionsParsed, setConnectionsParsed] = useState(false);
  const [mission, setMission] = useState('');
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const parseConnections = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_BASE}/parse-connections`);
      setConnectionsParsed(true);
      alert(`Successfully parsed ${response.data.count} connections!`);
    } catch (err) {
      setError('Failed to parse connections: ' + err.message);
    }
    setLoading(false);
  };

  const getSuggestions = async () => {
    if (!mission.trim()) {
      setError('Please enter your mission first');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuggestions(null);
    
    try {
      const response = await axios.post(`${API_BASE}/get-suggestions`, {
        mission: mission
      });
      setSuggestions(response.data);
    } catch (err) {
      setError('Failed to get suggestions: ' + err.message);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            LinkedIn AI Weak Ties Chatbot
          </h1>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          <div className="space-y-6">
            {/* Step 1: Parse Connections */}
            <div className="border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Step 1: Load LinkedIn Connections</h2>
              <p className="text-gray-600 mb-4">
                Parse your LinkedIn connections from the CSV file in the data folder.
              </p>
              <button
                onClick={parseConnections}
                disabled={loading || connectionsParsed}
                className={`px-6 py-2 rounded-lg font-medium ${
                  connectionsParsed 
                    ? 'bg-green-500 text-white' 
                    : loading 
                      ? 'bg-gray-300 text-gray-500' 
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                {loading ? 'Parsing...' : connectionsParsed ? ' Connections Loaded' : 'Parse Connections'}
              </button>
            </div>

            {/* Step 2: Enter Mission */}
            <div className="border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Step 2: Describe Your Mission</h2>
              <textarea
                value={mission}
                onChange={(e) => setMission(e.target.value)}
                placeholder="e.g., I'm expanding my logistics business into Brazil and looking for reliable partners or advisors who know the local market."
                className="w-full p-3 border border-gray-300 rounded-lg h-24 resize-none"
                disabled={loading}
              />
            </div>

            {/* Step 3: Get Suggestions */}
            <div className="border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Step 3: Get AI Suggestions</h2>
              <button
                onClick={getSuggestions}
                disabled={loading || !connectionsParsed}
                className={`px-6 py-2 rounded-lg font-medium ${
                  !connectionsParsed 
                    ? 'bg-gray-300 text-gray-500' 
                    : loading 
                      ? 'bg-gray-300 text-gray-500' 
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                {loading ? 'Getting Suggestions...' : 'Get Suggestions'}
              </button>
            </div>

            {/* Results */}
            {suggestions && (
              <div className="border rounded-lg p-6 bg-blue-50">
                <h2 className="text-xl font-semibold mb-4">AI Suggestions</h2>
                <div className="bg-white p-4 rounded border">
                  <h3 className="font-medium mb-2">Mission:</h3>
                  <p className="text-gray-700 mb-4">{suggestions.mission}</p>
                  
                  <h3 className="font-medium mb-2">Suggestions:</h3>
                  <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-3 rounded">
                    {suggestions.suggestions}
                  </pre>
                  
                  <p className="text-sm text-gray-500 mt-4">
                    Based on {suggestions.total_connections} total connections
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;