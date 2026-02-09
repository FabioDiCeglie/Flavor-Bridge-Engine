const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://flavor-bridge-engine.fabiodiceglie.workers.dev";

export type SearchMatch = {
  id: string;
  score: number;
  name: string;
  description: string;
  compounds: string;
};

export type SearchResponse = {
  query: string;
  matches: SearchMatch[];
};

export type SearchError = {
  error: string;
  query: string;
  message?: string;
};

export type ExplainResponse = {
  query: string;
  explanation: string;
};

export async function searchIngredient(q: string): Promise<SearchResponse> {
  const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(q)}`);
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, ...data };
  }
  return data as SearchResponse;
}

export async function explainFlavorBridge(query: string, matches: SearchMatch[]): Promise<ExplainResponse> {
  const res = await fetch(`${API_URL}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, matches }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw { status: res.status, ...data };
  }
  return data as ExplainResponse;
}
