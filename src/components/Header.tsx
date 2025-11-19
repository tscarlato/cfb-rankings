interface HeaderProps {
  year: string;
  onRefresh: () => void;
}

export const Header = ({ year, onRefresh }: HeaderProps) => {
  return (
    <div className="bg-gradient-primary rounded-2xl shadow-2xl p-8 text-white relative overflow-hidden">
      <div className="absolute inset-0 bg-black/10"></div>
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 shadow-lg">
              <i className="fas fa-trophy text-yellow-300 text-5xl drop-shadow-lg"></i>
            </div>
            <div>
              <h1 className="text-4xl md:text-5xl font-extrabold mb-2 tracking-tight">
                CFB Rankings <span className="text-yellow-300">{year}</span>
              </h1>
              <div className="flex items-center gap-3 text-blue-100 text-lg">
                <span className="bg-white/20 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-semibold shadow-md">
                  FBS
                </span>
                <span className="text-white/50">•</span>
                <span className="bg-white/20 backdrop-blur-sm px-4 py-1.5 rounded-full text-sm font-semibold shadow-md">
                  Regular Season
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={onRefresh}
            className="bg-white text-primary px-6 py-3 rounded-xl hover:bg-blue-50 transition-all font-bold shadow-lg hover:shadow-xl flex items-center gap-2 hover:scale-105 active:scale-95"
          >
            <i className="fas fa-sync-alt"></i>
            Refresh
          </button>
        </div>
        <p className="text-blue-100 text-lg font-medium">
          Custom ranking system based on wins, strength of schedule, and margin of victory
        </p>
      </div>
    </div>
  );
};
