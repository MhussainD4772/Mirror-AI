import { EmotionScore } from '../types/reflection';

type SentimentPolarity = 'positive' | 'negative' | 'neutral';

const emotionPolarityMap: Record<string, SentimentPolarity> = {
  admiration: 'positive',
  amusement: 'positive',
  anger: 'negative',
  annoyance: 'negative',
  approval: 'positive',
  caring: 'positive',
  confusion: 'neutral',
  curiosity: 'positive',
  desire: 'positive',
  disappointment: 'negative',
  disapproval: 'negative',
  disgust: 'negative',
  embarrassment: 'negative',
  excitement: 'positive',
  fear: 'negative',
  gratitude: 'positive',
  grief: 'negative',
  joy: 'positive',
  love: 'positive',
  nervousness: 'negative',
  optimism: 'positive',
  pride: 'positive',
  realization: 'neutral',
  relief: 'positive',
  remorse: 'negative',
  sadness: 'negative',
  surprise: 'neutral',
  neutral: 'neutral',
};

export const deriveLegacySentiment = (
  dominantEmotion?: string,
  fallbackSentiment: string = 'neutral'
): SentimentPolarity => {
  if (!dominantEmotion) {
    return normalizeSentiment(fallbackSentiment);
  }
  const normalized = dominantEmotion.toLowerCase();
  return emotionPolarityMap[normalized] ?? normalizeSentiment(fallbackSentiment);
};

const normalizeSentiment = (sentiment: string): SentimentPolarity => {
  switch (sentiment?.toLowerCase()) {
    case 'positive':
      return 'positive';
    case 'negative':
      return 'negative';
    default:
      return 'neutral';
  }
};

export const getEmotionColorClasses = (polarity: SentimentPolarity): string => {
  switch (polarity) {
    case 'positive':
      return 'bg-green-500/20 text-green-400 border-green-500/30';
    case 'negative':
      return 'bg-red-500/20 text-red-400 border-red-500/30';
    default:
      return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
  }
};

export const getEmotionEmoji = (polarity: SentimentPolarity): string => {
  switch (polarity) {
    case 'positive':
      return '🙂';
    case 'negative':
      return '🙁';
    default:
      return '😐';
  }
};

export const extractTopEmotions = (
  emotions?: Record<string, number>,
  fallbackTop?: EmotionScore[]
): EmotionScore[] => {
  if (emotions && Object.keys(emotions).length > 0) {
    const sorted = Object.entries(emotions)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3);
    return sorted.map(([label, score]) => ({ label, score }));
  }
  return fallbackTop ?? [];
};

export const formatEmotionLabel = (label: string): string =>
  label
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

