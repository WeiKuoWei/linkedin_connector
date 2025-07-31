import React from 'react';

const SuggestionsSection = ({ suggestions, onGenerateMessage, onOpenLinkedInProfile }) => {
  if (!suggestions) return null;

  return (
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
                    onClick={() => onGenerateMessage(suggestion)} 
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
                  >
                    📧 Generate Message
                  </button>
                  <button
                    onClick={() => onOpenLinkedInProfile(suggestion.linkedin_url)}
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
  );
};

export default SuggestionsSection;