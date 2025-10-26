import React, { useState } from 'react';
import ReflectionForm from '../components/ReflectionForm';
import ReflectionCard from '../components/ReflectionCard';

interface Reflection {
  id: string;
  text: string;
  ai_summary: string;
  sentiment: string;
  tags: string[];
  created_at: string;
}

export default function Home() {
  const [recentReflections, setRecentReflections] = useState<Reflection[]>([]);

  const handleReflectionAdded = (newReflection: Reflection) => {
    setRecentReflections(prev => [newReflection, ...prev]);
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-slate-100 mb-4">
          Welcome to Mirror AI
        </h1>
        <p className="text-xl text-slate-300 max-w-2xl mx-auto">
          Your personal reflection companion. Share your thoughts, get AI insights, 
          and track your emotional journey over time.
        </p>
      </div>

      {/* Reflection Form */}
      <div className="max-w-2xl mx-auto">
        <ReflectionForm onReflectionAdded={handleReflectionAdded} />
      </div>

      {/* Recent Reflections */}
      {recentReflections.length > 0 && (
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-slate-100 mb-6">
            Recent Reflections
          </h2>
          <div className="space-y-4">
            {recentReflections.map((reflection) => (
              <ReflectionCard key={reflection.id} reflection={reflection} />
            ))}
          </div>
        </div>
      )}

      {/* Call to Action */}
      {recentReflections.length === 0 && (
        <div className="text-center py-12">
          <div className="bg-slate-800 rounded-lg p-8 max-w-md mx-auto">
            <div className="text-6xl mb-4">🤔</div>
            <h3 className="text-xl font-semibold text-slate-100 mb-2">
              Ready to reflect?
            </h3>
            <p className="text-slate-300">
              Start your journey of self-discovery by sharing your first reflection above.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}