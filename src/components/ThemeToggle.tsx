import { useEffect, useState } from "react";

export const ThemeToggle = () => {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    // Check for saved theme preference or default to light
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    const preferredTheme = savedTheme || "light";

    setTheme(preferredTheme);
    document.documentElement.classList.toggle("dark", preferredTheme === "dark");
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.classList.toggle("dark", newTheme === "dark");
  };

  return (
    <button
      onClick={toggleTheme}
      className="group relative bg-gradient-to-br from-secondary to-secondary/80 text-white px-4 md:px-5 py-3 md:py-3.5 rounded-xl font-bold shadow-brutal hover:shadow-xl transition-all hover:scale-105 active:scale-95 border-2 border-secondary/30 flex items-center gap-2 md:gap-3"
      aria-label="Toggle theme"
    >
      {theme === "light" ? (
        <>
          <i className="fas fa-moon text-accent text-lg md:text-xl"></i>
          <span className="font-display text-base md:text-lg tracking-wide hidden sm:inline">
            NIGHT GAME
          </span>
        </>
      ) : (
        <>
          <i className="fas fa-sun text-accent text-lg md:text-xl"></i>
          <span className="font-display text-base md:text-lg tracking-wide hidden sm:inline">
            GAMEDAY
          </span>
        </>
      )}
    </button>
  );
};
