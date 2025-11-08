import React, { useState, useMemo, useEffect } from 'react';
import { ChevronUp, ChevronDown, Minus, Settings, Calendar, Search, RefreshCw, Trophy } from 'lucide-react';

const App = () => {
  const [scoreMultiplier, setScoreMultiplier] = useState(1.3);
  const [sosMultiplier, setSosMultiplier] = useState(1.0);
  const [showControls, setShowControls] = useState(false);
  const [selectedYear, setSelectedYear] = useState(2024);
  const [selectedWeek, setSelectedWeek] = useState('');
  const [selectedSeason, setSelectedSeason] = useState('regular');
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedTeam, setExpandedTeam] = useState(null);

  // Generate year options from 1980 to current year
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: currentYear - 1980 + 1 }, (_, i) => currentYear - i);

  // Week options - using "Current Week" as default
  const weekOptions = [
    { value: '', label: 'All Weeks' },
    ...Array.from({ length: 15 }, (_, i) => ({ value: i + 1, label: `Week ${i + 1}` }))
  ];

  // Team logos from ESPN
  const getTeamLogo = (teamName) => {
    const teamLogos = {
      // SEC
      'Alabama': '333', 'Georgia': '61', 'LSU': '99', 'Florida': '57',
      'Tennessee': '2633', 'Texas': '251', 'Texas A&M': '245', 'Auburn': '2',
      'Ole Miss': '145', 'Mississippi State': '344', 'Arkansas': '8',
      'Kentucky': '96', 'South Carolina': '2579', 'Missouri': '142',
      'Vanderbilt': '238', 'Oklahoma': '201',
      
      // Big Ten
      'Ohio State': '194', 'Michigan': '130', 'Penn State': '213', 'USC': '30',
      'Oregon': '2483', 'Washington': '264', 'UCLA': '26', 'Michigan State': '127',
      'Iowa': '2294', 'Wisconsin': '275', 'Nebraska': '158', 'Minnesota': '135',
      'Indiana': '84', 'Purdue': '2509', 'Maryland': '120', 'Rutgers': '164',
      'Northwestern': '77', 'Illinois': '356',
      
      // ACC
      'Clemson': '228', 'Florida State': '52', 'Miami': '2390',
      'North Carolina': '153', 'NC State': '152', 'Louisville': '97',
      'Duke': '150', 'Virginia Tech': '259', 'Virginia': '258',
      'Georgia Tech': '59', 'Boston College': '103', 'Syracuse': '183',
      'Wake Forest': '154', 'Pittsburgh': '221', 'Stanford': '24',
      'California': '25', 'SMU': '2567',
      
      // Big 12
      'Kansas State': '2306', 'TCU': '2628', 'Baylor': '239', 'Texas Tech': '2641',
      'Oklahoma State': '197', 'West Virginia': '277', 'Iowa State': '66',
      'Kansas': '2305', 'BYU': '252', 'Utah': '254', 'Colorado': '38',
      'Arizona': '12', 'Arizona State': '9', 'Cincinnati': '2132',
      'Houston': '248', 'UCF': '2116',
      
      // Independent
      'Notre Dame': '87', 'UConn': '41', 'UMass': '113', 'Army': '349',
      
      // Group of 5
      'Memphis': '235', 'Tulane': '2655', 'Navy': '2426', 'Boise State': '68',
      'San Diego State': '21', 'Fresno State': '278', 'Air Force': '2005',
      'App State': '2026', 'Appalachian State': '2026', 'Coastal Carolina': '324',
      'James Madison': '256', 'Marshall': '276', 'Georgia Southern': '290',
      'Liberty': '2335', 'Western Kentucky': '98', 'Toledo': '2649'
    };
    
    const teamId = teamLogos[teamName];
    return teamId ? `https://a.espncdn.com/i/teamlogos/ncaa/500/${teamId}.png` : null;
  };

  // Fetch rankings from API
  const fetchRankings = async () => {
    setLoading(true);
    setError(null);
    setExpandedTeam(null);

    try {
      let url = `/rankings?year=${selectedYear}&season_type=${selectedSeason}`;
      if (selectedWeek) url += `&week=${selectedWeek}`;
      url += `&win_loss_multiplier=1.0`;
      url += `&one_score_multiplier=1.0`;
      url += `&two_score_multiplier=${scoreMultiplier}`;
      url += `&three_score_multiplier=${sosMultiplier}`;
      url += `&strength_of_schedule_multiplier=1.0`;

      const response = await fetch(url);
      if (!response.ok) throw new Error(`Failed to fetch rankings: ${response.status}`);
      
      const data = await response.json();
      setTeams(data.teams || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount and when parameters change
  useEffect(() => {
    fetchRankings();
  }, [selectedYear, selectedWeek, selectedSeason, scoreMultiplier, sosMultiplier]);

  // Filter teams by search
  const filteredTeams = useMemo(() => {
    if (!searchQuery) return teams;
    return teams.filter(team => 
      team.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [teams, searchQuery]);

  // Sort teams by ranking
  const rankedTeams = useMemo(() => {
    return [...filteredTeams].sort((a, b) => b.ranking - a.ranking);
  }, [filteredTeams]);

  const getRankColor = (rank) => {
    if (rank <= 5) return 'from-orange-500 to-red-600';
    if (rank <= 10) return 'from-green-500 to-emerald-600';
    if (rank <= 25) return 'from-blue-500 to-indigo-600';
    return 'from-slate-600 to-slate-700';
  };

  const getMarginColor = (margin) => {
    if (margin > 0) return 'text-green-600';
    if (margin < 0) return 'text-red-600';
    return 'text-slate-600';
  };

  const getRatingColor = (rating) => {
    if (rating > 15) return 'text-green-600';
    if (rating > 10) return 'text-green-700';
    if (rating > 5) return 'text-blue-600';
    if (rating > 0) return 'text-slate-700';
    if (rating > -5) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex flex-col gap-4">
            {/* Title Row */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-orange-500/20 rounded-xl p-2 sm:p-3">
                  <Trophy className="w-6 h-6 sm:w-8 sm:h-8 text-orange-500" />
                </div>
                <div>
                  <h1 className="text-2xl sm:text-4xl font-bold tracking-tight">
                    CFB Power Rankings
                  </h1>
                  <p className="text-slate-400 text-sm sm:text-base mt-1">
                    {selectedYear} • FBS • {selectedSeason === 'regular' ? 'Regular Season' : 'Regular + Postseason'}
                  </p>
                </div>
              </div>
              <button 
                onClick={fetchRankings}
                className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-600"
              >
                <RefreshCw size={18} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
            </div>

            {/* Controls Row */}
            <div className="flex flex-col sm:flex-row gap-3">
              {/* Year Selector */}
              <div className="flex items-center gap-2 bg-slate-800 rounded-lg border border-slate-600 px-3 py-2 flex-1 sm:flex-initial">
                <Calendar size={18} className="text-slate-400" />
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(Number(e.target.value))}
                  className="bg-transparent text-white font-medium outline-none cursor-pointer w-full sm:w-auto"
                >
                  {years.map(year => (
                    <option key={year} value={year} className="bg-slate-800">{year}</option>
                  ))}
                </select>
              </div>

              {/* Week Selector */}
              <select
                value={selectedWeek}
                onChange={(e) => setSelectedWeek(e.target.value)}
                className="bg-slate-800 text-white font-medium rounded-lg border border-slate-600 px-3 py-2 outline-none cursor-pointer flex-1 sm:flex-initial"
              >
                {weekOptions.map(option => (
                  <option key={option.value} value={option.value} className="bg-slate-800">
                    {option.label}
                  </option>
                ))}
              </select>

              {/* Season Type Selector */}
              <select
                value={selectedSeason}
                onChange={(e) => setSelectedSeason(e.target.value)}
                className="bg-slate-800 text-white font-medium rounded-lg border border-slate-600 px-3 py-2 outline-none cursor-pointer flex-1 sm:flex-initial"
              >
                <option value="regular" className="bg-slate-800">Regular Season</option>
                <option value="both" className="bg-slate-800">Regular + Postseason</option>
              </select>

              {/* Customize Button */}
              <button 
                onClick={() => setShowControls(!showControls)}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-600"
              >
                <Settings size={20} />
                <span className="sm:inline">Customize</span>
              </button>
            </div>

            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
              <input
                type="text"
                placeholder="Find your team..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-800 text-white rounded-lg border border-slate-600 pl-10 pr-4 py-2 outline-none focus:border-orange-500 transition-colors"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Control Panel */}
        {showControls && (
          <div className="mb-6 sm:mb-8 bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-semibold mb-4 flex items-center gap-2">
              <Settings size={20} className="text-orange-500" />
              Formula Controls
            </h2>
            
            <div className="grid sm:grid-cols-2 gap-4 sm:gap-6">
              {/* Score Margin Multiplier */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className="text-sm font-medium text-slate-300">
                    2-Score Game Weight (9-16pts)
                  </label>
                  <span className="text-lg font-bold text-orange-500">{scoreMultiplier.toFixed(1)}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={scoreMultiplier}
                  onChange={(e) => setScoreMultiplier(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-orange-500"
                />
              </div>

              {/* 3+ Score Multiplier */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className="text-sm font-medium text-slate-300">
                    3+ Score Game Weight (>16pts)
                  </label>
                  <span className="text-lg font-bold text-orange-500">{sosMultiplier.toFixed(1)}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={sosMultiplier}
                  onChange={(e) => setSosMultiplier(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-orange-500"
                />
              </div>
            </div>

            <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-slate-700">
              <p className="text-sm text-slate-400">
                <strong>Formula:</strong> (W/L × Margin Multiplier) + ((Opponent Rank ÷ 100) × SoS Multiplier)
              </p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-12 text-center">
            <RefreshCw className="inline-block w-12 h-12 text-orange-500 animate-spin mb-4" />
            <p className="text-xl text-slate-300 font-semibold">Loading rankings...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-slate-800/50 backdrop-blur-sm border border-red-700 rounded-xl p-12 text-center">
            <p className="text-xl text-red-400 font-semibold mb-4">Error: {error}</p>
            <button
              onClick={fetchRankings}
              className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg font-semibold"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Rankings Table */}
        {!loading && !error && (
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
            {/* Table Header */}
            <div className="bg-slate-900/80 px-4 sm:px-6 py-3 sm:py-4 grid grid-cols-12 gap-2 sm:gap-4 text-xs sm:text-sm font-semibold text-slate-400 border-b border-slate-700">
              <div className="col-span-1">Rank</div>
              <div className="col-span-6 sm:col-span-5">Team</div>
              <div className="col-span-2 text-center hidden sm:block">Record</div>
              <div className="col-span-3 sm:col-span-2 text-right">Rating</div>
              <div className="col-span-2 sm:col-span-1 text-center">Details</div>
            </div>

            {/* Team Rows */}
            <div className="max-h-[calc(100vh-400px)] overflow-y-auto">
              {rankedTeams.map((team, index) => {
                const rank = index + 1;
                const logoUrl = getTeamLogo(team.name);
                const isExpanded = expandedTeam === team.name;

                return (
                  <React.Fragment key={team.name}>
                    {/* Main Row */}
                    <div
                      onClick={() => setExpandedTeam(isExpanded ? null : team.name)}
                      className="px-4 sm:px-6 py-3 sm:py-4 grid grid-cols-12 gap-2 sm:gap-4 items-center hover:bg-slate-700/30 transition-all duration-200 border-b border-slate-700/50 cursor-pointer group"
                    >
                      {/* Rank */}
                      <div className="col-span-1">
                        <div className={`w-8 h-8 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center font-bold text-sm sm:text-lg bg-gradient-to-br ${getRankColor(rank)} text-white shadow-lg`}>
                          {rank}
                        </div>
                      </div>

                      {/* Team */}
                      <div className="col-span-6 sm:col-span-5 flex items-center gap-2 sm:gap-3 min-w-0">
                        <div className="w-8 h-8 sm:w-10 sm:h-10 flex-shrink-0 bg-slate-700 rounded-lg flex items-center justify-center overflow-hidden">
                          {logoUrl ? (
                            <img 
                              src={logoUrl} 
                              alt={team.name}
                              className="w-full h-full object-contain"
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          ) : (
                            <span className="text-xs font-bold text-slate-400">
                              {team.name.substring(0, 3)}
                            </span>
                          )}
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="font-semibold text-sm sm:text-lg text-slate-100 group-hover:text-white transition-colors truncate">
                            {team.name}
                          </div>
                          <div className="text-xs text-slate-500 sm:hidden">
                            {team.wins}-{team.losses}
                          </div>
                        </div>
                      </div>

                      {/* Record - Desktop */}
                      <div className="col-span-2 text-center hidden sm:block">
                        <span className="text-slate-300 font-medium">
                          {team.wins}-{team.losses}
                        </span>
                      </div>

                      {/* Rating */}
                      <div className="col-span-3 sm:col-span-2 text-right">
                        <span className={`text-base sm:text-xl font-bold ${getRatingColor(team.ranking)}`}>
                          {team.ranking.toFixed(2)}
                        </span>
                      </div>

                      {/* Expand Button */}
                      <div className="col-span-2 sm:col-span-1 text-center">
                        <div className="bg-slate-700 group-hover:bg-slate-600 rounded-lg p-1.5 sm:p-2 inline-block transition-colors">
                          {isExpanded ? (
                            <ChevronUp size={16} className="text-orange-500" />
                          ) : (
                            <ChevronDown size={16} className="text-slate-400" />
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Expanded Game Details */}
                    {isExpanded && (
                      <div className="bg-slate-900/50 border-b border-slate-700/50 px-4 sm:px-6 py-4 sm:py-6">
                        <h3 className="text-base sm:text-lg font-bold text-slate-200 mb-3 sm:mb-4 flex items-center gap-2">
                          <span className="text-orange-500">{team.name}</span>
                          <span className="text-slate-500">Game Results</span>
                        </h3>
                        <div className="space-y-2">
                          {team.games.map((game, idx) => {
                            const oppLogoUrl = getTeamLogo(game.opponent);
                            return (
                              <div
                                key={idx}
                                className="bg-slate-800/50 rounded-lg p-3 sm:p-4 flex items-center justify-between gap-2 sm:gap-4 hover:bg-slate-800 transition-colors"
                              >
                                {/* Left side - Result and Opponent */}
                                <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                                  <span className={`text-xs font-bold px-2 py-1 rounded ${game.won ? 'bg-green-600' : 'bg-red-600'} text-white flex-shrink-0`}>
                                    {game.won ? 'W' : 'L'}
                                  </span>
                                  {oppLogoUrl && (
                                    <div className="w-6 h-6 sm:w-8 sm:h-8 flex-shrink-0">
                                      <img 
                                        src={oppLogoUrl} 
                                        alt={game.opponent}
                                        className="w-full h-full object-contain"
                                        onError={(e) => e.target.style.display = 'none'}
                                      />
                                    </div>
                                  )}
                                  <div className="min-w-0 flex-1">
                                    <div className="text-sm sm:text-base font-semibold text-slate-200 truncate">
                                      {game.opponent}
                                    </div>
                                    <div className="text-xs text-slate-500">
                                      {game.opponent_record}
                                    </div>
                                  </div>
                                </div>

                                {/* Right side - Stats */}
                                <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
                                  <div className="text-right hidden sm:block">
                                    <div className="text-xs text-slate-500">OPP RANK</div>
                                    <div className={`text-sm font-bold ${getRatingColor(game.opponent_rank)}`}>
                                      {game.opponent_rank.toFixed(2)}
                                    </div>
                                  </div>
                                  <div className="text-right">
                                    <div className="text-xs text-slate-500">MARGIN</div>
                                    <div className={`text-sm font-bold ${getMarginColor(game.margin)}`}>
                                      {game.margin > 0 ? '+' : ''}{game.margin}
                                    </div>
                                  </div>
                                  <div className="text-right">
                                    <div className="text-xs text-slate-500">VALUE</div>
                                    <div className="text-sm font-bold text-orange-500">
                                      {game.value.toFixed(2)}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>

            {/* No Results */}
            {rankedTeams.length === 0 && (
              <div className="p-12 text-center text-slate-400">
                <p className="text-lg">No teams found</p>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        {!loading && !error && teams.length > 0 && (
          <div className="mt-6 sm:mt-8 text-center text-xs sm:text-sm text-slate-500">
            <p>Showing {rankedTeams.length} of {teams.length} FBS teams</p>
            <p className="mt-2">Rankings update in real-time as you adjust the formula weights</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;