import { useState, useEffect } from "react";
import { TeamLogo } from "@/components/TeamLogo";
import { RankBadge } from "@/components/RankBadge";
import { TeamDetails } from "@/components/TeamDetails";
import { Header } from "@/components/Header";
import { Controls } from "@/components/Controls";
import { ShareButton } from "@/components/ShareButton";
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
  // Initialize state from URL params if present (for shared links)
  const getInitialParams = (): FormulaParams => {
    const urlParams = new URLSearchParams(window.location.search);

    if (urlParams.has('wl')) {
      return {
        win_loss_multiplier: parseFloat(urlParams.get('wl') || '1.0'),
        one_score_multiplier: parseFloat(urlParams.get('os') || '1.0'),
        two_score_multiplier: parseFloat(urlParams.get('ts') || '1.3'),
        three_score_multiplier: parseFloat(urlParams.get('ths') || '1.5'),
        strength_of_schedule_multiplier: parseFloat(urlParams.get('sos') || '1.0'),
      };
    }

    return {
      win_loss_multiplier: 1.0,
      one_score_multiplier: 1.0,
      two_score_multiplier: 1.3,
      three_score_multiplier: 1.5,
      strength_of_schedule_multiplier: 1.0,
    };
  };

  const [allTeams, setAllTeams] = useState<Team[]>([]);
  const [filteredTeams, setFilteredTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedTeam, setExpandedTeam] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [year, setYear] = useState("2025");
  const [week, setWeek] = useState("");
  const [seasonType, setSeasonType] = useState("regular");
  const [formulaParams, setFormulaParams] = useState<FormulaParams>(getInitialParams());

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
    <div className="min-h-screen bg-background texture-paper p-4 md:p-8">
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

        {/* Big prominent share button */}
        <div className="animate-pop">
          <ShareButton
            year={year}
            week={week}
            seasonType={seasonType}
            formulaParams={formulaParams}
          />
        </div>

        <div className="bg-card rounded-xl shadow-brutal overflow-hidden border-4 border-primary/20 animate-slide-up">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gradient-maroon text-white texture-stripes">
                <tr>
                  <th className="px-4 md:px-6 py-4 md:py-5 text-left font-display text-xl md:text-2xl tracking-wide">RANK</th>
                  <th className="px-4 md:px-6 py-4 md:py-5 text-left font-display text-xl md:text-2xl tracking-wide">TEAM</th>
                  <th className="px-4 md:px-6 py-4 md:py-5 text-center font-display text-xl md:text-2xl tracking-wide">RECORD</th>
                  <th className="px-4 md:px-6 py-4 md:py-5 text-right font-display text-xl md:text-2xl tracking-wide">RATING</th>
                  <th className="px-4 md:px-6 py-4 md:py-5 text-center font-display text-xl md:text-2xl tracking-wide"></th>
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
                        className="border-b-2 border-border/50 cursor-pointer transition-all duration-200 hover:bg-accent/10 group"
                        onClick={() => toggleTeamDetails(team.name)}
                      >
                        <td className="px-4 md:px-6 py-4 md:py-5">
                          <RankBadge rank={rank} />
                        </td>
                        <td className="px-4 md:px-6 py-4 md:py-5">
                          <div className="flex items-center gap-3 md:gap-4">
                            <div className="w-12 h-12 md:w-16 md:h-16 flex-shrink-0">
                              <TeamLogo teamName={team.name} />
                            </div>
                            <span className="font-bold text-base md:text-xl text-foreground group-hover:text-primary transition-colors">
                              {team.name}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 md:px-6 py-4 md:py-5 text-center">
                          <span className="inline-flex items-center justify-center bg-gradient-to-br from-muted to-muted/70 px-4 py-2 md:px-5 md:py-2.5 rounded-xl font-bold text-sm md:text-base text-foreground min-w-[70px] md:min-w-[80px] shadow-lg border-2 border-border">
                            {team.wins}-{team.losses}
                          </span>
                        </td>
                        <td className="px-4 md:px-6 py-4 md:py-5 text-right">
                          <span className="font-display text-2xl md:text-3xl font-bold text-primary">
                            {team.ranking.toFixed(2)}
                          </span>
                        </td>
                        <td className="px-4 md:px-6 py-4 md:py-5 text-center">
                          <div className="inline-flex items-center justify-center bg-primary/10 group-hover:bg-primary/20 rounded-lg p-2 md:p-3 transition-all duration-200">
                            <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'} text-primary text-sm md:text-base transition-transform duration-200 group-hover:scale-110`}></i>
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
