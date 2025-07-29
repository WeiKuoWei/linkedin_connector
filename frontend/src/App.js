import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';
const ENRICHMENT_SECONDS_PER_PROFILE = 5; // seconds per enrichment (should match backend config)

function App() {
  const [file, setFile] = useState(null);
  const [connectionsParsed, setConnectionsParsed] = useState(false);
  const [connectionsCount, setConnectionsCount] = useState(0);
  const [mission, setMission] = useState('');
  const [suggestions, setSuggestions] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Progress tracking
  const [enrichmentProgress, setEnrichmentProgress] = useState(null);
  const [realTimeProgress, setRealTimeProgress] = useState(null);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a CSV file');
    }
  };

  const uploadFile = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploadLoading(true);
    setError('');
    setEnrichmentProgress(null);
    setRealTimeProgress(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Upload the file and start background enrichment
      const response = await axios.post(`${API_BASE}/upload-csv`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      // Set basic connection info immediately
      setConnectionsParsed(true);
      setConnectionsCount(response.data.count);
      
      // If enrichment was started, begin polling for progress
      if (response.data.enrichment_started && response.data.will_enrich > 0) {
        setRealTimeProgress({ current: 0, total: response.data.will_enrich });
        
        // Poll for progress updates
        const pollProgress = setInterval(async () => {
          try {
            const progressResponse = await axios.get(`${API_BASE}/enrichment-progress`);
            const { current, total, completed, in_progress } = progressResponse.data;
            
            // Only update if enrichment is actually in progress
            if (in_progress || !completed) {
              setRealTimeProgress({ current, total });
            }
            
            if (completed && !in_progress) {
              clearInterval(pollProgress);
              setRealTimeProgress(null);
              
              // Show completion message
              setEnrichmentProgress({
                enriched: response.data.will_enrich,
                total: response.data.total_enriched + response.data.will_enrich
              });
              
              console.log(`Enrichment completed! ${response.data.will_enrich} profiles were enriched.`);
            }
          } catch (err) {
            clearInterval(pollProgress);
            console.error('Error polling progress:', err);
            setRealTimeProgress(null);
          }
        }, 1000); // Poll every second
        
        // Fallback timeout to prevent infinite polling
        setTimeout(() => {
          clearInterval(pollProgress);
          setRealTimeProgress(null);
          setEnrichmentProgress({
            enriched: response.data.will_enrich,
            total: response.data.total_enriched + response.data.will_enrich
          });
        }, 60000); // 1 minute timeout
      } else {
        // No enrichment needed
        if (response.data.total_enriched > 0) {
          setEnrichmentProgress({
            enriched: 0, // No new enrichments
            total: response.data.total_enriched
          });
        }
      }
      
    } catch (err) {
      setError('Failed to upload file: ' + (err.response?.data?.detail || err.message));
    }
    setUploadLoading(false);
  };

  const getSuggestions = async () => {
    if (!mission.trim()) {
      setError('Please enter your mission first');
      return;
    }
    
    setSuggestionsLoading(true);
    setError('');
    setSuggestions(null);
    
    try {
      const response = await axios.post(`${API_BASE}/get-suggestions`, {
        mission: mission
      });
      setSuggestions(response.data);
    } catch (err) {
      setError('Failed to get suggestions: ' + (err.response?.data?.detail || err.message));
    }
    setSuggestionsLoading(false);
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
            {/* Step 1: Upload File */}
            <div className="border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Step 1: Upload LinkedIn Connections</h2>
              <p className="text-gray-600 mb-4">
                Upload your LinkedIn connections CSV file (exported from LinkedIn).
              </p>
              
              {/* File Drop Zone */}
              <div 
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  file 
                    ? 'border-green-400 bg-green-50' 
                    : 'border-gray-300 hover:border-gray-400 bg-gray-50'
                }`}
                onDrop={(e) => {
                  e.preventDefault();
                  const droppedFile = e.dataTransfer.files[0];
                  handleFileSelect(droppedFile);
                }}
                onDragOver={(e) => e.preventDefault()}
              >
                {file ? (
                  <div className="text-green-700">
                    <svg className="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm">Ready to upload</p>
                  </div>
                ) : (
                  <div className="text-gray-500">
                    <svg className="mx-auto h-12 w-12 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                      <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    <p className="mb-2">Drop your CSV file here, or</p>
                    <label className="cursor-pointer">
                      <span className="text-blue-500 hover:text-blue-600 font-medium">browse files</span>
                      <input
                        type="file"
                        accept=".csv"
                        onChange={(e) => handleFileSelect(e.target.files[0])}
                        className="hidden"
                      />
                    </label>
                  </div>
                )}
              </div>
              
              <button
                onClick={uploadFile}
                disabled={!file || uploadLoading}
                className={`mt-4 px-6 py-2 rounded-lg font-medium ${
                  !file || uploadLoading
                    ? 'bg-gray-300 text-gray-500' 
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                {uploadLoading ? 'Processing...' : 'Upload & Parse'}
              </button>

              {/* Connection Count Display */}
              {connectionsParsed && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
                  <p className="text-sm text-green-700">
                    ✓ Successfully loaded {connectionsCount} connections
                  </p>
                </div>
              )}

              {/* Real-time Progress Bar */}
              {realTimeProgress && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-blue-700">
                      Enriching LinkedIn profiles...
                    </p>
                    <p className="text-sm text-blue-600">
                      {realTimeProgress.current}/{realTimeProgress.total}
                    </p>
                  </div>
                  <div className="w-full bg-blue-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${Math.min((realTimeProgress.current / realTimeProgress.total) * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                  <p className="text-xs text-blue-600 mt-1">
                    Each take up to {realTimeProgress.total * ENRICHMENT_SECONDS_PER_PROFILE} seconds...
                  </p>
                </div>
              )}

              {/* Static Enrichment Results */}
              {enrichmentProgress && !realTimeProgress && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-sm text-blue-700">
                    {enrichmentProgress.enriched > 0 
                      ? `✨ Enriched ${enrichmentProgress.enriched} new profiles with LinkedIn data.`
                      : `📊 Using ${enrichmentProgress.total} previously enriched profiles.`
                    } Total enriched: {enrichmentProgress.total}
                  </p>
                </div>
              )}
            </div>

            {/* Step 2: Mission & Suggestions */}
            <div className="border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Step 2: Describe Your Mission & Get Suggestions</h2>
              <textarea
                value={mission}
                onChange={(e) => setMission(e.target.value)}
                placeholder="e.g., I'm expanding my logistics business into Brazil and looking for reliable partners or advisors who know the local market."
                className="w-full p-3 border border-gray-300 rounded-lg h-24 resize-none mb-4"
                disabled={suggestionsLoading}
              />
              
              <button
                onClick={getSuggestions}
                disabled={suggestionsLoading || !connectionsParsed}
                className={`px-6 py-2 rounded-lg font-medium ${
                  !connectionsParsed 
                    ? 'bg-gray-300 text-gray-500' 
                    : suggestionsLoading 
                      ? 'bg-gray-300 text-gray-500' 
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                {suggestionsLoading ? 'Getting Suggestions...' : 'Get AI Suggestions'}
              </button>
            </div>

            {/* Results */}
            {suggestions && (
              <div className="border rounded-lg p-6 bg-blue-50">
                <h2 className="text-xl font-semibold mb-4">Suggestions</h2>
                <div className="bg-white p-4 rounded border">
                  {/* <h3 className="font-medium mb-2">Mission:</h3>
                  <p className="text-gray-700 mb-4">{suggestions.mission}</p>
                  
                  <h3 className="font-medium mb-4">Suggestions:</h3>
                   */}
                  {/* Format suggestions properly if it's an array */}
                  {Array.isArray(suggestions.suggestions) ? (
                    <div className="space-y-4">
                      {suggestions.suggestions.map((suggestion, index) => (
                        <div key={index} className="bg-gray-50 p-4 rounded border-l-4 border-blue-500">
                          <h4 className="font-semibold text-lg text-gray-900 mb-1">
                            {suggestion.name}
                          </h4>
                          <p className="text-blue-700 font-medium mb-2">
                            {suggestion.role} at {suggestion.company}
                          </p>
                          <div className="mb-2">
                            <span className="font-medium text-gray-700">Why they're relevant:</span>
                            <p className="text-gray-600 mt-1">{suggestion.reasoning}</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">How they can help:</span>
                            <p className="text-gray-600 mt-1">{suggestion.how_they_help}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-3 rounded">
                      {typeof suggestions.suggestions === 'string' 
                        ? suggestions.suggestions 
                        : JSON.stringify(suggestions.suggestions, null, 2)}
                    </pre>
                  )}
                  
                  <p className="text-sm text-gray-500 mt-4">
                    Based on {suggestions.total_connections} total connections 
                    ({suggestions.enriched_connections} enriched with LinkedIn data)
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