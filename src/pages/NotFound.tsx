import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center animate-scale-in">
        <i className="fas fa-exclamation-triangle text-warning text-6xl mb-6"></i>
        <h1 className="mb-4 text-5xl font-bold text-foreground">404</h1>
        <p className="mb-6 text-xl text-muted-foreground">Oops! Page not found</p>
        <a
          href="/"
          className="inline-flex items-center gap-2 bg-gradient-primary text-white px-6 py-3 rounded-xl hover:opacity-90 transition-all font-bold shadow-lg hover:shadow-xl hover:scale-105"
        >
          <i className="fas fa-home"></i>
          Return to Home
        </a>
      </div>
    </div>
  );
};

export default NotFound;
