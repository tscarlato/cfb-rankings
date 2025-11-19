interface StatsFooterProps {
  teamCount: number;
}

export const StatsFooter = ({ teamCount }: StatsFooterProps) => {
  return (
    <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 p-6">
      <div className="bg-gradient-to-br from-primary/10 to-primary/5 backdrop-blur-sm rounded-xl p-6 shadow-md border border-primary/20">
        <div className="flex items-center gap-4">
          <div className="bg-primary/20 rounded-xl p-4 shadow-sm">
            <i className="fas fa-users text-primary text-3xl"></i>
          </div>
          <div>
            <p className="text-muted-foreground text-sm font-semibold uppercase tracking-wide">Total Teams</p>
            <p className="text-3xl font-bold text-foreground">{teamCount}</p>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-success/10 to-success/5 backdrop-blur-sm rounded-xl p-6 shadow-md border border-success/20">
        <div className="flex items-center gap-4">
          <div className="bg-success/20 rounded-xl p-4 shadow-sm">
            <i className="fas fa-calculator text-success text-3xl"></i>
          </div>
          <div>
            <p className="text-muted-foreground text-sm font-semibold uppercase tracking-wide">Formula</p>
            <p className="text-lg font-bold text-foreground">Custom Algorithm</p>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-warning/10 to-warning/5 backdrop-blur-sm rounded-xl p-6 shadow-md border border-warning/20">
        <div className="flex items-center gap-4">
          <div className="bg-warning/20 rounded-xl p-4 shadow-sm">
            <i className="fas fa-star text-warning text-3xl"></i>
          </div>
          <div>
            <p className="text-muted-foreground text-sm font-semibold uppercase tracking-wide">Data Source</p>
            <p className="text-lg font-bold text-foreground">CFB Data API</p>
          </div>
        </div>
      </div>
    </div>
  );
};
