import { useState } from 'react';
import { uploadFile, getEnrichmentProgress } from '../services/api';
import { POLLING_INTERVAL } from '../services/constants';

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

      // Set basic info
      setConnectionsParsed(true);
      setConnectionsCount(response.count);
      
      // Show enrichment info
      if (response.total_enriched > 0 || response.will_enrich > 0) {
        setEnrichmentProgress({
          enriched: 0,
          total: response.total_enriched
        });
      }
      
      // Start simple polling if enrichment started
      if (response.enrichment_started && response.will_enrich > 0) {
        setRealTimeProgress({ current: 0, total: response.will_enrich });
        
        const pollProgress = setInterval(async () => {
          try {
            const { current, total, completed } = await getEnrichmentProgress();
            
            setRealTimeProgress({ current, total });
            
            if (completed) {
              clearInterval(pollProgress);
              setRealTimeProgress(null);
              setEnrichmentProgress({
                enriched: total,
                total: response.total_enriched + total
              });
            }
          } catch (err) {
            clearInterval(pollProgress);
            setRealTimeProgress(null);
          }
        }, POLLING_INTERVAL);
      }
      
      return null;
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