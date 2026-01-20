interface ToastProps {
  message: string;
}

export default function Toast({ message }: ToastProps) {
  return (
    <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50 animate-fade-in">
      <div className="bg-bg-card border border-accent-decisions px-6 py-3 rounded-lg shadow-2xl">
        <p className="text-sm text-text-primary">{message}</p>
      </div>
    </div>
  );
}
