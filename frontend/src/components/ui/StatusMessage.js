import React from 'react';

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
            {enrichmentProgress.in_progress 
              ? `🔄 Enriching profiles in background...` 
              : enrichmentProgress.enriched > 0 
                ? `✨ Enriched ${enrichmentProgress.enriched} new profiles with LinkedIn data.`
                : `📊 Using ${enrichmentProgress.total} previously enriched profiles.`
            } Total enriched connections: {enrichmentProgress.total}
          </p>
        </div>
      </>
    );
  }

  // Don't show basic success message if enrichment is happening
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