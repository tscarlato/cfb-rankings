interface RankBadgeProps {
  rank: number;
}

export const RankBadge = ({ rank }: RankBadgeProps) => {
  // Determine gradient and style based on rank tier
  let gradientClass = "";
  let borderColor = "";
  let iconClass = "";

  if (rank <= 4) {
    // Top 4 (Playoff spots) - GOLD, extra special
    gradientClass = "bg-gradient-warning";
    borderColor = "border-4 border-accent/50";
    iconClass = "fas fa-crown";
  } else if (rank <= 12) {
    // Top 12 (CFP bracket) - GREEN
    gradientClass = "bg-gradient-success";
    borderColor = "border-4 border-success/30";
    iconClass = "";
  } else if (rank <= 25) {
    // Top 25 - ACCENT
    gradientClass = "bg-gradient-accent";
    borderColor = "border-4 border-accent/30";
    iconClass = "";
  } else {
    // Everyone else - MAROON
    gradientClass = "bg-gradient-maroon";
    borderColor = "border-2 border-secondary/30";
    iconClass = "";
  }

  return (
    <div className="relative group">
      {/* Main badge with chunky 3D shadow */}
      <div
        className={`
          w-16 h-16 md:w-20 md:h-20
          flex flex-col items-center justify-center
          rounded-xl
          ${gradientClass}
          ${borderColor}
          shadow-brutal
          transition-all duration-200
          group-hover:scale-110 group-hover:shadow-xl
          text-white
          relative
        `}
      >
        {/* Crown icon for top 4 */}
        {iconClass && (
          <i className={`${iconClass} text-accent text-xs md:text-sm mb-0.5 drop-shadow-lg`}></i>
        )}

        {/* Rank number - HUGE and bold */}
        <span className="font-display text-2xl md:text-4xl leading-none text-shadow-pop">
          {rank}
        </span>
      </div>

      {/* Animated highlight for top ranks */}
      {rank <= 4 && (
        <div className="absolute -inset-1 bg-accent/20 rounded-xl blur-sm animate-pulse -z-10"></div>
      )}
    </div>
  );
};
