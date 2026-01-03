import { Reflection } from '../types/reflection';
import { extractTopEmotions } from './emotionUtils';

export const normalizeReflection = (entry: any): Reflection => {
  let emotions: Record<string, number> | undefined;
  let providedTopEmotions;

  if (entry?.emotions) {
    if (typeof entry.emotions === 'string') {
      try {
        emotions = JSON.parse(entry.emotions);
      } catch {
        emotions = undefined;
      }
    } else {
      emotions = entry.emotions;
    }
  }

  if (entry?.top_emotions) {
    if (typeof entry.top_emotions === 'string') {
      try {
        providedTopEmotions = JSON.parse(entry.top_emotions);
      } catch {
        providedTopEmotions = undefined;
      }
    } else if (Array.isArray(entry.top_emotions)) {
      providedTopEmotions = entry.top_emotions;
    }
  }

  const dominantEmotion: string =
    entry?.dominant_emotion || entry?.sentiment || 'neutral';

  const tags: string[] = Array.isArray(entry?.tags)
    ? entry.tags
    : typeof entry?.tags === 'string'
    ? entry.tags.split(',').map((tag: string) => tag.trim()).filter(Boolean)
    : [];

  return {
    id: entry?.id || '',
    text: entry?.text || '',
    ai_summary: entry?.ai_summary || '',
    sentiment: entry?.sentiment,
    dominant_emotion: dominantEmotion,
    emotions,
    top_emotions: extractTopEmotions(emotions, providedTopEmotions),
    tags,
    created_at: entry?.created_at || new Date().toISOString(),
  };
};

