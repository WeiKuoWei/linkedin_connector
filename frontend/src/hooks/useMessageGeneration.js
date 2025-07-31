import { useState } from 'react';
import { generateMessage } from '../services/api';

export const useMessageGeneration = () => {
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [generatedMessage, setGeneratedMessage] = useState('');
  const [messageLoading, setMessageLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerateMessage = async (suggestion, mission) => {
    setSelectedConnection(suggestion);
    setShowMessageModal(true);
    setMessageLoading(true);
    setGeneratedMessage('');
    
    try {
      const response = await generateMessage({
        name: suggestion.name,
        company: suggestion.company,
        role: suggestion.role,
        mission: mission,
        profile_summary: suggestion.profile_summary || '',
        location: suggestion.location || ''
      });
      
      setGeneratedMessage(response.message);
    } catch (err) {
      setGeneratedMessage('Error generating message. Please try again.');
      console.error('Error generating message:', err);
    }
    setMessageLoading(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const openLinkedInProfile = (url) => {
    if (url) {
      window.open(url, '_blank');
    }
  };

  return {
    showMessageModal,
    setShowMessageModal,
    selectedConnection,
    generatedMessage,
    setGeneratedMessage,
    messageLoading,
    copied,
    handleGenerateMessage,
    copyToClipboard,
    openLinkedInProfile
  };
};