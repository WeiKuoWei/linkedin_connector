import React, { useState } from 'react';
import { uploadFile, getEnrichmentProgress, getSuggestions, generateMessage } from './api';
import { 
  FileUploadZone, 
  ProgressBar, 
  StatusMessage, 
  // SuggestionCard, 
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

  // Message generation
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [generatedMessage, setGeneratedMessage] = useState('');
  const [messageLoading, setMessageLoading] = useState(false);
  const [copied, setCopied] = useState(false);

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
            total: response.total_enriched + response.will_enrich,
            needs_vectorization: response.needs_vectorization || 0
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

  const handleGenerateMessage = async (suggestion) => {
    setSelectedConnection(suggestion);
    setShowMessageModal(true);
    setMessageLoading(true);
    setGeneratedMessage('');
    
    try {
      const response = await generateMessage({
        name: suggestion.name,
        company: suggestion.company,
        role: suggestion.role,
        mission: mission,
        profile_summary: suggestion.profile_summary || '',
        location: suggestion.location || ''
      });
      
      setGeneratedMessage(response.message);
    } catch (err) {
      setGeneratedMessage('Error generating message. Please try again.');
      console.error('Error generating message:', err);
    }
    setMessageLoading(false);
  };

    const copyToClipboard = (text) => {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000); // Reset after 3 seconds
    };

    const openLinkedInProfile = (url) => {
      if (url) {
        window.open(url, '_blank');
      }
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
                        <div key={index} className="bg-gray-50 p-4 rounded border-l-4 border-blue-500">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h4 className="font-semibold text-lg text-gray-900 mb-1">
                                {suggestion.name}
                              </h4>
                              <p className="text-blue-700 font-medium mb-2">
                                {suggestion.role} at {suggestion.company}
                              </p>
                              {suggestion.location && (
                                <p className="text-sm text-gray-500 mb-2">📍 {suggestion.location}</p>
                              )}
                              {/* <div className="flex items-center mb-2">
                                <span className="text-sm text-gray-600">Connection Strength:</span>
                                <span className="ml-2 text-sm font-medium text-yellow-600">
                                  ⭐⭐⭐ {suggestion.connection_strength || 'Medium'}
                                </span>
                              </div> */}
                            </div>
                          </div>
                          
                          <div className="mb-2">
                            <span className="font-medium text-gray-700">Why they're relevant:</span>
                            <p className="text-gray-600 mt-1">{suggestion.reasoning}</p>
                          </div>
                          <div className="mb-4">
                            <span className="font-medium text-gray-700">How they can help:</span>
                            <p className="text-gray-600 mt-1">{suggestion.how_they_help}</p>
                          </div>
                          
                          {/* Action Buttons */}
                          <div className="flex gap-3">
                            <button
                              onClick={() => handleGenerateMessage(suggestion)} 
                              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
                            >
                              📧 Generate Message
                            </button>
                            <button
                              onClick={() => openLinkedInProfile(suggestion.linkedin_url)}
                              disabled={!suggestion.linkedin_url}
                              className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                                suggestion.linkedin_url 
                                  ? 'bg-blue-700 text-white hover:bg-blue-800' 
                                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              }`}
                            >
                              🔗 View LinkedIn Profile
                            </button>
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
            {/* Message Generation Modal */}
            {showMessageModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-semibold">
                      📧 Message for {selectedConnection?.name}
                    </h3>
                    <button
                      onClick={() => setShowMessageModal(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ✕
                    </button>
                  </div>
                  
                  {selectedConnection && (
                    <div className="mb-4 p-3 bg-gray-50 rounded">
                      <p className="text-sm text-gray-600">
                        <strong>{selectedConnection.role}</strong> at <strong>{selectedConnection.company}</strong>
                        {selectedConnection.location && ` • ${selectedConnection.location}`}
                      </p>
                    </div>
                  )}
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Generated Message:
                    </label>
                    {messageLoading ? (
                      <div className="p-4 bg-gray-50 rounded border">
                        <p className="text-gray-500">Generating personalized message...</p>
                      </div>
                    ) : (
                      <textarea
                        value={generatedMessage}
                        onChange={(e) => setGeneratedMessage(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg h-48 resize-none"
                        placeholder="Your personalized message will appear here..."
                      />
                    )}
                  </div>
                  
                  <div className="flex gap-3">
                    <button
                      onClick={() => copyToClipboard(generatedMessage)}
                      disabled={!generatedMessage || messageLoading}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        generatedMessage && !messageLoading
                          ? 'bg-green-500 text-white hover:bg-green-600'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      {copied ? '✅ Copied to Clipboard!' : '📋 Copy to Clipboard'}
                    </button>
                    <button
                      onClick={() => openLinkedInProfile(selectedConnection?.linkedin_url)}
                      disabled={!selectedConnection?.linkedin_url}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        selectedConnection?.linkedin_url
                          ? 'bg-blue-700 text-white hover:bg-blue-800'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      🔗 Open LinkedIn to Send
                    </button>
                    <button
                      onClick={() => setShowMessageModal(false)}
                      className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                    >
                      Close
                    </button>
                  </div>
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