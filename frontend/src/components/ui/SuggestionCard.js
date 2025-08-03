import React from 'react';

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