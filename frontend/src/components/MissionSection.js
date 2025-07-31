import React from 'react';

const MissionSection = ({
  mission,
  onMissionChange,
  onGetSuggestions,
  suggestionsLoading,
  connectionsParsed
}) => {
  return (
    <div className="border rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Step 2: Describe Your Mission & Get Suggestions</h2>
      <textarea
        value={mission}
        onChange={(e) => onMissionChange(e.target.value)}
        placeholder="e.g., I'm expanding my logistics business into Brazil and looking for reliable partners or advisors who know the local market."
        className="w-full p-3 border border-gray-300 rounded-lg h-24 resize-none mb-4"
        disabled={suggestionsLoading}
      />
      
      <button
        onClick={onGetSuggestions}
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
  );
};

export default MissionSection;