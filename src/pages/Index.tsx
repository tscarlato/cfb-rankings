import { useState, useEffect } from "react";
import { TeamLogo } from "@/components/TeamLogo";
import { RankBadge } from "@/components/RankBadge";
import { TeamDetails } from "@/components/TeamDetails";
import { Header } from "@/components/Header";
import { Controls } from "@/components/Controls";
import { StatsFooter } from "@/components/StatsFooter";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ErrorDisplay } from "@/components/ErrorDisplay";
import { getTeamLogo, getRankColor } from "@/lib/cfb-utils";

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

interface FormulaParams {
  win_loss_multiplier: number;
  one_score_multiplier: number;
  two_score_multiplier: number;
  three_score_multiplier: number;
  strength_of_schedule_multiplier: number;
}

const Index = () => {
  const [allTeams, setAllTeams] = useState<Team[]>([]);
  const [filteredTeams, setFilteredTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTeam, setExpandedTeam] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [year, setYear] = useState("2024");
  const [week, setWeek] = useState("");
  const [seasonType, setSeasonType] = useState("regular");
  const [formulaParams, setFormulaParams] = useState<FormulaParams>({
    win_loss_multiplier: 1.0,
    one_score_multiplier: 1.0,
    two_score_multiplier: 1.3,
    three_score_multiplier: 1.5,
    strength_of_schedule_multiplier: 1.0,
  });

  const fetchRankings = async () => {
    setLoading(true);
    setError(null);
    setExpandedTeam(null);

    try {
      let url = `/rankings?year=${year}&season_type=${seasonType}`;
      if (week) url += `&week=${week}`;
      
      // Add formula parameters
      url += `&win_loss_multiplier=${formulaParams.win_loss_multiplier}`;
      url += `&one_score_multiplier=${formulaParams.one_score_multiplier}`;
      url += `&two_score_multiplier=${formulaParams.two_score_multiplier}`;
      url += `&three_score_multiplier=${formulaParams.three_score_multiplier}`;
      url += `&strength_of_schedule_multiplier=${formulaParams.strength_of_schedule_multiplier}`;

      const response = await fetch(url);
      if (!response.ok) throw new Error(`API returned ${response.status}`);

      const data = await response.json();
      setAllTeams(data.teams || []);
      setFilteredTeams(data.teams || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load rankings");
      console.error('Error fetching rankings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRankings();
  }, [year, week, seasonType, formulaParams]);

  useEffect(() => {
    const filtered = allTeams.filter((team) =>
      team.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredTeams(filtered);
  }, [searchQuery, allTeams]);

  const toggleTeamDetails = (teamName: string) => {
    setExpandedTeam(expandedTeam === teamName ? null : teamName);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background p-4 md:p-8">
        <div className="max-w-7xl mx-auto">
          <ErrorDisplay error={error} onRetry={fetchRankings} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8 font-[Inter]">
      <div className="max-w-7xl mx-auto space-y-6 animate-fade-in">
        <Header year={year} onRefresh={fetchRankings} />
        
        <Controls
          year={year}
          week={week}
          seasonType={seasonType}
          searchQuery={searchQuery}
          formulaParams={formulaParams}
          onYearChange={setYear}
          onWeekChange={setWeek}
          onSeasonTypeChange={setSeasonType}
          onSearchChange={setSearchQuery}
          onFormulaChange={setFormulaParams}
          onApplyFormula={fetchRankings}
        />

        <div className="bg-card rounded-2xl shadow-xl overflow-hidden border border-border animate-slide-up">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-to-r from-slate-800 to-slate-700 text-white">
                <tr>
                  <th className="px-6 py-5 text-left font-bold text-lg tracking-wide">Rank</th>
                  <th className="px-6 py-5 text-left font-bold text-lg tracking-wide">Team</th>
                  <th className="px-6 py-5 text-center font-bold text-lg tracking-wide">Record</th>
                  <th className="px-6 py-5 text-right font-bold text-lg tracking-wide">Rating</th>
                  <th className="px-6 py-5 text-center font-bold text-lg tracking-wide">Details</th>
                </tr>
              </thead>
              <tbody>
                {filteredTeams.map((team, index) => {
                  const rank = index + 1;
                  const isExpanded = expandedTeam === team.name;
                  
                  return (
                    <>
                      <tr
                        key={team.name}
                        className="border-b border-border cursor-pointer transition-all duration-200 hover:bg-muted/50 hover:scale-[1.01] hover:shadow-md"
                        onClick={() => toggleTeamDetails(team.name)}
                      >
                        <td className="px-6 py-5">
                          <RankBadge rank={rank} />
                        </td>
                        <td className="px-6 py-5">
                          <div className="flex items-center gap-4">
                            <TeamLogo teamName={team.name} />
                            <span className="font-bold text-lg text-foreground">{team.name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-5 text-center">
                          <span className="inline-flex items-center justify-center bg-muted px-5 py-2.5 rounded-xl font-bold text-foreground min-w-[80px] shadow-sm">
                            {team.wins}-{team.losses}
                          </span>
                        </td>
                        <td className="px-6 py-5 text-right">
                          <span className={`font-mono text-2xl font-bold ${getRankColor(team.ranking)}`}>
                            {team.ranking.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-6 py-5 text-center">
                          <div className="inline-flex items-center justify-center bg-primary/10 hover:bg-primary/20 rounded-lg p-3 transition-all duration-200 group">
                            <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'} text-primary transition-transform duration-200 group-hover:scale-110`}></i>
                          </div>
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-gradient-to-r from-muted/30 to-muted/10 animate-accordion-down">
                          <td colSpan={5} className="px-6 py-6">
                            <TeamDetails team={team} />
                          </td>
                        </tr>
                      )}
                    </>
                  );
                })}
              </tbody>
            </table>
          </div>

          <StatsFooter teamCount={filteredTeams.length} />
        </div>
      </div>
    </div>
  );
};

export default Index;
