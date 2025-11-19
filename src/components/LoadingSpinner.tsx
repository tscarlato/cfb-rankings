export const LoadingSpinner = () => {
  return (
    <div className="bg-card rounded-2xl shadow-xl p-12 text-center border border-border animate-scale-in">
      <div className="inline-block text-primary text-6xl mb-6 animate-spin">
        <i className="fas fa-spinner"></i>
      </div>
      <p className="text-3xl text-foreground font-bold mb-2">Loading rankings...</p>
      <p className="text-muted-foreground text-lg">Calculating team performance metrics</p>
    </div>
  );
};
