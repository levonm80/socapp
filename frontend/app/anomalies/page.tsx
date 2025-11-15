'use client';

export default function AnomaliesPage() {
  return (
    <div className="min-h-screen bg-background-dark p-8">
      <h1 className="text-4xl font-black text-white">Anomalies</h1>
      <p className="mt-4 text-base text-gray-400">
        View and investigate detected anomalies
      </p>
      <div className="mt-8 rounded-xl border border-border-dark bg-component-dark p-6">
        <p className="text-text-secondary-dark">Anomalies implementation - list, timeline, drill-down</p>
      </div>
    </div>
  );
}

