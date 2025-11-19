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
          const resultClass = game.won
            ? "bg-gradient-success text-white"
            : "bg-gradient-to-r from-red-500 to-red-600 text-white";
          const resultText = game.won ? "W" : "L";
          const marginClass = game.margin > 0 ? "text-success" : "text-destructive";
          const rankColor = getRankColor(game.opponent_rank);

          return (
            <div
              key={index}
              className="flex items-center justify-between p-5 bg-background rounded-xl border-2 border-border hover:border-primary/50 transition-all shadow-sm hover:shadow-md"
            >
              <div className="flex items-center gap-4 flex-1">
                <span className={`font-bold px-4 py-2.5 rounded-lg ${resultClass} shadow-md min-w-[48px] text-center`}>
                  {resultText}
                </span>
                <TeamLogo teamName={game.opponent} />
                <div>
                  <div className="font-bold text-foreground text-lg">{game.opponent}</div>
                  <div className="text-muted-foreground font-mono text-sm">{game.opponent_record}</div>
                </div>
              </div>
              <div className="flex items-center gap-8">
                <div className="text-center">
                  <div className="text-xs text-muted-foreground font-semibold mb-1 uppercase tracking-wide">
                    Opp Rank
                  </div>
                  <div className={`font-mono font-bold ${rankColor} text-lg`}>
                    {game.opponent_rank.toFixed(2)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-muted-foreground font-semibold mb-1 uppercase tracking-wide">
                    Margin
                  </div>
                  <div className={`font-mono font-bold ${marginClass} text-lg`}>
                    {game.margin > 0 ? "+" : ""}
                    {game.margin}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-muted-foreground font-semibold mb-1 uppercase tracking-wide">
                    Value
                  </div>
                  <div className="font-mono font-bold text-primary text-lg">{game.value.toFixed(2)}</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
