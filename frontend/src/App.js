import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './pages/LandingPage';
import ProtectedRoute from './components/ProtectedRoute';
import { getSuggestions } from './services/api';
import { 
  FileUploadSection,
  MissionSection,
  SuggestionsSection,
  MessageModal,
  ErrorMessage 
} from './components';
import { useFileUpload, useMessageGeneration } from './hooks';

// Main Dashboard Component (the original App content)
function Dashboard() {
  const [mission, setMission] = useState('');
  const [suggestions, setSuggestions] = useState(null);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [error, setError] = useState('');
  const { user, signOut } = useAuth();

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
    <div className="min-h-screen bg-gray-50">
      {/* Header with User Info and Logout */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            LinkedIn AI Chatbot
          </h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              Welcome, {user?.email}
            </span>
            <button
              onClick={signOut}
              className="px-4 py-2 text-sm bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
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
    </div>
  );
}

// App Router Component
function AppRouter() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route 
        path="/" 
        element={user ? <Navigate to="/dashboard" replace /> : <LandingPage />} 
      />
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// Main App Component
function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </Router>
  );
}

export default App;