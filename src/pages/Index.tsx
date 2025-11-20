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
          {/* Header - Desktop Only */}
          <div className="hidden md:block bg-gradient-maroon text-white texture-stripes px-6 py-5">
            <div className="grid grid-cols-12 gap-4 items-center">
              <div className="col-span-1 font-display text-xl tracking-wide">RANK</div>
              <div className="col-span-5 font-display text-xl tracking-wide">TEAM</div>
              <div className="col-span-2 text-center font-display text-xl tracking-wide">RECORD</div>
              <div className="col-span-2 text-right font-display text-xl tracking-wide">RATING</div>
              <div className="col-span-2"></div>
            </div>
          </div>

          {/* Team Cards */}
          <div className="divide-y-2 divide-border/50">
            {filteredTeams.map((team, index) => {
              const rank = index + 1;
              const isExpanded = expandedTeam === team.name;

              return (
                <div key={team.name}>
                  {/* Team Card */}
                  <div
                    onClick={() => toggleTeamDetails(team.name)}
                    className="cursor-pointer transition-all duration-200 hover:bg-accent/10 group p-4 md:px-6 md:py-5"
                  >
                    <div className="grid grid-cols-12 gap-3 md:gap-4 items-center">
                      {/* Rank Badge - Ticket Stub Style */}
                      <div className="col-span-2 md:col-span-1">
                        <div className="relative">
                          {/* Ticket stub with perforation */}
                          <div className="border-r-2 border-dashed border-border/50 pr-2 md:pr-3">
                            <RankBadge rank={rank} />
                          </div>
                        </div>
                      </div>

                      {/* Team Info */}
                      <div className="col-span-6 md:col-span-5 overflow-hidden pl-1">
                        <div className="flex items-center gap-2 md:gap-3">
                          <div className="w-8 h-8 md:w-12 md:h-12 flex-shrink-0">
                            <TeamLogo teamName={team.name} />
                          </div>
                          <div className="min-w-0 flex-1 overflow-hidden">
                            <div className="font-bold text-sm md:text-lg text-foreground group-hover:text-primary transition-colors truncate">
                              {team.name}
                            </div>
                            {/* Mobile: Show record below name */}
                            <div className="md:hidden text-xs text-muted-foreground font-semibold">
                              {team.wins}-{team.losses}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Record - Desktop Only */}
                      <div className="hidden md:block md:col-span-2 text-center">
                        <span className="inline-flex items-center justify-center bg-gradient-to-br from-muted to-muted/70 px-4 py-2 rounded-lg font-bold text-sm text-foreground shadow-md border-2 border-border">
                          {team.wins}-{team.losses}
                        </span>
                      </div>

                      {/* Rating */}
                      <div className="col-span-3 md:col-span-2 text-right">
                        <div className="text-xs text-muted-foreground font-bold uppercase tracking-wide mb-0.5 md:hidden">
                          Rating
                        </div>
                        <span className="font-display text-xl md:text-2xl font-bold text-primary">
                          {team.ranking.toFixed(2)}
                        </span>
                      </div>

                      {/* Expand Button */}
                      <div className="col-span-1 md:col-span-2 text-right">
                        <div className="inline-flex items-center justify-center bg-primary/10 group-hover:bg-primary/20 rounded-lg p-2 md:p-3 transition-all duration-200">
                          <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'} text-primary text-xs md:text-sm transition-transform duration-200 group-hover:scale-110`}></i>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="bg-gradient-to-r from-muted/30 to-muted/10 animate-accordion-down px-4 py-5 md:px-6 md:py-6">
                      <TeamDetails team={team} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <StatsFooter teamCount={filteredTeams.length} />
        </div>
      </div>
    </div>
  );
};

export default Index;
