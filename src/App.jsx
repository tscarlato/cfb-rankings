import React, { useState, useMemo, useEffect } from 'react';
import { ChevronUp, ChevronDown, Minus, Settings, Calendar, Search, RefreshCw, Trophy } from 'lucide-react';

const App = () => {
  // Formula parameters
  const [winMultiplier, setWinMultiplier] = useState(1.0);
  const [lossMultiplier, setLossMultiplier] = useState(1.0);
  const [oneScoreMultiplier, setOneScoreMultiplier] = useState(1.0);
  const [twoScoreMultiplier, setTwoScoreMultiplier] = useState(1.3);
  const [threeScoreMultiplier, setThreeScoreMultiplier] = useState(1.5);
  const [sosMultiplier, setSosMultiplier] = useState(1.0);

  const [showControls, setShowControls] = useState(false);
  const [selectedYear, setSelectedYear] = useState(2025);
  const [selectedWeek, setSelectedWeek] = useState('');
  const [selectedSeason, setSelectedSeason] = useState('regular');
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedTeam, setExpandedTeam] = useState(null);
  const [headerVisible, setHeaderVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

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
      
      // Group of 5 - AAC
      'Memphis': '235', 'Tulane': '2655', 'Navy': '2426', 'South Florida': '58',
      'East Carolina': '151', 'Temple': '218', 'UAB': '5', 'North Texas': '249',
      'UTSA': '2636', 'Charlotte': '2429', 'Tulsa': '202', 'Florida Atlantic': '2226',
      'Rice': '242',

      // Group of 5 - Mountain West
      'Boise State': '68', 'San Diego State': '21', 'Fresno State': '278',
      'Air Force': '2005', 'Colorado State': '36', 'Wyoming': '2849',
      'New Mexico': '167', 'Nevada': '2440', 'UNLV': '2439', 'San Jose State': '23',
      'Utah State': '328', 'Hawaii': '62',

      // Group of 5 - Sun Belt
      'App State': '2026', 'Appalachian State': '2026', 'Coastal Carolina': '324',
      'James Madison': '256', 'Marshall': '276', 'Georgia Southern': '290',
      'Louisiana': '309', 'Louisiana Lafayette': '309', 'Troy': '2653',
      'Arkansas State': '2032', 'South Alabama': '6', 'Georgia State': '2247',
      'Old Dominion': '295', 'Southern Miss': '2572', 'Southern Mississippi': '2572',
      'Texas State': '326', 'ULM': '2433',

      // Group of 5 - MAC
      'Toledo': '2649', 'Miami (OH)': '193', 'Miami OH': '193', 'Ohio': '195',
      'Bowling Green': '189', 'Northern Illinois': '2459', 'Ball State': '2050',
      'Western Michigan': '2711', 'Central Michigan': '2117', 'Eastern Michigan': '2199',
      'Buffalo': '2084', 'Kent State': '2309', 'Akron': '2006',

      // Group of 5 - CUSA
      'Western Kentucky': '98', 'Liberty': '2335', 'Middle Tennessee': '2393',
      'Jacksonville State': '55', 'Louisiana Tech': '2348', 'New Mexico State': '166',
      'Sam Houston State': '2534', 'Sam Houston': '2534', 'UTEP': '2638',
      'Florida International': '2229', 'FIU': '2229', 'Kennesaw State': '338'
    };
    
    const teamId = teamLogos[teamName];
    return teamId ? `https://a.espncdn.com/i/teamlogos/ncaa/500/${teamId}.png` : null;
  };

  // Get team conference
  const getTeamConference = (teamName) => {
    const conferences = {
      // SEC
      'Alabama': 'SEC', 'Georgia': 'SEC', 'LSU': 'SEC', 'Florida': 'SEC',
      'Tennessee': 'SEC', 'Texas': 'SEC', 'Texas A&M': 'SEC', 'Auburn': 'SEC',
      'Ole Miss': 'SEC', 'Mississippi State': 'SEC', 'Arkansas': 'SEC',
      'Kentucky': 'SEC', 'South Carolina': 'SEC', 'Missouri': 'SEC',
      'Vanderbilt': 'SEC', 'Oklahoma': 'SEC',

      // Big Ten
      'Ohio State': 'Big Ten', 'Michigan': 'Big Ten', 'Penn State': 'Big Ten', 'USC': 'Big Ten',
      'Oregon': 'Big Ten', 'Washington': 'Big Ten', 'UCLA': 'Big Ten', 'Michigan State': 'Big Ten',
      'Iowa': 'Big Ten', 'Wisconsin': 'Big Ten', 'Nebraska': 'Big Ten', 'Minnesota': 'Big Ten',
      'Indiana': 'Big Ten', 'Purdue': 'Big Ten', 'Maryland': 'Big Ten', 'Rutgers': 'Big Ten',
      'Northwestern': 'Big Ten', 'Illinois': 'Big Ten',

      // ACC
      'Clemson': 'ACC', 'Florida State': 'ACC', 'Miami': 'ACC',
      'North Carolina': 'ACC', 'NC State': 'ACC', 'Louisville': 'ACC',
      'Duke': 'ACC', 'Virginia Tech': 'ACC', 'Virginia': 'ACC',
      'Georgia Tech': 'ACC', 'Boston College': 'ACC', 'Syracuse': 'ACC',
      'Wake Forest': 'ACC', 'Pittsburgh': 'ACC', 'Stanford': 'ACC',
      'California': 'ACC', 'SMU': 'ACC',

      // Big 12
      'Kansas State': 'Big 12', 'TCU': 'Big 12', 'Baylor': 'Big 12', 'Texas Tech': 'Big 12',
      'Oklahoma State': 'Big 12', 'West Virginia': 'Big 12', 'Iowa State': 'Big 12',
      'Kansas': 'Big 12', 'BYU': 'Big 12', 'Utah': 'Big 12', 'Colorado': 'Big 12',
      'Arizona': 'Big 12', 'Arizona State': 'Big 12', 'Cincinnati': 'Big 12',
      'Houston': 'Big 12', 'UCF': 'Big 12',

      // Independent
      'Notre Dame': 'Independent', 'UConn': 'Independent', 'UMass': 'Independent', 'Army': 'Independent',

      // AAC (American)
      'Memphis': 'AAC', 'Tulane': 'AAC', 'Navy': 'AAC', 'South Florida': 'AAC',
      'East Carolina': 'AAC', 'Temple': 'AAC', 'UAB': 'AAC', 'North Texas': 'AAC',
      'UTSA': 'AAC', 'Charlotte': 'AAC', 'Tulsa': 'AAC', 'Florida Atlantic': 'AAC',
      'Rice': 'AAC',

      // Mountain West
      'Boise State': 'Mountain West', 'San Diego State': 'Mountain West', 'Fresno State': 'Mountain West',
      'Air Force': 'Mountain West', 'Colorado State': 'Mountain West', 'Wyoming': 'Mountain West',
      'New Mexico': 'Mountain West', 'Nevada': 'Mountain West', 'UNLV': 'Mountain West',
      'San Jose State': 'Mountain West', 'Utah State': 'Mountain West', 'Hawaii': 'Mountain West',

      // Sun Belt
      'App State': 'Sun Belt', 'Appalachian State': 'Sun Belt', 'Coastal Carolina': 'Sun Belt',
      'James Madison': 'Sun Belt', 'Marshall': 'Sun Belt', 'Georgia Southern': 'Sun Belt',
      'Louisiana': 'Sun Belt', 'Louisiana Lafayette': 'Sun Belt', 'Troy': 'Sun Belt',
      'Arkansas State': 'Sun Belt', 'South Alabama': 'Sun Belt', 'Georgia State': 'Sun Belt',
      'Old Dominion': 'Sun Belt', 'Southern Miss': 'Sun Belt', 'Southern Mississippi': 'Sun Belt',
      'Texas State': 'Sun Belt', 'ULM': 'Sun Belt',

      // MAC
      'Toledo': 'MAC', 'Miami (OH)': 'MAC', 'Miami OH': 'MAC', 'Ohio': 'MAC',
      'Bowling Green': 'MAC', 'Northern Illinois': 'MAC', 'Ball State': 'MAC',
      'Western Michigan': 'MAC', 'Central Michigan': 'MAC', 'Eastern Michigan': 'MAC',
      'Buffalo': 'MAC', 'Kent State': 'MAC', 'Akron': 'MAC',

      // CUSA
      'Western Kentucky': 'CUSA', 'Liberty': 'CUSA', 'Middle Tennessee': 'CUSA',
      'Jacksonville State': 'CUSA', 'Louisiana Tech': 'CUSA', 'New Mexico State': 'CUSA',
      'Sam Houston State': 'CUSA', 'Sam Houston': 'CUSA', 'UTEP': 'CUSA',
      'Florida International': 'CUSA', 'FIU': 'CUSA', 'Kennesaw State': 'CUSA'
    };

    return conferences[teamName] || 'Other';
  };

  // Fetch rankings from API
  const fetchRankings = async () => {
    setLoading(true);
    setError(null);
    setExpandedTeam(null);

    try {
      let url = `/rankings?year=${selectedYear}&season_type=${selectedSeason}`;
      if (selectedWeek) url += `&week=${selectedWeek}`;
      url += `&win_loss_multiplier=${winMultiplier}`;
      url += `&one_score_multiplier=${oneScoreMultiplier}`;
      url += `&two_score_multiplier=${twoScoreMultiplier}`;
      url += `&three_score_multiplier=${threeScoreMultiplier}`;
      url += `&strength_of_schedule_multiplier=${sosMultiplier}`;

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

  // Clear cache and fetch fresh data
  const clearCacheAndRefresh = async () => {
    setLoading(true);
    setError(null);
    try {
      // Call clear-cache endpoint
      await fetch('/clear-cache', { method: 'POST' });
      // Then fetch fresh rankings
      await fetchRankings();
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  // Fetch on mount and when parameters change
  useEffect(() => {
    fetchRankings();
  }, [selectedYear, selectedWeek, selectedSeason, winMultiplier, lossMultiplier, oneScoreMultiplier, twoScoreMultiplier, threeScoreMultiplier, sosMultiplier]);

  // Handle scroll to hide/show header
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;

      // Show header when scrolling up or at top
      if (currentScrollY < lastScrollY || currentScrollY < 10) {
        setHeaderVisible(true);
      }
      // Hide header when scrolling down (after scrolling past 100px)
      else if (currentScrollY > 100 && currentScrollY > lastScrollY) {
        setHeaderVisible(false);
      }

      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  // Filter teams by search (supports team name or conference)
  const filteredTeams = useMemo(() => {
    if (!searchQuery) return teams;
    const query = searchQuery.toLowerCase();
    return teams.filter(team => {
      const teamName = team.name.toLowerCase();
      const conference = getTeamConference(team.name).toLowerCase();
      return teamName.includes(query) || conference.includes(query);
    });
  }, [teams, searchQuery]);

  // Sort teams by ranking and assign ranks based on full list
  const rankedTeams = useMemo(() => {
    // First, sort all teams to establish true ranks
    const sortedAllTeams = [...teams].sort((a, b) => b.ranking - a.ranking);

    // Create a map of team name to their true rank
    const rankMap = new Map();
    sortedAllTeams.forEach((team, index) => {
      rankMap.set(team.name, index + 1);
    });

    // Sort filtered teams and attach their true rank
    return [...filteredTeams]
      .sort((a, b) => b.ranking - a.ranking)
      .map(team => ({
        ...team,
        trueRank: rankMap.get(team.name)
      }));
  }, [teams, filteredTeams]);

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
      <div className={`border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-10 transition-transform duration-300 ${headerVisible ? 'translate-y-0' : '-translate-y-full'}`}>
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
                onClick={clearCacheAndRefresh}
                className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors border border-orange-500"
                title="Clear cache and get latest data from API"
              >
                <RefreshCw size={18} />
                <span className="hidden sm:inline">Get Latest</span>
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
                placeholder="Search by team or conference..."
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
            <h2 className="text-lg sm:text-xl font-semibold mb-6 flex items-center gap-2">
              <Settings size={20} className="text-orange-500" />
              Ranking Formula Customization
            </h2>

            {/* Section 1: Game Outcome Impact */}
            <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border border-slate-600">
              <h3 className="text-md font-semibold mb-4 text-green-400 flex items-center gap-2">
                <Trophy size={16} />
                Game Outcome Impact
              </h3>
              <div className="grid sm:grid-cols-2 gap-4">
                {/* Win Value */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-slate-300">
                      Win Value
                    </label>
                    <span className="text-lg font-bold text-green-500 bg-green-500/10 px-2 py-1 rounded">
                      +{winMultiplier.toFixed(1)}x
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1.0"
                    max="2.0"
                    step="0.1"
                    value={winMultiplier}
                    onChange={(e) => setWinMultiplier(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-green-500"
                  />
                  <p className="text-xs text-slate-500 mt-1">Base reward for winning (always ≥ 1.0)</p>
                </div>

                {/* Loss Penalty */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-slate-300">
                      Loss Penalty
                    </label>
                    <span className="text-lg font-bold text-red-500 bg-red-500/10 px-2 py-1 rounded">
                      -{lossMultiplier.toFixed(1)}x
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1.0"
                    max="2.0"
                    step="0.1"
                    value={lossMultiplier}
                    onChange={(e) => setLossMultiplier(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-red-500"
                  />
                  <p className="text-xs text-slate-500 mt-1">Penalty for losing (always ≥ 1.0, applied as negative)</p>
                </div>
              </div>
            </div>

            {/* Section 2: Margin of Victory Impact */}
            <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border border-slate-600">
              <h3 className="text-md font-semibold mb-4 text-blue-400 flex items-center gap-2">
                <ChevronUp size={16} />
                Margin of Victory Impact
              </h3>
              <div className="grid sm:grid-cols-3 gap-4">
                {/* 1-Score Games */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-slate-300">
                      1-Score (≤8pts)
                    </label>
                    <span className="text-lg font-bold text-blue-400 bg-blue-400/10 px-2 py-1 rounded">
                      {oneScoreMultiplier.toFixed(1)}x
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={oneScoreMultiplier}
                    onChange={(e) => setOneScoreMultiplier(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-400"
                  />
                  <p className="text-xs text-slate-500 mt-1">Close games</p>
                </div>

                {/* 2-Score Games */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-slate-300">
                      2-Score (9-16pts)
                    </label>
                    <span className="text-lg font-bold text-blue-400 bg-blue-400/10 px-2 py-1 rounded">
                      {twoScoreMultiplier.toFixed(1)}x
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={twoScoreMultiplier}
                    onChange={(e) => setTwoScoreMultiplier(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-400"
                  />
                  <p className="text-xs text-slate-500 mt-1">Moderate wins</p>
                </div>

                {/* 3+ Score Games */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-slate-300">
                      3+ Score (&gt;16pts)
                    </label>
                    <span className="text-lg font-bold text-blue-400 bg-blue-400/10 px-2 py-1 rounded">
                      {threeScoreMultiplier.toFixed(1)}x
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    value={threeScoreMultiplier}
                    onChange={(e) => setThreeScoreMultiplier(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-400"
                  />
                  <p className="text-xs text-slate-500 mt-1">Blowouts</p>
                </div>
              </div>
            </div>

            {/* Section 3: Strength of Schedule Impact */}
            <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border border-slate-600">
              <h3 className="text-md font-semibold mb-4 text-purple-400 flex items-center gap-2">
                <ChevronDown size={16} />
                Strength of Schedule Impact
              </h3>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-medium text-slate-300">
                    Opponent Strength Weight
                  </label>
                  <span className="text-lg font-bold text-purple-400 bg-purple-400/10 px-2 py-1 rounded">
                    {sosMultiplier.toFixed(1)}x
                  </span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="2.0"
                  step="0.1"
                  value={sosMultiplier}
                  onChange={(e) => setSosMultiplier(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-400"
                />
                <p className="text-xs text-slate-500 mt-1">
                  How much opponent quality matters (0 = only W/L matters, 2.0 = SoS heavily weighted)
                </p>
              </div>
            </div>

            {/* Formula Explanation */}
            <div className="mt-6 pt-6 border-t border-slate-700">
              <h3 className="text-md font-semibold mb-3 text-orange-400">📐 Ranking Formula Explained</h3>
              <div className="bg-slate-900/50 p-4 rounded-lg space-y-3">
                <p className="text-sm text-slate-300 leading-relaxed">
                  Each game contributes points to a team's overall rating using this formula:
                </p>
                <div className="bg-slate-950/50 p-3 rounded border border-slate-600">
                  <code className="text-orange-400 text-sm">
                    Game Value = (Outcome × Margin) + Opponent Strength
                  </code>
                </div>
                <div className="text-sm text-slate-400 space-y-2">
                  <p><strong className="text-slate-300">Outcome:</strong> Win Value (+) or Loss Penalty (-)</p>
                  <p><strong className="text-slate-300">Margin:</strong> Multiplier based on point differential (1-score, 2-score, or 3+ score)</p>
                  <p><strong className="text-slate-300">Opponent Strength:</strong> (Opponent Rating ÷ 100) × SoS Weight</p>
                </div>
                <div className="bg-blue-500/10 border border-blue-500/30 p-3 rounded mt-3">
                  <p className="text-xs text-blue-300">
                    <strong>Example:</strong> Beating a 75.0-rated team by 20 points with default settings:<br/>
                    <code className="text-blue-200">(+1.0 × 1.5) + (75.0 ÷ 100 × 1.0) = 1.5 + 0.75 = 2.25 points</code>
                  </p>
                </div>
              </div>
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
            <div>
              {rankedTeams.map((team, index) => {
                const rank = team.trueRank;
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
                        <div className="w-8 h-8 sm:w-10 sm:h-10 flex-shrink-0 bg-slate-100 rounded-lg flex items-center justify-center overflow-hidden p-1">
                          {logoUrl ? (
                            <img
                              src={logoUrl}
                              alt={team.name}
                              className="w-full h-full object-contain"
                              onError={(e) => {
                                e.target.parentElement.innerHTML = `<span class="text-xs font-bold text-slate-600">${team.name.substring(0, 3).toUpperCase()}</span>`;
                              }}
                            />
                          ) : (
                            <span className="text-xs font-bold text-slate-600">
                              {team.name.substring(0, 3).toUpperCase()}
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
                                  <div className="w-6 h-6 sm:w-8 sm:h-8 flex-shrink-0 bg-slate-100 rounded flex items-center justify-center p-0.5">
                                    {oppLogoUrl ? (
                                      <img
                                        src={oppLogoUrl}
                                        alt={game.opponent}
                                        className="w-full h-full object-contain"
                                        onError={(e) => {
                                          e.target.parentElement.innerHTML = `<span class="text-[0.5rem] font-bold text-slate-600">${game.opponent.substring(0, 2).toUpperCase()}</span>`;
                                        }}
                                      />
                                    ) : (
                                      <span className="text-[0.5rem] font-bold text-slate-600">
                                        {game.opponent.substring(0, 2).toUpperCase()}
                                      </span>
                                    )}
                                  </div>
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