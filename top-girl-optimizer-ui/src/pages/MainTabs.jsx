import React from 'react';
import { useState } from 'react';
import Dashboard from './Dashboard';
import BuildingsCRUD from './BuildingsCRUD';

export default function MainTabs() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <div className="flex space-x-4 border-b mb-6">
        <button
          className={`py-2 px-4 font-semibold ${activeTab === 'dashboard' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`py-2 px-4 font-semibold ${activeTab === 'buildings' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
          onClick={() => setActiveTab('buildings')}
        >
          Buildings
        </button>
      </div>

      {activeTab === 'dashboard' && <Dashboard />}
      {activeTab === 'buildings' && <BuildingsCRUD />}
    </div>
  );
}
