import { AppProps } from "next/app";
import Head from "next/head";
import "@/styles/globals.css";
import Navbar from "../components/Navbar";
import { AuthProvider } from "../contexts/AuthContext";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <Head>
        <title>Mirror AI - Your Personal Reflection Companion</title>
        <meta
          name="description"
          content="AI-powered personal reflection and emotional analysis system. Share your thoughts, get empathetic insights, and track your emotional journey."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta
          name="keywords"
          content="AI, reflection, emotional analysis, mental health, self-awareness, journaling"
        />
        <meta name="author" content="Mirror AI" />

        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://mirror-ai.vercel.app/" />
        <meta
          property="og:title"
          content="Mirror AI - Your Personal Reflection Companion"
        />
        <meta
          property="og:description"
          content="AI-powered personal reflection and emotional analysis system. Share your thoughts, get empathetic insights, and track your emotional journey."
        />
        <meta
          property="og:image"
          content="https://mirror-ai.vercel.app/og-image.png"
        />

        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://mirror-ai.vercel.app/" />
        <meta
          property="twitter:title"
          content="Mirror AI - Your Personal Reflection Companion"
        />
        <meta
          property="twitter:description"
          content="AI-powered personal reflection and emotional analysis system. Share your thoughts, get empathetic insights, and track your emotional journey."
        />
        <meta
          property="twitter:image"
          content="https://mirror-ai.vercel.app/og-image.png"
        />

        <link rel="icon" href="/favicon.ico" />
        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/apple-touch-icon.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="32x32"
          href="/favicon-32x32.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="16x16"
          href="/favicon-16x16.png"
        />
        <link rel="manifest" href="/site.webmanifest" />

        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </Head>
      <div className="min-h-screen bg-slate-900">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Component {...pageProps} />
        </main>
      </div>
    </AuthProvider>
  );
}
