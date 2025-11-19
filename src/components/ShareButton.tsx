import { useState } from "react";
import { toast } from "sonner";

interface ShareButtonProps {
  year: string;
  week: string;
  seasonType: string;
  formulaParams: {
    win_loss_multiplier: number;
    one_score_multiplier: number;
    two_score_multiplier: number;
    three_score_multiplier: number;
    strength_of_schedule_multiplier: number;
  };
}

export const ShareButton = ({ year, week, seasonType, formulaParams }: ShareButtonProps) => {
  const [justCopied, setJustCopied] = useState(false);

  const generateShareUrl = () => {
    const baseUrl = window.location.origin + window.location.pathname;
    const params = new URLSearchParams();

    params.set('year', year);
    if (week) params.set('week', week);
    params.set('season_type', seasonType);
    params.set('wl', formulaParams.win_loss_multiplier.toString());
    params.set('os', formulaParams.one_score_multiplier.toString());
    params.set('ts', formulaParams.two_score_multiplier.toString());
    params.set('ths', formulaParams.three_score_multiplier.toString());
    params.set('sos', formulaParams.strength_of_schedule_multiplier.toString());

    return `${baseUrl}?${params.toString()}`;
  };

  const handleShare = async () => {
    const url = generateShareUrl();

    try {
      await navigator.clipboard.writeText(url);
      setJustCopied(true);
      toast.success("Link copied to clipboard!", {
        description: "Share your hot take with the world!",
        duration: 3000,
      });

      setTimeout(() => setJustCopied(false), 3000);
    } catch (err) {
      toast.error("Failed to copy link", {
        description: "Please try again",
      });
    }
  };

  return (
    <button
      onClick={handleShare}
      disabled={justCopied}
      className="group relative bg-gradient-accent text-secondary px-6 md:px-8 py-4 md:py-5 rounded-xl font-bold shadow-brutal hover:shadow-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-75 disabled:cursor-not-allowed border-4 border-accent/50 overflow-hidden"
    >
      {/* Animated background shimmer */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000"></div>

      {/* Button content */}
      <div className="relative z-10 flex items-center gap-3">
        <i className={`fas ${justCopied ? 'fa-check-circle' : 'fa-share-alt'} text-2xl md:text-3xl transition-all duration-300`}></i>
        <div className="text-left">
          <div className="font-display text-2xl md:text-3xl tracking-wide leading-none text-shadow-pop">
            {justCopied ? "COPIED!" : "SHARE YOUR RANKINGS"}
          </div>
          <div className="text-xs md:text-sm font-normal opacity-90 mt-0.5">
            {justCopied ? "Now go start some arguments" : "Copy link to clipboard"}
          </div>
        </div>
      </div>

      {/* Confetti burst animation on copy */}
      {justCopied && (
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-white rounded-full animate-ping"
              style={{
                top: '50%',
                left: '50%',
                animationDelay: `${i * 50}ms`,
                transform: `rotate(${i * 45}deg) translateY(-30px)`,
              }}
            />
          ))}
        </div>
      )}
    </button>
  );
};
