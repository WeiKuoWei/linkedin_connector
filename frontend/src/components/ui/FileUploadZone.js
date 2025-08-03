import React from 'react';

export const FileUploadZone = ({ file, onFileSelect }) => (
  <div 
    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
      file 
        ? 'border-green-400 bg-green-50' 
        : 'border-gray-300 hover:border-gray-400 bg-gray-50'
    }`}
    onDrop={(e) => {
      e.preventDefault();
      const droppedFile = e.dataTransfer.files[0];
      onFileSelect(droppedFile);
    }}
    onDragOver={(e) => e.preventDefault()}
  >
    {file ? (
      <div className="text-green-700">
        <svg className="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="font-medium">{file.name}</p>
        <p className="text-sm">Ready to upload</p>
      </div>
    ) : (
      <div className="text-gray-500">
        <svg className="mx-auto h-12 w-12 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p className="mb-2">Drop your CSV file here, or</p>
        <label className="cursor-pointer">
          <span className="text-blue-500 hover:text-blue-600 font-medium">browse files</span>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => onFileSelect(e.target.files[0])}
            className="hidden"
          />
        </label>
      </div>
    )}
  </div>
);