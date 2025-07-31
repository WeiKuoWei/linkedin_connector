import { useState } from 'react';
import { uploadFile, getEnrichmentProgress } from '../services/api';

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
      return null; // No error
    } else {
      return 'Please select a CSV file';
    }
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
        
        // Poll for progress updates
        const pollProgress = setInterval(async () => {
          try {
            const progressData = await getEnrichmentProgress();
            const { current, total, completed, in_progress } = progressData;
            
            // Only update if enrichment is actually in progress
            if (in_progress || !completed) {
              setRealTimeProgress({ current, total });
            }
            
            if (completed && !in_progress) {
              clearInterval(pollProgress);
              setRealTimeProgress(null);
              
              // Show completion message
              setEnrichmentProgress({
                enriched: response.will_enrich,
                total: response.total_enriched + response.will_enrich
              });
              
              console.log(`Enrichment completed! ${response.will_enrich} profiles were enriched.`);
            }
          } catch (err) {
            clearInterval(pollProgress);
            console.error('Error polling progress:', err);
            setRealTimeProgress(null);
          }
        }, 5000);
        
        // Fallback timeout to prevent infinite polling
        setTimeout(() => {
          clearInterval(pollProgress);
          setRealTimeProgress(null);
          setEnrichmentProgress({
            enriched: response.will_enrich,
            total: response.total_enriched + response.will_enrich,
            needs_vectorization: response.needs_vectorization || 0
          });
        }, 60000);
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
    handleUpload
  };
};