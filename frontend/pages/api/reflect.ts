import type { NextApiRequest, NextApiResponse } from "next";

// Try server-side env var first, then fallback to public (for client-side access)
// This allows the API route to work even if NEXT_PUBLIC_BACKEND_URL isn't set
const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "http://127.0.0.1:8000";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  // Only allow POST requests
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/reflect`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Forward the authorization header from the client
        ...(req.headers.authorization && {
          Authorization: req.headers.authorization,
        }),
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();

    // Forward the status code and response
    return res.status(response.status).json(data);
  } catch (error: any) {
    console.error("Error proxying reflect request:", error);
    return res.status(500).json({
      error: "Failed to process reflection",
      detail: error.message,
    });
  }
}
