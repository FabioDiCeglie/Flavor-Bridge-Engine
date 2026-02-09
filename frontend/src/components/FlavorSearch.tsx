"use client";

import { useState, FormEvent, useRef, useEffect } from "react";
import {
  searchIngredient,
  explainFlavorBridge,
  type SearchMatch,
  type SearchResponse,
  type SearchError,
} from "@/lib/api";

const GREEN = "#1db954";

const SUGGESTIONS = [
  "Miso",
  "Parmesan cheese",
  "Soy sauce",
  "Garlic",
  "Ginger",
  "Kale",
  "Kombu",
  "Cherry tomato",
];

// Desktop only: scattered around the chat card
const BUBBLE_POSITIONS = [
  { left: "-5.5rem", top: "8%" },
  { right: "-4rem", top: "22%" },
  { left: "-5rem", top: "45%" },
  { right: "-3.5rem", top: "58%" },
  { left: "-5.5rem", top: "68%" },
  { right: "-4rem", top: "35%" },
  { left: "50%", top: "-2.5rem", style: { transform: "translateX(-50%)" } },
  { left: "85%", top: "72%", style: { transform: "translateX(-50%)" } },
];

export default function FlavorSearch() {
  const [query, setQuery] = useState("");
  const [currentQuery, setCurrentQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [explainLoading, setExplainLoading] = useState(false);
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [searchError, setSearchError] = useState<SearchError | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [loading, searchResult, searchError, explanation]);

  async function doSearch(q: string) {
    const trimmed = q.trim();
    if (!trimmed) return;
    setQuery(trimmed);
    setCurrentQuery(trimmed);
    setSearchResult(null);
    setSearchError(null);
    setExplanation(null);
    setLoading(true);
    try {
      const data = await searchIngredient(trimmed);
      setSearchResult(data);
    } catch (err: unknown) {
      const e = err as SearchError & { status?: number };
      if (e.status === 404) {
        setSearchError({ error: e.error, query: e.query, message: e.message });
      } else if (e.status === 429) {
        setSearchError({
          error: "Too many requests",
          query: trimmed,
          message: "Slow down — try again in a minute.",
        });
      } else {
        setSearchError({
          error: "Something went wrong",
          query: trimmed,
          message: e.message || "Please try again.",
        });
      }
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    doSearch(query);
  }

  async function handleExplain() {
    if (!searchResult?.matches?.length) return;
    setExplainLoading(true);
    setExplanation(null);
    try {
      const data = await explainFlavorBridge(searchResult.query, searchResult.matches);
      setExplanation(data.explanation);
    } catch {
      setExplanation("Couldn't load this time. Try again!");
    } finally {
      setExplainLoading(false);
    }
  }

  function tryAnother() {
    setQuery("");
    setCurrentQuery("");
    setSearchResult(null);
    setSearchError(null);
    setExplanation(null);
  }

  const hasSearched = currentQuery.length > 0;
  const showInput = !loading && !searchResult;

  return (
    <div className="relative mx-auto flex h-[560px] w-full max-w-2xl max-h-[calc(100vh-10rem)] flex-col overflow-visible">
      {/* Desktop: floating bubbles around the chat card */}
      {SUGGESTIONS.map((ingredient, i) => {
        const pos = BUBBLE_POSITIONS[i] ?? BUBBLE_POSITIONS[0];
        return (
          <button
            key={ingredient}
            type="button"
            onClick={() => !loading && doSearch(ingredient)}
            disabled={loading}
            className="animate-float absolute z-20 hidden rounded-2xl border-2 border-[#1db954]/50 bg-[#181818] px-3 py-2 text-center text-sm font-semibold text-[#1db954] shadow-lg transition hover:border-[#1db954] hover:bg-[#1db954]/20 hover:scale-110 hover:shadow-[#1db954]/20 disabled:opacity-50 lg:block"
            style={{
              left: "left" in pos ? pos.left : undefined,
              right: "right" in pos ? pos.right : undefined,
              top: pos.top,
              animationDelay: `${i * 0.35}s`,
              animationDuration: `${3.5 + (i % 3) * 0.5}s`,
              ...("style" in pos ? pos.style : {}),
            }}
          >
            {ingredient}
          </button>
        );
      })}

      {/* Chat card */}
      <div className="relative z-10 flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-3xl bg-[#181818] shadow-2xl">
        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-4 py-5">
            <div className="mx-auto w-full max-w-full space-y-4 break-words">
              {hasSearched && (
                <Bubble type="user">
                  <p className="font-semibold">{currentQuery}</p>
                </Bubble>
              )}

              {loading && (
                <Bubble type="app">
                  <p className="text-neutral-400">Finding your umami cousins…</p>
                </Bubble>
              )}

              {searchError && (
                <Bubble type="app">
                  <p className="font-medium text-white">Oops! We don&apos;t have that one yet.</p>
                  <p className="mt-1 text-sm text-neutral-400">{searchError.message}</p>
                </Bubble>
              )}

              {searchResult && (
                <Bubble type="app">
                  <p className="mb-3 font-semibold text-white">
                    You found {searchResult.matches.length} umami cousins! 🎉
                  </p>
                  <ul className="space-y-2">
                    {searchResult.matches.map((m) => (
                      <MatchPill key={m.id} match={m} />
                    ))}
                  </ul>
                  {!explanation && (
                    <button
                      type="button"
                      onClick={handleExplain}
                      disabled={explainLoading}
                      className="mt-4 w-full rounded-xl bg-[#1db954] py-2.5 font-bold text-black transition hover:bg-[#1ed760] active:scale-[0.98] disabled:opacity-60"
                    >
                      {explainLoading ? "Thinking…" : "Why do they taste similar? →"}
                    </button>
                  )}
                </Bubble>
              )}

              {explanation && (
                <Bubble type="app">
                  <p className="mb-2 font-semibold text-[#1db954]">Here&apos;s the science 🧪</p>
                  <p className="text-sm leading-relaxed text-neutral-300">{explanation}</p>
                  <button
                    type="button"
                    onClick={tryAnother}
                    className="mt-3 text-sm font-semibold text-[#1db954] hover:underline"
                  >
                    Try another ingredient →
                  </button>
                </Bubble>
              )}

              <div ref={bottomRef} />
            </div>
          </div>

          <div className="border-t border-neutral-800 p-4">
            {showInput ? (
              <form onSubmit={handleSearch} className="flex gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Or type one…"
                  className="flex-1 rounded-xl border border-neutral-700 bg-[#282828] px-4 py-3 text-white placeholder-neutral-500 outline-none transition focus:border-[#1db954] focus:ring-2 focus:ring-[#1db954]/30"
                  style={{ caretColor: GREEN }}
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="rounded-xl bg-[#1db954] px-5 py-3 font-bold text-black transition hover:bg-[#1ed760] active:scale-95 disabled:opacity-50"
                >
                  Go
                </button>
              </form>
            ) : (
              <button
                type="button"
                onClick={tryAnother}
                className="w-full rounded-xl border-2 border-dashed border-neutral-600 py-3 text-sm font-medium text-neutral-400 transition hover:border-[#1db954] hover:text-[#1db954]"
              >
                Try another ingredient
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Mobile only: bubbles below the chat */}
      <div className="flex shrink-0 flex-wrap justify-center gap-2 pt-4 pb-1 lg:hidden">
        {SUGGESTIONS.map((ingredient, i) => (
          <button
            key={ingredient}
            type="button"
            onClick={() => !loading && doSearch(ingredient)}
            disabled={loading}
            className="animate-float rounded-xl border-2 border-[#1db954]/50 bg-[#181818] px-2.5 py-1.5 text-xs font-semibold text-[#1db954] shadow-lg transition hover:border-[#1db954] hover:bg-[#1db954]/20 hover:scale-105 disabled:opacity-50"
            style={{
              animationDelay: `${i * 0.35}s`,
              animationDuration: `${3.5 + (i % 3) * 0.5}s`,
            }}
          >
            {ingredient}
          </button>
        ))}
      </div>
    </div>
  );
}

function Bubble({
  type,
  children,
}: {
  type: "app" | "user";
  children: React.ReactNode;
}) {
  return (
    <div className={`flex ${type === "user" ? "justify-end" : "justify-start"}`}>
      <div
        className={
          type === "user"
            ? "max-w-[85%] rounded-2xl rounded-br-md bg-[#1db954] px-4 py-2.5 text-black"
            : "max-w-[85%] rounded-2xl rounded-bl-md bg-[#282828] px-4 py-2.5"
        }
      >
        {children}
      </div>
    </div>
  );
}

function MatchPill({ match }: { match: SearchMatch }) {
  const [open, setOpen] = useState(false);
  const short =
    match.description.length > 80
      ? match.description.slice(0, 80).trim() + "…"
      : match.description;

  return (
    <button
      type="button"
      onClick={() => setOpen(!open)}
      className="w-full rounded-xl bg-[#121212] p-3 text-left transition hover:bg-[#333]"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium text-white">{match.name}</span>
        <span className="rounded-full bg-[#1db954]/25 px-2 py-0.5 text-xs font-semibold text-[#1db954]">
          {(match.score * 100).toFixed(0)}%
        </span>
      </div>
      <p className="mt-1 text-xs text-neutral-500">{open ? match.description : short}</p>
      {open && match.compounds && (
        <p className="mt-2 text-xs text-neutral-600">Compounds: {match.compounds}</p>
      )}
    </button>
  );
}
