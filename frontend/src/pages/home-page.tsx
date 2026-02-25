import { useHealth } from "@/hooks/use-health";

export function HomePage() {
  const { status, loading, error } = useHealth();

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Client Agent</h1>
      <div className="p-4 border rounded-lg">
        <h2 className="text-lg font-semibold mb-2">API Status</h2>
        {loading && <p className="text-gray-500">Checking...</p>}
        {error && <p className="text-red-500">{error}</p>}
        {!loading && !error && (
          <p className="text-green-600" data-testid="health-status">
            {status}
          </p>
        )}
      </div>
    </div>
  );
}
