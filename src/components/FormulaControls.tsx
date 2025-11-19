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

  const handlePreset = (presetName: string) => {
    switch (presetName) {
      case "just-win":
        onParamsChange({
          win_loss_multiplier: 1.5,
          one_score_multiplier: 1.0,
          two_score_multiplier: 1.0,
          three_score_multiplier: 1.0,
          strength_of_schedule_multiplier: 1.0,
        });
        break;
      case "blowout":
        onParamsChange({
          win_loss_multiplier: 1.0,
          one_score_multiplier: 0.5,
          two_score_multiplier: 1.5,
          three_score_multiplier: 2.0,
          strength_of_schedule_multiplier: 1.0,
        });
        break;
      case "schedule":
        onParamsChange({
          win_loss_multiplier: 1.0,
          one_score_multiplier: 1.0,
          two_score_multiplier: 1.0,
          three_score_multiplier: 1.0,
          strength_of_schedule_multiplier: 2.0,
        });
        break;
    }
  };

  const updateParam = (key: keyof FormulaParams, value: number) => {
    onParamsChange({ ...params, [key]: value });
  };

  const inputClassName = "w-full px-4 py-3 border-3 border-primary/40 rounded-xl focus:ring-4 focus:ring-primary/30 focus:border-primary bg-card font-bold transition-all duration-200 hover:border-primary shadow-lg text-lg";

  return (
    <div className="p-5 md:p-6 bg-card rounded-xl border-4 border-primary/30 shadow-brutal texture-paper">
      {/* Header */}
      <div className="mb-5">
        <h3 className="font-display text-3xl md:text-4xl text-primary mb-2 flex items-center gap-3 text-shadow-pop">
          <i className="fas fa-sliders-h text-2xl md:text-3xl"></i>
          TWEAK YOUR FORMULA
        </h3>
        <p className="text-sm md:text-base text-muted-foreground font-bold">
          Quick presets or go full nerd mode
        </p>
      </div>

      {/* Preset Buttons - THE GOOD STUFF */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <button
          onClick={() => handlePreset("just-win")}
          className="group relative bg-gradient-success text-white px-4 py-4 rounded-xl font-bold shadow-brutal hover:shadow-xl transition-all hover:scale-105 active:scale-95 border-2 border-success/30"
        >
          <div className="flex flex-col items-center gap-1">
            <div className="flex items-center gap-2">
              <i className="fas fa-trophy text-xl"></i>
              <span className="font-display text-xl md:text-2xl tracking-wide">JUST WIN BABY</span>
            </div>
            <span className="text-xs font-normal opacity-90">W's are all that matter</span>
          </div>
        </button>

        <button
          onClick={() => handlePreset("blowout")}
          className="group relative bg-gradient-warning text-secondary px-4 py-4 rounded-xl font-bold shadow-brutal hover:shadow-xl transition-all hover:scale-105 active:scale-95 border-2 border-accent/50"
        >
          <div className="flex flex-col items-center gap-1">
            <div className="flex items-center gap-2">
              <i className="fas fa-fire text-xl"></i>
              <span className="font-display text-xl md:text-2xl tracking-wide">BLOWOUT CITY</span>
            </div>
            <span className="text-xs font-normal opacity-90">Domination only</span>
          </div>
        </button>

        <button
          onClick={() => handlePreset("schedule")}
          className="group relative bg-gradient-maroon text-white px-4 py-4 rounded-xl font-bold shadow-brutal hover:shadow-xl transition-all hover:scale-105 active:scale-95 border-2 border-secondary/30"
        >
          <div className="flex flex-col items-center gap-1">
            <div className="flex items-center gap-2">
              <i className="fas fa-brain text-xl"></i>
              <span className="font-display text-xl md:text-2xl tracking-wide">SCHEDULE SICKO</span>
            </div>
            <span className="text-xs font-normal opacity-90">SoS obsessed</span>
          </div>
        </button>
      </div>

      {/* Divider */}
      <div className="flex items-center gap-3 mb-5">
        <div className="flex-1 h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
        <span className="text-xs font-bold text-muted-foreground uppercase tracking-wide">Or Customize</span>
        <div className="flex-1 h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent"></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-bold text-foreground mb-2 uppercase tracking-wide">
            <i className="fas fa-check-circle text-success mr-1"></i>
            Win/Loss Weight
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
          <label className="block text-sm font-bold text-foreground mb-2 uppercase tracking-wide">
            <i className="fas fa-grip-lines text-warning mr-1"></i>
            Close Games (≤8)
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
          <label className="block text-sm font-bold text-foreground mb-2 uppercase tracking-wide">
            <i className="fas fa-chart-line text-primary mr-1"></i>
            2-Score (9-16)
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
          <label className="block text-sm font-bold text-foreground mb-2 uppercase tracking-wide">
            <i className="fas fa-fire text-destructive mr-1"></i>
            Blowouts (17+)
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

        <div className="md:col-span-2 lg:col-span-1">
          <label className="block text-sm font-bold text-foreground mb-2 uppercase tracking-wide">
            <i className="fas fa-shield-alt text-secondary mr-1"></i>
            Strength of Schedule
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

      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleReset}
          className="flex items-center gap-2 bg-muted text-foreground px-5 py-3 rounded-xl hover:bg-muted/80 transition-all font-bold shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 uppercase tracking-wide border-2 border-border"
        >
          <i className="fas fa-undo"></i>
          Reset
        </button>
      </div>
    </div>
  );
};
