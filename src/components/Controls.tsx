import { useState } from "react";
import { FormulaControls } from "./FormulaControls";

interface FormulaParams {
  win_loss_multiplier: number;
  one_score_multiplier: number;
  two_score_multiplier: number;
  three_score_multiplier: number;
  strength_of_schedule_multiplier: number;
}

interface ControlsProps {
  year: string;
  week: string;
  seasonType: string;
  searchQuery: string;
  formulaParams: FormulaParams;
  onYearChange: (year: string) => void;
  onWeekChange: (week: string) => void;
  onSeasonTypeChange: (type: string) => void;
  onSearchChange: (query: string) => void;
  onFormulaChange: (params: FormulaParams) => void;
  onApplyFormula: () => void;
}

export const Controls = ({
  year,
  week,
  seasonType,
  searchQuery,
  formulaParams,
  onYearChange,
  onWeekChange,
  onSeasonTypeChange,
  onSearchChange,
  onFormulaChange,
  onApplyFormula,
}: ControlsProps) => {
  const [showFormula, setShowFormula] = useState(false);

  const selectClassName = "w-full px-4 py-3 md:py-3.5 border-3 border-primary/40 rounded-xl focus:ring-4 focus:ring-primary/30 focus:border-primary font-bold bg-card transition-all duration-200 hover:border-primary shadow-lg text-sm md:text-base";
  const inputClassName = "w-full px-4 py-3 md:py-3.5 border-3 border-primary/40 rounded-xl focus:ring-4 focus:ring-primary/30 focus:border-primary bg-card transition-all duration-200 hover:border-primary shadow-lg text-sm md:text-base font-bold";

  return (
    <div className="bg-card rounded-xl shadow-brutal p-5 md:p-6 border-4 border-primary/20 texture-paper">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
        <div>
          <label className="block text-sm font-bold text-foreground mb-2 flex items-center gap-2">
            <i className="fas fa-calendar text-primary"></i>
            Year
          </label>
          <select
            value={year}
            onChange={(e) => onYearChange(e.target.value)}
            className={selectClassName}
          >
            <option value="2025">2025</option>
            <option value="2024">2024</option>
            <option value="2023">2023</option>
            <option value="2022">2022</option>
            <option value="2021">2021</option>
            <option value="2020">2020</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2 flex items-center gap-2">
            <i className="fas fa-clock text-primary"></i>
            Week
          </label>
          <select
            value={week}
            onChange={(e) => onWeekChange(e.target.value)}
            className={selectClassName}
          >
            <option value="">All Weeks</option>
            {Array.from({ length: 15 }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                Week {i + 1}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2 flex items-center gap-2">
            <i className="fas fa-football-ball text-primary"></i>
            Season Type
          </label>
          <select
            value={seasonType}
            onChange={(e) => onSeasonTypeChange(e.target.value)}
            className={selectClassName}
          >
            <option value="regular">Regular Season</option>
            <option value="both">Regular + Postseason</option>
          </select>
        </div>

        <div className="lg:col-span-2">
          <label className="block text-sm font-bold text-foreground mb-2 flex items-center gap-2">
            <i className="fas fa-search text-primary"></i>
            Search Teams
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Find your team..."
            className={inputClassName}
          />
        </div>
      </div>

      <div className="border-t-4 border-primary/20 pt-4">
        <button
          onClick={() => setShowFormula(!showFormula)}
          className="flex items-center gap-3 text-primary hover:text-primary-glow font-bold text-base md:text-lg group transition-all hover:scale-[1.02]"
        >
          <div className="bg-primary/10 group-hover:bg-primary/20 rounded-lg p-2.5 transition-all shadow-lg group-hover:shadow-xl">
            <i className={`fas fa-chevron-${showFormula ? 'up' : 'down'} transition-transform duration-200`}></i>
          </div>
          <span className="font-display text-xl md:text-2xl tracking-wide">CUSTOMIZE FORMULA</span>
          <span className="text-xs md:text-sm font-normal text-muted-foreground uppercase">(For Nerds)</span>
        </button>

        {showFormula && (
          <div className="mt-6 animate-accordion-down">
            <FormulaControls
              params={formulaParams}
              onParamsChange={onFormulaChange}
              onApply={onApplyFormula}
            />
          </div>
        )}
      </div>
    </div>
  );
};
