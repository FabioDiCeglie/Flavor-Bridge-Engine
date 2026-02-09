"use client";

const FLOATING_POSITIONS = [
  { left: "-5.5rem", top: "8%" },
  { right: "-4rem", top: "22%" },
  { left: "-5rem", top: "45%" },
  { right: "-3.5rem", top: "58%" },
  { left: "-5.5rem", top: "68%" },
  { right: "-4rem", top: "35%" },
  { left: "50%", top: "-2.5rem", style: { transform: "translateX(-50%)" } },
  { left: "85%", top: "72%", style: { transform: "translateX(-50%)" } },
];

type Props = {
  suggestions: string[];
  loading: boolean;
  onSelect: (ingredient: string) => void;
  variant: "floating" | "row";
};

export default function SuggestionBubbles({ suggestions, loading, onSelect, variant }: Props) {
  if (variant === "floating") {
    return (
      <>
        {suggestions.map((ingredient, i) => {
          const pos = FLOATING_POSITIONS[i] ?? FLOATING_POSITIONS[0];
          return (
            <button
              key={ingredient}
              type="button"
              onClick={() => !loading && onSelect(ingredient)}
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
      </>
    );
  }

  return (
    <div className="flex shrink-0 flex-wrap justify-center gap-2 pt-4 pb-1 lg:hidden">
      {suggestions.map((ingredient, i) => (
        <button
          key={ingredient}
          type="button"
          onClick={() => !loading && onSelect(ingredient)}
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
  );
}
