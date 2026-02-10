"use client";

export default function Toast({
  message,
  onDismiss,
}: {
  message: string;
  onDismiss: () => void;
}) {
  return (
    <div
      role="alert"
      className="fixed top-6 left-1/2 z-50 -translate-x-1/2 rounded-xl border border-red-500/30 bg-[#282828] px-4 py-3 text-sm text-white shadow-lg"
    >
      <div className="flex items-center gap-3">
        <span>{message}</span>
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 rounded p-1 text-neutral-400 transition hover:bg-white/10 hover:text-white"
          aria-label="Dismiss"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
