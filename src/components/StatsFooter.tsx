interface StatsFooterProps {
  teamCount: number;
}

export const StatsFooter = ({ teamCount }: StatsFooterProps) => {
  return (
    <div className="p-5 md:p-6 bg-muted/30 rounded-t-xl border-t-4 border-primary/20">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-primary text-white rounded-xl p-4 md:p-5 shadow-brutal border-2 border-primary/30 group hover:scale-105 transition-transform">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="bg-white/20 rounded-lg p-3 shadow-lg">
              <i className="fas fa-users text-2xl md:text-3xl"></i>
            </div>
            <div>
              <p className="text-xs md:text-sm font-bold uppercase tracking-wide opacity-90">Total Teams</p>
              <p className="text-2xl md:text-3xl font-display font-bold text-shadow-pop">{teamCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-success text-white rounded-xl p-4 md:p-5 shadow-brutal border-2 border-success/30 group hover:scale-105 transition-transform">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="bg-white/20 rounded-lg p-3 shadow-lg">
              <i className="fas fa-calculator text-2xl md:text-3xl"></i>
            </div>
            <div>
              <p className="text-xs md:text-sm font-bold uppercase tracking-wide opacity-90">Formula</p>
              <p className="text-base md:text-lg font-bold">Custom Algorithm</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-accent text-secondary rounded-xl p-4 md:p-5 shadow-brutal border-2 border-accent/30 group hover:scale-105 transition-transform">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="bg-secondary/20 rounded-lg p-3 shadow-lg">
              <i className="fas fa-database text-2xl md:text-3xl"></i>
            </div>
            <div>
              <p className="text-xs md:text-sm font-bold uppercase tracking-wide opacity-90">Data Source</p>
              <p className="text-base md:text-lg font-bold">CFB Data API</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
