import { TeamLogo } from "./TeamLogo";
import { getRankColor } from "@/lib/cfb-utils";

interface Game {
  opponent: string;
  opponent_record: string;
  opponent_rank: number;
  won: boolean;
  margin: number;
  value: number;
}

interface Team {
  name: string;
  wins: number;
  losses: number;
  ranking: number;
  games: Game[];
}

interface TeamDetailsProps {
  team: Team;
}

export const TeamDetails = ({ team }: TeamDetailsProps) => {
  return (
    <div className="bg-card rounded-xl p-5 md:p-6 border-4 border-primary/20 shadow-brutal">
      <h3 className="font-display text-2xl md:text-3xl text-primary mb-5 flex items-center gap-3 text-shadow-pop">
        <i className="fas fa-list text-xl md:text-2xl"></i>
        {team.name.toUpperCase()} GAME RESULTS
      </h3>
      <div className="space-y-3">
        {team.games.map((game, index) => {
          const isWin = game.won;
          const resultBadgeClass = isWin
            ? "bg-gradient-success text-white"
            : "bg-gradient-to-r from-red-500 to-red-600 text-white";
          const resultText = isWin ? "W" : "L";
          const borderColor = isWin ? "border-l-success" : "border-l-destructive";
          const bgGlow = isWin ? "bg-success/5 hover:bg-success/10" : "bg-destructive/5 hover:bg-destructive/10";
          const marginDisplay = game.margin > 0 ? `+${game.margin}` : game.margin;
          const rankColor = getRankColor(game.opponent_rank);

          return (
            <div
              key={index}
              className={`
                relative overflow-hidden
                rounded-xl border-2 border-border ${borderColor} border-l-4
                ${bgGlow}
                transition-all duration-200
                hover:shadow-lg hover:scale-[1.01]
                p-4 md:p-5
              `}
            >
              {/* Top Row: Opponent Info + Result Badge */}
              <div className="flex items-center justify-between mb-3 gap-4">
                {/* Opponent Section */}
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-10 h-10 md:w-12 md:h-12 flex-shrink-0">
                    <TeamLogo teamName={game.opponent} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-base md:text-xl text-foreground leading-tight truncate">
                      vs {game.opponent}
                    </div>
                    <div className="text-xs md:text-sm text-muted-foreground font-semibold">
                      {game.opponent_record}
                    </div>
                  </div>
                </div>

                {/* Result Badge */}
                <div className={`
                  ${resultBadgeClass}
                  font-display text-3xl md:text-4xl
                  px-4 py-2 md:px-5 md:py-3
                  rounded-lg shadow-brutal
                  min-w-[60px] md:min-w-[70px]
                  text-center
                  flex-shrink-0
                  text-shadow-pop
                `}>
                  {resultText}
                </div>
              </div>

              {/* Bottom Row: Score + Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 items-center">
                {/* Score Section */}
                <div className="col-span-2 md:col-span-1">
                  <div className="text-xs text-muted-foreground font-bold uppercase tracking-wide mb-1">
                    Final Score
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="font-display text-xl md:text-2xl text-foreground">
                      {/* Placeholder for actual score - using margin as proxy */}
                      FINAL
                    </span>
                    <span className={`font-bold text-lg md:text-xl ${isWin ? 'text-success' : 'text-destructive'}`}>
                      {marginDisplay}
                    </span>
                  </div>
                </div>

                {/* Opponent Rank */}
                <div>
                  <div className="text-xs text-muted-foreground font-bold uppercase tracking-wide mb-1">
                    Opp Rank
                  </div>
                  <div className={`font-mono font-bold text-base md:text-lg ${rankColor}`}>
                    {game.opponent_rank.toFixed(1)}
                  </div>
                </div>

                {/* Margin Category */}
                <div>
                  <div className="text-xs text-muted-foreground font-bold uppercase tracking-wide mb-1">
                    Margin
                  </div>
                  <div className="font-bold text-base md:text-lg text-foreground">
                    {Math.abs(game.margin) <= 8 ? "1-Score" :
                     Math.abs(game.margin) <= 16 ? "2-Score" : "Blowout"}
                  </div>
                </div>

                {/* Game Value */}
                <div>
                  <div className="text-xs text-muted-foreground font-bold uppercase tracking-wide mb-1">
                    Value
                  </div>
                  <div className="font-mono font-bold text-base md:text-lg text-primary">
                    {game.value.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
