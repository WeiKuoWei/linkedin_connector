import React from 'react';
import { ENRICHMENT_SECONDS_PER_PROFILE, MAX_CONCURRENT_REQUESTS, RATE_LIMIT_SLEEP_SECONDS, VECTORIZATION_SECONDS_PER_PROFILE } from '../../services/constants';

export const ProgressBar = ({ realTimeProgress }) => {
  const numberOfBatches = Math.ceil(realTimeProgress.total / MAX_CONCURRENT_REQUESTS);
  const TOTAL_PROCESSING_TIME_PER_PROFILE = ENRICHMENT_SECONDS_PER_PROFILE + VECTORIZATION_SECONDS_PER_PROFILE;
  const processingTime = numberOfBatches * (TOTAL_PROCESSING_TIME_PER_PROFILE + RATE_LIMIT_SLEEP_SECONDS);

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
};