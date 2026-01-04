# Mirror AI

Your personal reflection companion powered by AI.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Now-blue)](https://mirror-ai-pink.vercel.app)

Write about your day and get AI-powered insights about your emotions and patterns.

---

## What is Mirror AI?

Mirror AI helps you understand yourself better by analyzing your daily reflections with AI. Just write about your day, and get instant insights on:

- Your emotional state (sentiment analysis)
- Empathetic summaries and suggestions
- Recurring themes and patterns
- Trends over time

---

## Features

- 🤖 **AI Analysis** - Sentiment analysis and empathetic summaries
- 📊 **Dashboard** - Visualize your mood trends and patterns
- 📱 **Mobile-Friendly** - Works on any device
- 🔒 **Private** - Your data stays secure in Supabase

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/MhussainD4772/Mirror-AI.git
   cd Mirror-AI
   ```

2. **Backend setup**

   ```bash
   cd backend
   pip install -r requirements.txt
   # Set up .env with your credentials (see below)
   uvicorn main:app --reload
   ```

3. **Frontend setup** (new terminal)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Visit** http://localhost:3000

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
HF_TOKEN=your_huggingface_token
```

---

## Tech Stack

- **Frontend**: Next.js + TypeScript + TailwindCSS
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **AI**: Hugging Face Models (free)
- **Deployment**: Vercel (frontend) + Render (backend)

---

## Project Structure

```
mirror-ai/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── routes/              # API routes
│   ├── services/            # AI services
│   └── supabase_client.py   # DB client
├── frontend/
│   ├── pages/               # Next.js pages
│   ├── components/          # React components
│   └── utils/               # API client
└── README.md
```

---

## Deployment

### Backend (Render)

1. Connect GitHub repo to Render
2. Set root directory: `backend`
3. Add environment variables
4. Deploy

### Frontend (Vercel)

1. Import repo to Vercel
2. Set root directory: `frontend`
3. Add `NEXT_PUBLIC_BACKEND_URL` variable
4. Deploy

---

## Contributing

Contributions are welcome! Just fork the repo and submit a pull request.

---

## License

MIT License

---

**Built with ❤️ for self-discovery**
