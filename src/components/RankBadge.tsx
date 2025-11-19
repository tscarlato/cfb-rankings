interface RankBadgeProps {
  rank: number;
}

export const RankBadge = ({ rank }: RankBadgeProps) => {
  let badgeClass = "w-14 h-14 flex items-center justify-center rounded-xl font-extrabold text-xl text-white shadow-lg transition-transform duration-200 hover:scale-110";
  
  if (rank <= 5) {
    badgeClass += " bg-gradient-warning";
  } else if (rank <= 10) {
    badgeClass += " bg-gradient-success";
  } else if (rank <= 25) {
    badgeClass += " bg-gradient-accent";
  } else {
    badgeClass += " bg-gradient-primary";
  }

  return <div className={badgeClass}>{rank}</div>;
};
