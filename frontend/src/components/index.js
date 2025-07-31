import React from 'react';
import { ENRICHMENT_SECONDS_PER_PROFILE, MAX_CONCURRENT_REQUESTS } from '../services/constants';

export const FileUploadZone = ({ file, onFileSelect }) => (
  <div 
    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
      file 
        ? 'border-green-400 bg-green-50' 
        : 'border-gray-300 hover:border-gray-400 bg-gray-50'
    }`}
    onDrop={(e) => {
      e.preventDefault();
      const droppedFile = e.dataTransfer.files[0];
      onFileSelect(droppedFile);
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
            onChange={(e) => onFileSelect(e.target.files[0])}
            className="hidden"
          />
        </label>
      </div>
    )}
  </div>
);

export const ProgressBar = ({ realTimeProgress }) => {
  const processingTime = realTimeProgress.total > MAX_CONCURRENT_REQUESTS 
  ? realTimeProgress.total * ENRICHMENT_SECONDS_PER_PROFILE / MAX_CONCURRENT_REQUESTS 
  : realTimeProgress.total * ENRICHMENT_SECONDS_PER_PROFILE;

  return (
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
        Takes up to {processingTime.toFixed(0)} seconds to process...
      </p>
    </div>
  );
}
    

export const StatusMessage = ({ connectionsParsed, connectionsCount, enrichmentProgress, realTimeProgress }) => {
  // Show enrichment progress first (higher priority)
  if (enrichmentProgress && !realTimeProgress) {
    return (
      <>
      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
        <p className="text-sm text-green-700">
          ✓ Successfully loaded {connectionsCount} connections
        </p>
      </div>
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
        <p className="text-sm text-blue-700">
          {enrichmentProgress.enriched > 0 
            ? `✨ Enriched ${enrichmentProgress.enriched} new profiles with LinkedIn data.`
            : `📊 Using ${enrichmentProgress.total} previously enriched profiles.`
          } Total enriched: {enrichmentProgress.total}
        </p>
        {enrichmentProgress.needs_vectorization > 0 && (
          <p className="text-sm text-blue-600 mt-1">
            🔄 Vectorizing {enrichmentProgress.needs_vectorization} profiles for semantic search...
          </p>
        )}
      </div>
      </>
    );
  }

  // Show basic connection count if no enrichment info available
  if (connectionsParsed && !realTimeProgress && !enrichmentProgress) {
    return (
      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
        <p className="text-sm text-green-700">
          ✓ Successfully loaded {connectionsCount} connections
        </p>
      </div>
    );
  }

  return null;
};

export const SuggestionCard = ({ suggestion, index }) => (
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
);

export const ErrorMessage = ({ error }) => error ? (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
    {error}
  </div>
) : null;

export { default as FileUploadSection } from './FileUploadSection';
export { default as MissionSection } from './MissionSection';
export { default as SuggestionsSection } from './SuggestionsSection';
export { default as MessageModal } from './MessageModal';