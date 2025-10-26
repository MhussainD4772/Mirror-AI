import React from 'react';

interface ReflectionCardProps {
  reflection: {
    id: string;
    text: string;
    ai_summary: string;
    sentiment: string;
    tags: string[];
    created_at: string;
  };
}

const ReflectionCard: React.FC<ReflectionCardProps> = ({ reflection }) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'negative':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'neutral':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  const getSentimentEmoji = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return '🙂';
      case 'negative':
        return '🙁';
      case 'neutral':
        return '😐';
      default:
        return '😐';
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getSentimentEmoji(reflection.sentiment)}</span>
          <div>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSentimentColor(reflection.sentiment)}`}>
              {reflection.sentiment}
            </div>
          </div>
        </div>
        <span className="text-slate-400 text-sm">
          {formatDate(reflection.created_at)}
        </span>
      </div>

      <div className="space-y-4">
        <div>
          <h3 className="text-slate-300 text-sm font-medium mb-2">Your reflection</h3>
          <p className="text-slate-100 leading-relaxed">
            {reflection.text}
          </p>
        </div>

        <div>
          <h3 className="text-slate-300 text-sm font-medium mb-2">AI insight</h3>
          <p className="text-slate-200 leading-relaxed italic">
            {reflection.ai_summary}
          </p>
        </div>

        {reflection.tags && reflection.tags.length > 0 && (
          <div>
            <h3 className="text-slate-300 text-sm font-medium mb-2">Themes</h3>
            <div className="flex flex-wrap gap-2">
              {reflection.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-500/20 text-blue-400 border border-blue-500/30"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReflectionCard;