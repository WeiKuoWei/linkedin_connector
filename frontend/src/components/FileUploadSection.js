import React from 'react';
import { FileUploadZone, ProgressBar, StatusMessage } from './index';

const FileUploadSection = ({
  file,
  onFileSelect,
  onUpload,
  uploadLoading,
  connectionsParsed,
  connectionsCount,
  enrichmentProgress,
  realTimeProgress
}) => {
  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Step 1: Upload LinkedIn Connections</h2>
      <p className="text-gray-600 mb-4">
        Upload your LinkedIn connections CSV file (exported from LinkedIn).
      </p>
      
      <FileUploadZone file={file} onFileSelect={onFileSelect} />
      
      <button
        onClick={onUpload}
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
  );
};

export default FileUploadSection;