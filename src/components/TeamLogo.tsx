import { useState } from "react";
import { getTeamLogo } from "@/lib/cfb-utils";

interface TeamLogoProps {
  teamName: string;
}

export const TeamLogo = ({ teamName }: TeamLogoProps) => {
  const [imageError, setImageError] = useState(false);
  const logoUrl = getTeamLogo(teamName);

  if (!logoUrl || imageError) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-white rounded-full shadow-lg border-3 border-primary/20">
        <i className="fas fa-football-ball text-muted-foreground text-2xl"></i>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex items-center justify-center bg-white rounded-full shadow-lg border-3 border-primary/20 overflow-hidden transition-transform duration-200 group-hover:scale-110 group-hover:shadow-xl">
      <img
        src={logoUrl}
        alt={teamName}
        className="w-[85%] h-[85%] object-contain"
        onError={() => setImageError(true)}
      />
    </div>
  );
};
