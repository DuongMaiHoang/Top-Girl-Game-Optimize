import React from 'react';
export function Button({ variant = 'default', className = '', ...props }) {
  const base = 'px-4 py-2 rounded font-medium transition-colors ';
  const variants = {
    default: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    outline: 'border border-gray-400 text-gray-800 hover:bg-gray-100',
    destructive: 'bg-red-600 text-white hover:bg-red-700',
  };
  const variantClass = variants[variant] || variants.default;

  return (
    <button
      className={base + variantClass + ' ' + className}
      {...props}
    />
  );
}
