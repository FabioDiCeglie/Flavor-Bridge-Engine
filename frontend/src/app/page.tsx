import FlavorSearch from "../components/FlavorSearch";

export default function Home() {
  return (
    <div className="min-h-screen bg-[#121212]">
      <div className="mx-auto max-w-7xl px-4 pt-14 pb-8 sm:px-6 sm:pt-20 sm:pb-10 lg:flex lg:items-stretch lg:gap-10">
        {/* Left: project story */}
        <aside className="mb-8 flex flex-col justify-center lg:mb-0 lg:min-w-[240px] lg:max-w-sm lg:shrink-0">
          <p className="text-base leading-relaxed text-neutral-300 sm:text-lg">
            I had to figure out how to represent &apos;Umami&apos; as a mathematical vector so an AI could understand that miso and parmesan share similar chemical properties.
          </p>
        </aside>

        {/* Right: Chat */}
        <main className="min-w-0 flex-1">
          <FlavorSearch />
        </main>
      </div>
    </div>
  );
}
