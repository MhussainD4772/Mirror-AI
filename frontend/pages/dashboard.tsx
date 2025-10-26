import React, { useState, useEffect } from 'react';
import ReflectionCard from '../components/ReflectionCard';
import ChartSection from '../components/ChartSection';
import api from '../utils/apiClient';

interface Reflection {
  id: string;
  text: string;
  ai_summary: string;
  sentiment: string;
  tags: string[];
  created_at: string;
}

export default function Dashboard() {
  const [entries, setEntries] = useState<Reflection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchEntries();
  }, []);

  const fetchEntries = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/entries');
      setEntries(response.data.entries || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch entries');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading your reflections...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6 max-w-md mx-auto">
          <div className="text-red-400 text-lg mb-2">⚠️ Error</div>
          <p className="text-red-300">{error}</p>
          <button
            onClick={fetchEntries}
            className="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-slate-100 mb-4">
          Your Reflection Dashboard
        </h1>
        <p className="text-xl text-slate-300">
          Track your emotional journey and discover patterns in your thoughts.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <div className="text-3xl font-bold text-slate-100 mb-2">
            {entries.length}
          </div>
          <div className="text-slate-300">Total Reflections</div>
        </div>
        
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <div className="text-3xl font-bold text-green-400 mb-2">
            {entries.filter(e => e.sentiment === 'positive').length}
          </div>
          <div className="text-slate-300">Positive Days</div>
        </div>
        
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <div className="text-3xl font-bold text-blue-400 mb-2">
            {new Set(entries.flatMap(e => e.tags)).size}
          </div>
          <div className="text-slate-300">Unique Themes</div>
        </div>
      </div>

      {/* Charts Section */}
      {entries.length > 0 && (
        <ChartSection entries={entries} />
      )}

      {/* Entries List */}
      <div>
        <h2 className="text-2xl font-semibold text-slate-100 mb-6">
          All Reflections
        </h2>
        
        {entries.length === 0 ? (
          <div className="text-center py-12">
            <div className="bg-slate-800 rounded-lg p-8 max-w-md mx-auto">
              <div className="text-6xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-slate-100 mb-2">
                No reflections yet
              </h3>
              <p className="text-slate-300 mb-4">
                Start reflecting to see your insights and patterns here.
              </p>
              <a
                href="/"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md transition-colors"
              >
                Add Your First Reflection
              </a>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {entries.map((reflection) => (
              <ReflectionCard key={reflection.id} reflection={reflection} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}