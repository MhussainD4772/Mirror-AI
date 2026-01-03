export interface EmotionScore {
  label: string;
  score: number;
}

export interface Reflection {
  id: string;
  text: string;
  ai_summary: string;
  sentiment?: string; // legacy field
  dominant_emotion?: string;
  emotions?: Record<string, number>;
  top_emotions?: EmotionScore[];
  tags: string[];
  created_at: string;
}

