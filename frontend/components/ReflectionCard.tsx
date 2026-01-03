import React from 'react';
import { Reflection } from '../types/reflection';
import {
  deriveLegacySentiment,
  getEmotionColorClasses,
  getEmotionEmoji,
  extractTopEmotions,
  formatEmotionLabel,
} from '../utils/emotionUtils';

interface ReflectionCardProps {
  reflection: Reflection;
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

  const polarity = deriveLegacySentiment(
    reflection.dominant_emotion,
    reflection.sentiment
  );
  const dominantLabel = formatEmotionLabel(
    reflection.dominant_emotion || reflection.sentiment || 'Neutral'
  );
  const topEmotions = extractTopEmotions(
    reflection.emotions,
    reflection.top_emotions
  );

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getEmotionEmoji(polarity)}</span>
          <div>
            <div
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getEmotionColorClasses(
                polarity
              )}`}
            >
              {dominantLabel}
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

        {topEmotions.length > 0 && (
          <div>
            <h3 className="text-slate-300 text-sm font-medium mb-2">
              Top emotions
            </h3>
            <div className="flex flex-wrap gap-2">
              {topEmotions.map((emotion) => (
                <div
                  key={emotion.label}
                  className="px-3 py-1 rounded-full border border-slate-600 text-sm text-slate-200 bg-slate-700/60"
                  title={`${formatEmotionLabel(emotion.label)} • ${(emotion.score * 100).toFixed(1)}%`}
                >
                  <span className="font-medium text-slate-100">
                    {formatEmotionLabel(emotion.label)}
                  </span>
                  <span className="ml-2 text-slate-300">
                    {(emotion.score * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

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