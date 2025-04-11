import React from 'react';
export function Label({ htmlFor, children }) {
  return (
    <label htmlFor={htmlFor} className="text-sm font-medium mb-1">
      {children}
    </label>
  );
}