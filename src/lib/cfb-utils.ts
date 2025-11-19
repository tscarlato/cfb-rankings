// Team logo mapping - ESPN CDN URLs
const teamLogos: Record<string, string> = {
  // Power 4 - SEC
  'Alabama': '333', 'Georgia': '61', 'LSU': '99', 'Florida': '57',
  'Tennessee': '2633', 'Texas': '251', 'Texas A&M': '245', 'Auburn': '2',
  'Ole Miss': '145', 'Mississippi State': '344', 'Arkansas': '8',
  'Kentucky': '96', 'South Carolina': '2579', 'Missouri': '142',
  'Vanderbilt': '238', 'Oklahoma': '201',
  
  // Power 4 - Big Ten
  'Ohio State': '194', 'Michigan': '130', 'Penn State': '213',
  'USC': '30', 'Oregon': '2483', 'Washington': '264', 'UCLA': '26',
  'Michigan State': '127', 'Iowa': '2294', 'Wisconsin': '275',
  'Nebraska': '158', 'Minnesota': '135', 'Indiana': '84',
  'Purdue': '2509', 'Maryland': '120', 'Rutgers': '164',
  'Northwestern': '77', 'Illinois': '356',
  
  // Power 4 - ACC
  'Clemson': '228', 'Florida State': '52', 'Miami': '2390',
  'North Carolina': '153', 'NC State': '152', 'Louisville': '97',
  'Duke': '150', 'Virginia Tech': '259', 'Virginia': '258',
  'Georgia Tech': '59', 'Boston College': '103', 'Syracuse': '183',
  'Wake Forest': '154', 'Pittsburgh': '221', 'Stanford': '24',
  'California': '25', 'SMU': '2567',
  
  // Power 4 - Big 12
  'Kansas State': '2306', 'TCU': '2628', 'Baylor': '239',
  'Texas Tech': '2641', 'Oklahoma State': '197', 'West Virginia': '277',
  'Iowa State': '66', 'Kansas': '2305', 'BYU': '252', 'Utah': '254',
  'Colorado': '38', 'Arizona': '12', 'Arizona State': '9',
  'Cincinnati': '2132', 'Houston': '248', 'UCF': '2116',
  
  // Independent
  'Notre Dame': '87', 'UConn': '41', 'UMass': '113',
  
  // Group of 5 - American
  'Memphis': '235', 'Tulane': '2655', 'Navy': '2426',
  'South Florida': '58', 'Temple': '218', 'East Carolina': '151',
  'Tulsa': '202', 'UTSA': '2636', 'North Texas': '249',
  'Charlotte': '2429', 'Florida Atlantic': '2226', 'Rice': '242',
  'UAB': '5',
  
  // Group of 5 - Mountain West
  'Boise State': '68', 'San Diego State': '21', 'Fresno State': '278',
  'Air Force': '2005', 'Wyoming': '2005', 'Colorado State': '36',
  'Nevada': '2440', 'UNLV': '2439', 'New Mexico': '167',
  'San José State': '23', 'Utah State': '328', 'Hawaiʻi': '62',
  
  // Group of 5 - Sun Belt
  'App State': '2026', 'Appalachian State': '2026',
  'Coastal Carolina': '324', 'James Madison': '256', 'Marshall': '276',
  'Georgia Southern': '290', 'Georgia State': '2247', 'Troy': '2653',
  'South Alabama': '6', 'Louisiana': '309', 'Southern Mississippi': '2572',
  'Arkansas State': '2032', 'Louisiana Monroe': '2433', 'Texas State': '326',
  'Old Dominion': '295',
  
  // Group of 5 - MAC
  'Toledo': '2649', 'Miami (OH)': '193', 'Ohio': '195',
  'Bowling Green': '189', 'Northern Illinois': '2459', 'Ball State': '2050',
  'Eastern Michigan': '2199', 'Western Michigan': '2711',
  'Central Michigan': '2117', 'Buffalo': '2084', 'Kent State': '2309',
  'Akron': '4',
  
  // Group of 5 - CUSA
  'Liberty': '2335', 'Western Kentucky': '98', 'Jacksonville State': '55',
  'Louisiana Tech': '2348', 'Middle Tennessee': '2393', 'UTEP': '2638',
  'New Mexico State': '166', 'Sam Houston': '2534',
  'Sam Houston State': '2534', 'FIU': '2229', 'Kennesaw State': '2817',
  
  // Army variations
  'Army': '349', 'Army West Point': '349',
  
  // Additional variations
  'Hawaii': '62', "Hawai'i": '62', 'Miami (FL)': '2390',
  'Miami FL': '2390', 'UL Monroe': '2433', 'ULM': '2433',
  'Southern Miss': '2572', 'UL Lafayette': '309',
  'Louisiana Lafayette': '309', 'SJSU': '23', 'San Jose State': '23',
  'UT San Antonio': '2636'
};

export function getTeamLogo(teamName: string): string | null {
  const teamId = teamLogos[teamName];
  if (teamId) {
    return `https://a.espncdn.com/i/teamlogos/ncaa/500/${teamId}.png`;
  }
  return null;
}

export function getRankColor(rank: number): string {
  if (rank > 15) return "text-success";
  if (rank > 10) return "text-success/80";
  if (rank > 5) return "text-accent";
  if (rank > 0) return "text-foreground";
  if (rank > -5) return "text-warning";
  return "text-destructive";
}
