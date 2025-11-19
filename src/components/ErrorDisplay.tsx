interface ErrorDisplayProps {
  error: string;
  onRetry: () => void;
}

export const ErrorDisplay = ({ error, onRetry }: ErrorDisplayProps) => {
  return (
    <div className="bg-card rounded-2xl shadow-xl p-12 text-center border border-border animate-scale-in">
      <i className="fas fa-exclamation-circle text-destructive text-6xl mb-6"></i>
      <h2 className="text-3xl font-bold text-foreground mb-3">Error Loading Rankings</h2>
      <p className="text-muted-foreground mb-6 text-lg">{error}</p>
      <button
        onClick={onRetry}
        className="bg-gradient-primary text-white px-8 py-4 rounded-xl hover:opacity-90 font-bold text-lg shadow-lg hover:shadow-xl transition-all hover:scale-105 active:scale-95"
      >
        Try Again
      </button>
    </div>
  );
};
