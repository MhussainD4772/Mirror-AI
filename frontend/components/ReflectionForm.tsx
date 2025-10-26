import React, { useState } from 'react';
import api from '../utils/apiClient';

interface ReflectionFormProps {
  onReflectionAdded: (reflection: any) => void;
}

const ReflectionForm: React.FC<ReflectionFormProps> = ({ onReflectionAdded }) => {
  const [text, setText] = useState('');
  const [mood, setMood] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const moods = [
    { emoji: '🙂', value: 'positive', label: 'Good' },
    { emoji: '😐', value: 'neutral', label: 'Okay' },
    { emoji: '🙁', value: 'negative', label: 'Tough' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Please write something before reflecting');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await api.post('/reflect', {
        text: text.trim(),
        user_id: 'default_user', // For now, using default user
      });

      const reflection = response.data;
      onReflectionAdded(reflection);
      
      // Reset form
      setText('');
      setMood('');
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process reflection');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
      <h2 className="text-2xl font-semibold text-slate-100 mb-4">
        How are you feeling today?
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="reflection" className="block text-sm font-medium text-slate-300 mb-2">
            Share your thoughts
          </label>
          <textarea
            id="reflection"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="What's on your mind? How was your day? What are you grateful for?"
            className="w-full h-32 px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={isLoading}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Quick mood check
          </label>
          <div className="flex space-x-4">
            {moods.map((moodOption) => (
              <button
                key={moodOption.value}
                type="button"
                onClick={() => setMood(moodOption.value)}
                className={`flex flex-col items-center p-3 rounded-lg border-2 transition-colors ${
                  mood === moodOption.value
                    ? 'border-blue-500 bg-blue-500/20'
                    : 'border-slate-600 bg-slate-700 hover:border-slate-500'
                }`}
                disabled={isLoading}
              >
                <span className="text-2xl mb-1">{moodOption.emoji}</span>
                <span className="text-xs text-slate-300">{moodOption.label}</span>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="text-red-400 text-sm bg-red-900/20 border border-red-800 rounded-md p-3">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !text.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-md transition-colors flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Processing...</span>
            </>
          ) : (
            <span>Reflect</span>
          )}
        </button>
      </form>
    </div>
  );
};

export default ReflectionForm;