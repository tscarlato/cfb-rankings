interface FormulaParams {
  win_loss_multiplier: number;
  one_score_multiplier: number;
  two_score_multiplier: number;
  three_score_multiplier: number;
  strength_of_schedule_multiplier: number;
}

interface FormulaControlsProps {
  params: FormulaParams;
  onParamsChange: (params: FormulaParams) => void;
  onApply: () => void;
}

export const FormulaControls = ({ params, onParamsChange, onApply }: FormulaControlsProps) => {
  const handleReset = () => {
    onParamsChange({
      win_loss_multiplier: 1.0,
      one_score_multiplier: 1.0,
      two_score_multiplier: 1.3,
      three_score_multiplier: 1.5,
      strength_of_schedule_multiplier: 1.0,
    });
  };

  const updateParam = (key: keyof FormulaParams, value: number) => {
    onParamsChange({ ...params, [key]: value });
  };

  const inputClassName = "w-full px-4 py-3 border-2 border-primary/30 rounded-xl focus:ring-2 focus:ring-primary focus:border-primary bg-white font-semibold transition-all duration-200 hover:border-primary/50 shadow-sm";

  return (
    <div className="p-6 bg-gradient-to-br from-primary/5 to-accent/5 rounded-xl border-2 border-primary/20 shadow-lg">
      <h3 className="text-xl font-bold text-foreground mb-6 flex items-center gap-3">
        <i className="fas fa-sliders-h text-primary text-2xl"></i>
        Formula Parameters
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <div>
          <label className="block text-sm font-bold text-foreground mb-2">
            Win/Loss Impact
            <span className="text-xs text-muted-foreground font-normal ml-1">(default: 1.0)</span>
          </label>
          <input
            type="number"
            value={params.win_loss_multiplier}
            onChange={(e) => updateParam("win_loss_multiplier", parseFloat(e.target.value))}
            step="0.1"
            min="0"
            className={inputClassName}
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">
            1-Score Game (≤8 pts)
            <span className="text-xs text-muted-foreground font-normal ml-1">(default: 1.0)</span>
          </label>
          <input
            type="number"
            value={params.one_score_multiplier}
            onChange={(e) => updateParam("one_score_multiplier", parseFloat(e.target.value))}
            step="0.1"
            min="0"
            className={inputClassName}
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">
            2-Score Game (9-16 pts)
            <span className="text-xs text-muted-foreground font-normal ml-1">(default: 1.3)</span>
          </label>
          <input
            type="number"
            value={params.two_score_multiplier}
            onChange={(e) => updateParam("two_score_multiplier", parseFloat(e.target.value))}
            step="0.1"
            min="0"
            className={inputClassName}
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">
            3+ Score Game (&gt;16 pts)
            <span className="text-xs text-muted-foreground font-normal ml-1">(default: 1.5)</span>
          </label>
          <input
            type="number"
            value={params.three_score_multiplier}
            onChange={(e) => updateParam("three_score_multiplier", parseFloat(e.target.value))}
            step="0.1"
            min="0"
            className={inputClassName}
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-foreground mb-2">
            Strength of Schedule
            <span className="text-xs text-muted-foreground font-normal ml-1">(default: 1.0)</span>
          </label>
          <input
            type="number"
            value={params.strength_of_schedule_multiplier}
            onChange={(e) => updateParam("strength_of_schedule_multiplier", parseFloat(e.target.value))}
            step="0.1"
            min="0"
            className={inputClassName}
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={onApply}
          className="flex items-center gap-2 bg-gradient-primary text-white px-6 py-3 rounded-xl hover:opacity-90 transition-all font-bold shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
        >
          <i className="fas fa-calculator"></i>
          Apply Formula
        </button>
        <button
          onClick={handleReset}
          className="flex items-center gap-2 bg-slate-600 text-white px-6 py-3 rounded-xl hover:bg-slate-700 transition-all font-bold shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
        >
          <i className="fas fa-undo"></i>
          Reset to Defaults
        </button>
      </div>

      <div className="p-5 bg-white rounded-xl border-2 border-primary/20 shadow-sm">
        <p className="font-bold text-foreground mb-2 flex items-center gap-2">
          <i className="fas fa-calculator text-primary"></i>
          Current Formula:
        </p>
        <p className="text-sm text-muted-foreground font-mono mb-3">
          (Win/Loss × Score Margin Multiplier) + ((Opponent Rank ÷ 100) × SoS Multiplier)
        </p>
        <p className="text-sm text-muted-foreground">
          <strong className="text-foreground">Score Categories:</strong> 1-Score (≤8pts) = {params.one_score_multiplier}x, 
          2-Score (9-16pts) = {params.two_score_multiplier}x, 3+ Score (&gt;16pts) = {params.three_score_multiplier}x
        </p>
      </div>
    </div>
  );
};
