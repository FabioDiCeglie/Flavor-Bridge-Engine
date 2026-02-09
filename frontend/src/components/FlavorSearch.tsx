"use client";

import { useState, FormEvent, useRef, useEffect } from "react";
import {
  searchIngredient,
  explainFlavorBridge,
  type SearchMatch,
  type SearchResponse,
} from "../lib/api";
import SuggestionBubbles from "./SuggestionBubbles";
import Toast from "./Toast";

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

type SearchState = {
  query: string;
  currentQuery: string;
  loading: boolean;
  explainLoading: boolean;
  searchResult: SearchResponse | null;
  explanation: string | null;
  toastMessage: string | null;
};

const initialSearchState: SearchState = {
  query: "",
  currentQuery: "",
  loading: false,
  explainLoading: false,
  searchResult: null,
  explanation: null,
  toastMessage: null,
};

export default function FlavorSearch() {
  const [state, setState] = useState<SearchState>(initialSearchState);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.loading, state.searchResult, state.explanation]);

  async function doSearch(q: string) {
    const trimmed = q.trim();
    if (!trimmed) return;
    setState((s) => ({
      ...s,
      query: trimmed,
      currentQuery: trimmed,
      searchResult: null,
      explanation: null,
      loading: true,
    }));
    try {
      const data = await searchIngredient(trimmed);
      setState((s) => ({ ...s, searchResult: data, loading: false }));
    } catch (err: unknown) {
      const e = err as { status?: number; message?: string };
      const message =
        e.status === 404
          ? "We don't have this ingredient in our database yet."
          : e.status === 429
            ? "Slow down — try again in a minute."
            : e.message || "Something went wrong. Try again.";
      setState((s) => ({ ...s, loading: false, toastMessage: message }));
    }
  }

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    doSearch(state.query);
  }

  async function handleExplain() {
    if (!state.searchResult?.matches?.length) return;
    setState((s) => ({ ...s, explainLoading: true, explanation: null }));
    try {
      const data = await explainFlavorBridge(
        state.searchResult.query,
        state.searchResult.matches,
      );
      setState((s) => ({ ...s, explanation: data.explanation, explainLoading: false }));
    } catch {
      setState((s) => ({
        ...s,
        explainLoading: false,
        toastMessage: "Couldn't load this time. Try again!",
      }));
    }
  }

  function tryAnother() {
    setState((s) => ({
      ...s,
      query: "",
      currentQuery: "",
      searchResult: null,
      explanation: null,
    }));
  }

  const hasSearched = state.currentQuery.length > 0;
  const showInput = !state.loading && !state.searchResult;

  return (
    <div className="relative mx-auto flex h-[560px] w-full max-w-2xl max-h-[calc(100vh-10rem)] flex-col overflow-visible">
      <SuggestionBubbles
        suggestions={SUGGESTIONS}
        loading={state.loading}
        onSelect={doSearch}
        variant="floating"
      />

      {/* Chat card */}
      <div className="relative z-10 flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-3xl bg-[#181818] shadow-2xl">
        <div className="flex min-h-0 min-w-0 flex-1 flex-col">
          <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-4 py-5">
            <div className="mx-auto w-full max-w-full space-y-4 break-words">
              {hasSearched && (
                <Bubble type="user">
                  <p className="font-semibold">{state.currentQuery}</p>
                </Bubble>
              )}

              {state.loading && (
                <Bubble type="app">
                  <p className="text-neutral-400">Finding your umami cousins…</p>
                </Bubble>
              )}

              {state.searchResult && (
                <Bubble type="app">
                  <p className="mb-3 font-semibold text-white">
                    You found {state.searchResult.matches.length} umami cousins! 🎉
                  </p>
                  <ul className="space-y-2">
                    {state.searchResult.matches.map((m) => (
                      <MatchPill key={m.id} match={m} />
                    ))}
                  </ul>
                  {!state.explanation && (
                    <button
                      type="button"
                      onClick={handleExplain}
                      disabled={state.explainLoading}
                      className="mt-4 w-full rounded-xl bg-[#1db954] py-2.5 font-bold text-black transition hover:bg-[#1ed760] active:scale-[0.98] disabled:opacity-60"
                    >
                      {state.explainLoading ? "Thinking…" : "Why do they taste similar? →"}
                    </button>
                  )}
                </Bubble>
              )}

              {state.explanation && (
                <Bubble type="app">
                  <p className="mb-2 font-semibold text-[#1db954]">Here&apos;s the science 🧪</p>
                  <p className="text-sm leading-relaxed text-neutral-300">{state.explanation}</p>
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
                  value={state.query}
                  onChange={(e) => setState((s) => ({ ...s, query: e.target.value }))}
                  placeholder="Or type one…"
                  className="flex-1 rounded-xl border border-neutral-700 bg-[#282828] px-4 py-3 text-white placeholder-neutral-500 outline-none transition focus:border-[#1db954] focus:ring-2 focus:ring-[#1db954]/30"
                  style={{ caretColor: GREEN }}
                  disabled={state.loading}
                />
                <button
                  type="submit"
                  disabled={state.loading || !state.query.trim()}
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

      <SuggestionBubbles
        suggestions={SUGGESTIONS}
        loading={state.loading}
        onSelect={doSearch}
        variant="row"
      />

      {state.toastMessage && (
        <Toast
          message={state.toastMessage}
          onDismiss={() => setState((s) => ({ ...s, toastMessage: null }))}
        />
      )}
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
