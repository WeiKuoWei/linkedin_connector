import { useState } from 'react';
import { uploadFile, getEnrichmentProgress } from '../services/api';
import { ENRICHMENT_SECONDS_PER_PROFILE, MAX_CONCURRENT_REQUESTS, RATE_LIMIT_SLEEP_SECONDS, VECTORIZATION_SECONDS_PER_PROFILE, POLLING_SECONDS } from '../services/constants';

export const useFileUpload = () => {
  const [file, setFile] = useState(null);
  const [connectionsParsed, setConnectionsParsed] = useState(false);
  const [connectionsCount, setConnectionsCount] = useState(0);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [enrichmentProgress, setEnrichmentProgress] = useState(null);
  const [realTimeProgress, setRealTimeProgress] = useState(null);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      return null;
    } else {
      return 'Please select a CSV file';
    }
  };

  // Add reset function
  const resetFile = () => {
    setFile(null);
    setConnectionsParsed(false);
    setConnectionsCount(0);
    setEnrichmentProgress(null);
    setRealTimeProgress(null);
  };

  const handleUpload = async () => {
    if (!file) {
      return 'Please select a file first';
    }

    setUploadLoading(true);
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
        
        const numberOfBatches = Math.ceil(response.will_enrich / MAX_CONCURRENT_REQUESTS);
        
        const TOTAL_PROCESSING_TIME_PER_PROFILE = ENRICHMENT_SECONDS_PER_PROFILE + VECTORIZATION_SECONDS_PER_PROFILE;
        const estimatedProcessingTime = numberOfBatches * (TOTAL_PROCESSING_TIME_PER_PROFILE + RATE_LIMIT_SLEEP_SECONDS);
        const dynamicTimeout = (estimatedProcessingTime * 1.5) * 1000; // Add 50% buffer

        // Poll for progress updates
        const pollProgress = setInterval(async () => {
            try {
                const progressData = await getEnrichmentProgress();
                const { current, total, completed, in_progress } = progressData;
                
                // Always update progress if in progress
                if (in_progress) {
                    setRealTimeProgress({ current, total });
                }
                
                // Check for completion - simplified condition
                if (completed) {
                    clearInterval(pollProgress);
                    setRealTimeProgress(null);  // Hide progress bar
                    
                    // Show completion message
                    setEnrichmentProgress({
                        enriched: total,  // Use actual total from backend
                        total: response.total_enriched + total
                    });
                    
                    console.log(`Processing completed! ${total} profiles were processed.`);
                }
            } catch (err) {
                clearInterval(pollProgress);
                console.error('Error polling progress:', err);
                setRealTimeProgress(null);
            }
        }, POLLING_SECONDS);
        
        // Fallback timeout to prevent infinite polling
        setTimeout(() => {
          clearInterval(pollProgress);
          setRealTimeProgress(null);
          setEnrichmentProgress({
            enriched: response.will_enrich,
            total: response.total_enriched + response.will_enrich
          });
        }, dynamicTimeout); 
      } else {
        // No enrichment needed
        if (response.total_enriched > 0) {
          setEnrichmentProgress({
            enriched: 0,
            total: response.total_enriched
          });
        }
      }
      
      return null; // No error
    } catch (err) {
      return 'Failed to upload file: ' + (err.response?.data?.detail || err.message);
    } finally {
      setUploadLoading(false);
    }
  };

  return {
    file,
    connectionsParsed,
    connectionsCount,
    uploadLoading,
    enrichmentProgress,
    realTimeProgress,
    handleFileSelect,
    handleUpload,
    resetFile
  };
};