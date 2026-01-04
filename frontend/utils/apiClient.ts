import axios from "axios";
import { supabase } from "./supabase";

// Use Next.js API routes as proxy instead of direct backend calls
// This avoids CORS issues and keeps backend URL server-side only
const api = axios.create({
  baseURL:
    typeof window !== "undefined"
      ? ""
      : process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor for auth tokens and logging
api.interceptors.request.use(
  async (config) => {
    // Get current session and add auth token to headers
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
      }
    } catch (error) {
      console.error("Failed to get auth session:", error);
    }

    // Prepend /api to routes when running in browser (client-side)
    // This routes through Next.js API routes which proxy to the backend
    if (
      typeof window !== "undefined" &&
      config.url &&
      !config.url.startsWith("/api/") &&
      !config.url.startsWith("http")
    ) {
      config.url = `/api${config.url}`;
    }

    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);

    // Handle 401 unauthorized - redirect to login
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;
