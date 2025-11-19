import { ThemeToggle } from "./ThemeToggle";

interface HeaderProps {
  year: string;
  onRefresh: () => void;
}

export const Header = ({ year, onRefresh }: HeaderProps) => {
  return (
    <div className="bg-gradient-primary rounded-2xl shadow-brutal p-6 md:p-8 text-white relative overflow-hidden animate-bounce-in">
      {/* Diagonal stripes texture */}
      <div className="absolute inset-0 texture-stripes opacity-50"></div>

      {/* Main content */}
      <div className="relative z-10">
        <div className="flex items-start md:items-center justify-between mb-3 flex-col md:flex-row gap-4">
          <div className="flex items-center gap-3 md:gap-5">
            {/* Trophy icon - bigger and chunkier */}
            <div className="bg-accent/90 backdrop-blur-sm rounded-xl p-3 md:p-4 shadow-brutal animate-pop">
              <i className="fas fa-trophy text-secondary text-4xl md:text-6xl drop-shadow-lg"></i>
            </div>

            <div>
              {/* SHOUTY headline with Bebas Neue */}
              <h1 className="font-display text-5xl md:text-7xl font-bold tracking-wide text-shadow-brutal leading-none mb-2">
                CFB RANKINGS
              </h1>
              <div className="flex items-center gap-2 md:gap-3">
                <span className="font-display text-3xl md:text-4xl text-accent text-shadow-pop">
                  {year}
                </span>
                <span className="text-white/40 text-2xl">•</span>
                <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-lg text-xs md:text-sm font-bold shadow-lg uppercase tracking-wide">
                  FBS
                </span>
              </div>
            </div>
          </div>

          {/* Action buttons - chunky */}
          <div className="flex items-center gap-3 flex-wrap">
            <ThemeToggle />
            <button
              onClick={onRefresh}
              className="bg-accent text-secondary px-5 py-3 rounded-xl hover:bg-accent/90 transition-all font-bold shadow-brutal hover:shadow-xl flex items-center gap-2 hover:scale-105 active:scale-95 uppercase tracking-wide text-sm md:text-base"
            >
              <i className="fas fa-sync-alt text-lg"></i>
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>

        {/* Tagline */}
        <p className="text-white/90 text-base md:text-lg font-bold max-w-3xl">
          CREATE YOUR OWN RANKINGS • TWEAK THE FORMULA • SHARE YOUR HOT TAKES
        </p>
      </div>
    </div>
  );
};
