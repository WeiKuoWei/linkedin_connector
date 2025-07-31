import React, { useState } from 'react';
import { getSuggestions } from './services/api';
import { 
  FileUploadSection,
  MissionSection,
  SuggestionsSection,
  MessageModal,
  ErrorMessage 
} from './components';
import { useFileUpload, useMessageGeneration } from './hooks';

function App() {
  const [mission, setMission] = useState('');
  const [suggestions, setSuggestions] = useState(null);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [error, setError] = useState('');

  // Custom hooks
  const {
    file,
    connectionsParsed,
    connectionsCount,
    uploadLoading,
    enrichmentProgress,
    realTimeProgress,
    handleFileSelect,
    handleUpload,
    resetFile
  } = useFileUpload();

  const {
    showMessageModal,
    setShowMessageModal,
    selectedConnection,
    generatedMessage,
    setGeneratedMessage,
    messageLoading,
    copied,
    handleGenerateMessage,
    copyToClipboard,
    openLinkedInProfile
  } = useMessageGeneration();

  // Handle file upload with error handling
  const onFileSelect = (selectedFile) => {
    const error = handleFileSelect(selectedFile);
    setError(error || '');
  };

  const onUpload = async () => {
    const error = await handleUpload();
    setError(error || '');
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

  const onGenerateMessage = (suggestion) => {
    handleGenerateMessage(suggestion, mission);
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
            <FileUploadSection
              file={file}
              onFileSelect={onFileSelect}
              onUpload={onUpload}
              onRemove={resetFile} 
              uploadLoading={uploadLoading}
              connectionsParsed={connectionsParsed}
              connectionsCount={connectionsCount}
              enrichmentProgress={enrichmentProgress}
              realTimeProgress={realTimeProgress}
            />

            {/* Step 2: Mission & Suggestions */}
            <MissionSection
              mission={mission}
              onMissionChange={setMission}
              onGetSuggestions={handleGetSuggestions}
              suggestionsLoading={suggestionsLoading}
              connectionsParsed={connectionsParsed}
            />

            {/* Results */}
            <SuggestionsSection
              suggestions={suggestions}
              onGenerateMessage={onGenerateMessage}
              onOpenLinkedInProfile={openLinkedInProfile}
            />

            {/* Message Generation Modal */}
            <MessageModal
            show={showMessageModal}
            onClose={() => setShowMessageModal(false)}
            selectedConnection={selectedConnection}
            generatedMessage={generatedMessage}
            onMessageChange={setGeneratedMessage}
            messageLoading={messageLoading}
            onCopyToClipboard={copyToClipboard}
            onOpenLinkedInProfile={openLinkedInProfile}
            copied={copied}
          />
          
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;