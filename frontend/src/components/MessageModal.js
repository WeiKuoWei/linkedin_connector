import React from 'react';

const MessageModal = ({
  show,
  onClose,
  selectedConnection,
  generatedMessage,
  onMessageChange,
  messageLoading,
  onCopyToClipboard,
  onOpenLinkedInProfile,
  copied
}) => {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">
            📧 Message for {selectedConnection?.name}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        {selectedConnection && (
          <div className="mb-4 p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">
              <strong>{selectedConnection.role}</strong> at <strong>{selectedConnection.company}</strong>
              {selectedConnection.location && ` • ${selectedConnection.location}`}
            </p>
          </div>
        )}
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Generated Message:
          </label>
          {messageLoading ? (
            <div className="p-4 bg-gray-50 rounded border">
              <p className="text-gray-500">Generating personalized message...</p>
            </div>
          ) : (
            <textarea
              value={generatedMessage}
              onChange={(e) => onMessageChange(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg h-48 resize-none"
              placeholder="Your personalized message will appear here..."
            />
          )}
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={() => onCopyToClipboard(generatedMessage)}
            disabled={!generatedMessage || messageLoading}
            className={`px-4 py-2 rounded-lg transition-colors ${
              generatedMessage && !messageLoading
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {copied ? '✅ Copied to Clipboard!' : '📋 Copy to Clipboard'}
          </button>
          <button
            onClick={() => onOpenLinkedInProfile(selectedConnection?.linkedin_url)}
            disabled={!selectedConnection?.linkedin_url}
            className={`px-4 py-2 rounded-lg transition-colors ${
              selectedConnection?.linkedin_url
                ? 'bg-blue-700 text-white hover:bg-blue-800'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            🔗 Open LinkedIn to Send
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default MessageModal;