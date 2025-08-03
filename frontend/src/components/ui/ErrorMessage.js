import React from 'react';

export const ErrorMessage = ({ error }) => error ? (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
    {error}
  </div>
) : null;