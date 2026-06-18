import { Reflection } from "../types/reflection";

export function countPositiveDays(entries: Reflection[]): number {
  return entries.filter((entry) => entry.sentiment === "positive").length;
}

export function calculateStreak(entries: Reflection[]): number {
  if (entries.length === 0) return 0;

  const sorted = [...entries].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  let streak = 0;
  let current = new Date();

  for (const entry of sorted) {
    const entryDate = new Date(entry.created_at.split("T")[0]);
    if (entryDate.toDateString() === current.toDateString()) {
      streak += 1;
      current.setDate(current.getDate() - 1);
    } else if (entryDate < current) {
      break;
    }
  }

  return streak;
}

export function averageEntriesPerWeek(entries: Reflection[]): number {
  if (entries.length === 0) return 0;
  return entries.length / Math.max(1, Math.floor(entries.length / 7));
}

export function getDominantThemes(entries: Reflection[]): string[] {
  const counts: Record<string, number> = {};

  entries.forEach((entry) => {
    entry.tags.forEach((tag) => {
      counts[tag] = (counts[tag] || 0) + 1;
    });
  });

  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([tag]) => tag);
}
