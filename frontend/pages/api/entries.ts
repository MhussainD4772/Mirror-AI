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
  // Only allow GET requests
  if (req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    // Build query string from request query params
    const queryParams = new URLSearchParams();
    if (req.query.limit) {
      queryParams.append("limit", req.query.limit as string);
    }
    const queryString = queryParams.toString();
    const url = `${BACKEND_URL}/entries${queryString ? `?${queryString}` : ""}`;

    // Forward the request to the backend
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        // Forward the authorization header from the client
        ...(req.headers.authorization && {
          Authorization: req.headers.authorization,
        }),
      },
    });

    const data = await response.json();

    // Forward the status code and response
    return res.status(response.status).json(data);
  } catch (error: any) {
    console.error("Error proxying entries request:", error);
    return res.status(500).json({
      error: "Failed to fetch entries",
      detail: error.message,
    });
  }
}
