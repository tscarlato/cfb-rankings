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
      <div className="w-12 h-12 flex items-center justify-center bg-white rounded-full shadow-md border-2 border-border">
        <i className="fas fa-football-ball text-muted-foreground text-xl"></i>
      </div>
    );
  }

  return (
    <div className="w-12 h-12 flex items-center justify-center bg-white rounded-full shadow-md border-2 border-border overflow-hidden transition-transform duration-200 hover:scale-110">
      <img
        src={logoUrl}
        alt={teamName}
        className="w-10 h-10 object-contain"
        onError={() => setImageError(true)}
      />
    </div>
  );
};
