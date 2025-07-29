import React, { useState } from 'react';
import { uploadFile, getEnrichmentProgress, getSuggestions } from './api';
import { 
  FileUploadZone, 
  ProgressBar, 
  StatusMessage, 
  SuggestionCard, 
  ErrorMessage 
} from './components';

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

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploadLoading(true);
    setError('');
    setEnrichmentProgress(null);
    setRealTimeProgress(null);

    try {
      const response = await uploadFile(file);
      
      // Set basic connection info immediately
      setConnectionsParsed(true);
      setConnectionsCount(response.count);
      
      // If enrichment was started, begin polling for progress
      if (response.enrichment_started && response.will_enrich > 0) {
        setRealTimeProgress({ current: 0, total: response.will_enrich });
        
        // Poll for progress updates
        const pollProgress = setInterval(async () => {
          try {
            const progressData = await getEnrichmentProgress();
            const { current, total, completed, in_progress } = progressData;
            
            // Only update if enrichment is actually in progress
            if (in_progress || !completed) {
              setRealTimeProgress({ current, total });
            }
            
            if (completed && !in_progress) {
              clearInterval(pollProgress);
              setRealTimeProgress(null);
              
              // Show completion message
              setEnrichmentProgress({
                enriched: response.will_enrich,
                total: response.total_enriched + response.will_enrich
              });
              
              console.log(`Enrichment completed! ${response.will_enrich} profiles were enriched.`);
            }
          } catch (err) {
            clearInterval(pollProgress);
            console.error('Error polling progress:', err);
            setRealTimeProgress(null);
          }
        }, 5000); // Poll every second
        
        // Fallback timeout to prevent infinite polling
        setTimeout(() => {
          clearInterval(pollProgress);
          setRealTimeProgress(null);
          setEnrichmentProgress({
            enriched: response.will_enrich,
            total: response.total_enriched + response.will_enrich
          });
        }, 60000); // 1 minute timeout
      } else {
        // No enrichment needed
        if (response.total_enriched > 0) {
          setEnrichmentProgress({
            enriched: 0, // No new enrichments
            total: response.total_enriched
          });
        }
      }
      
    } catch (err) {
      setError('Failed to upload file: ' + (err.response?.data?.detail || err.message));
    }
    setUploadLoading(false);
  };

  const handleGetSuggestions = async () => {
    if (!mission.trim()) {
      setError('Please enter your mission first');
      return;
    }
    
    setSuggestionsLoading(true);
    setError('');
    setSuggestions(null);
    
    try {
      const response = await getSuggestions(mission);
      setSuggestions(response);
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
          
          <ErrorMessage error={error} />

          <div className="space-y-6">
            {/* Step 1: Upload File */}
            <div className="border rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Step 1: Upload LinkedIn Connections</h2>
              <p className="text-gray-600 mb-4">
                Upload your LinkedIn connections CSV file (exported from LinkedIn).
              </p>
              
              <FileUploadZone file={file} onFileSelect={handleFileSelect} />
              
              <button
                onClick={handleUpload}
                disabled={!file || uploadLoading}
                className={`mt-4 px-6 py-2 rounded-lg font-medium ${
                  !file || uploadLoading
                    ? 'bg-gray-300 text-gray-500' 
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                {uploadLoading ? 'Processing...' : 'Upload & Parse'}
              </button>

              <StatusMessage 
                connectionsParsed={connectionsParsed}
                connectionsCount={connectionsCount}
                enrichmentProgress={enrichmentProgress}
                realTimeProgress={realTimeProgress}
              />

              {realTimeProgress && <ProgressBar realTimeProgress={realTimeProgress} />}
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
                onClick={handleGetSuggestions}
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
                  {Array.isArray(suggestions.suggestions) ? (
                    <div className="space-y-4">
                      {suggestions.suggestions.map((suggestion, index) => (
                        <SuggestionCard key={index} suggestion={suggestion} index={index} />
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