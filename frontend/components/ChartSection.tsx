import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Filler,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Radar } from 'react-chartjs-2';
import { Reflection } from '../types/reflection';
import { deriveLegacySentiment, formatEmotionLabel } from '../utils/emotionUtils';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Filler,
  Title,
  Tooltip,
  Legend
);

interface ChartSectionProps {
  entries: Reflection[];
}

const ChartSection: React.FC<ChartSectionProps> = ({ entries }) => {
  // Process data for charts
  const processChartData = () => {
    if (!entries || entries.length === 0) {
      return {
        sentimentData: { labels: [], datasets: [] },
        tagData: { labels: [], datasets: [] },
        emotionSpectrum: { labels: [], datasets: [] },
      };
    }

    // Sort entries by date
    const sortedEntries = [...entries].sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );

    // Sentiment over time data
    const sentimentLabels = sortedEntries.map((entry) => {
      const date = new Date(entry.created_at);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const sentimentValues = sortedEntries.map((entry) => {
      const polarity = deriveLegacySentiment(
        entry.dominant_emotion,
        entry.sentiment
      );
      if (polarity === 'positive') return 1;
      if (polarity === 'negative') return -1;
      return 0;
    });

    // Tag frequency data
    const tagCounts: { [key: string]: number } = {};
    entries.forEach((entry) => {
      entry.tags.forEach((tag) => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });

    const sortedTags = Object.entries(tagCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 8); // Top 8 tags

    // Emotion spectrum (averaged probabilities)
    const emotionTotals: Record<string, number> = {};
    let emotionEntryCount = 0;

    entries.forEach((entry) => {
      if (entry.emotions && Object.keys(entry.emotions).length > 0) {
        emotionEntryCount += 1;
        Object.entries(entry.emotions).forEach(([label, score]) => {
          emotionTotals[label] = (emotionTotals[label] || 0) + score;
        });
      }
    });

    const emotionSpectrum =
      emotionEntryCount > 0
        ? (() => {
            const averages = Object.entries(emotionTotals).map(([label, total]) => [
              label,
              total / emotionEntryCount,
            ]);
            const topEmotions = averages
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5);
            return {
              labels: topEmotions.map(([label]) => formatEmotionLabel(label)),
              datasets: [
                {
                  label: 'Average intensity',
                  data: topEmotions.map(([, avg]) => Number(avg.toFixed(4))),
                  backgroundColor: 'rgba(129, 140, 248, 0.2)',
                  borderColor: 'rgba(99, 102, 241, 0.8)',
                  borderWidth: 2,
                  pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                },
              ],
            };
          })()
        : { labels: [], datasets: [] };

    return {
      sentimentData: {
        labels: sentimentLabels,
        datasets: [
          {
            label: 'Mood Trend',
            data: sentimentValues,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            pointBackgroundColor: 'rgb(59, 130, 246)',
            pointBorderColor: 'rgb(59, 130, 246)',
            pointRadius: 4,
          },
        ],
      },
      tagData: {
        labels: sortedTags.map(([tag]) => tag),
        datasets: [
          {
            label: 'Frequency',
            data: sortedTags.map(([, count]) => count),
            backgroundColor: 'rgba(59, 130, 246, 0.6)',
            borderColor: 'rgb(59, 130, 246)',
            borderWidth: 1,
          },
        ],
      },
      emotionSpectrum,
    };
  };

  const { sentimentData, tagData, emotionSpectrum } = processChartData();

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e2e8f0',
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#94a3b8',
        },
        grid: {
          color: '#334155',
        },
      },
      y: {
        ticks: {
          color: '#94a3b8',
        },
        grid: {
          color: '#334155',
        },
      },
    },
  };

  const sentimentChartOptions = {
    ...chartOptions,
    scales: {
      ...chartOptions.scales,
      y: {
        ...chartOptions.scales.y,
        min: -1.5,
        max: 1.5,
        ticks: {
          ...chartOptions.scales.y.ticks,
          callback: function (value: any) {
            switch (value) {
              case 1:
                return 'Positive';
              case 0:
                return 'Neutral';
              case -1:
                return 'Negative';
              default:
                return '';
            }
          },
        },
      },
    },
  };

  const emotionSpectrumOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e2e8f0',
        },
      },
    },
    scales: {
      r: {
        angleLines: {
          color: '#334155',
        },
        grid: {
          color: '#334155',
        },
        pointLabels: {
          color: '#cbd5f5',
          font: {
            size: 12,
          },
        },
        ticks: {
          display: false,
          beginAtZero: true,
          maxTicksLimit: 5,
        },
        max: 1,
        min: 0,
      },
    },
  };

  if (!entries || entries.length === 0) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Insights</h2>
        <div className="text-center text-slate-400 py-8">
          <p>No data available yet.</p>
          <p className="text-sm mt-2">Add some reflections to see your insights!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sentiment Trend Chart */}
      <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Mood Trend</h2>
        <div className="h-64">
          <Line data={sentimentData} options={sentimentChartOptions} />
        </div>
      </div>

      {/* Tag Frequency Chart */}
      <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-xl font-semibold text-slate-100 mb-4">Top Themes</h2>
        <div className="h-64">
          <Bar data={tagData} options={chartOptions} />
        </div>
      </div>

      {/* Emotion Spectrum */}
      {emotionSpectrum.labels.length > 0 && (
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-semibold text-slate-100 mb-4">
            Emotion Spectrum
          </h2>
          <p className="text-slate-300 text-sm mb-4">
            Shows the average intensity of your most common emotions.
          </p>
          <div className="h-72">
            <Radar data={emotionSpectrum} options={emotionSpectrumOptions} />
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartSection;