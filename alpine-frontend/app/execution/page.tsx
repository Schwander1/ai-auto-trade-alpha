"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useRequireAdmin } from "@/lib/admin";
import Navigation from "@/components/dashboard/Navigation";
import {
  Loader2,
  AlertCircle,
  Shield,
  Lock,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
} from "lucide-react";

/**
 * Execution Dashboard - Admin Only
 * Private dashboard for monitoring signal execution
 */
export default function ExecutionDashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { isAdmin, isLoading, isAuthenticated } = useRequireAdmin();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [rejectionReasons, setRejectionReasons] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAdmin || !isAuthenticated) return;

    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [metricsRes, queueRes, accountsRes, reasonsRes] = await Promise.all([
          fetch("/api/execution/metrics"),
          fetch("/api/execution/queue"),
          fetch("/api/execution/account-states"),
          fetch("/api/execution/rejection-reasons").catch(() => null), // Optional
        ]);

        if (metricsRes.status === 403 || queueRes.status === 403 || accountsRes.status === 403) {
          setError("Admin access required");
          return;
        }

        if (!metricsRes.ok || !queueRes.ok || !accountsRes.ok) {
          throw new Error("Failed to load dashboard data");
        }

        const [metrics, queue, accounts] = await Promise.all([
          metricsRes.json(),
          queueRes.json(),
          accountsRes.json(),
        ]);

        setDashboardData({ metrics, queue, accounts });

        // Fetch rejection reasons if available
        if (reasonsRes && reasonsRes.ok) {
          const reasons = await reasonsRes.json();
          setRejectionReasons(reasons);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [isAdmin, isAuthenticated]);

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-alpine-black-primary flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-alpine-neon-cyan animate-spin" />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-alpine-black-primary flex items-center justify-center">
        <div className="text-center max-w-md">
          <Shield className="w-16 h-16 text-alpine-semantic-error mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-alpine-text-primary mb-2">
            Admin Access Required
          </h2>
          <p className="text-alpine-text-secondary mb-4">
            This dashboard is restricted to administrators only.
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="px-4 py-2 bg-alpine-neon-cyan text-alpine-black-primary rounded-lg hover:bg-alpine-neon-cyan/80"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-alpine-black-primary flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-alpine-semantic-error mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-alpine-text-primary mb-2">Error</h2>
          <p className="text-alpine-text-secondary">{error}</p>
        </div>
      </div>
    );
  }

  const { metrics, queue, accounts } = dashboardData || {};

  return (
    <div className="min-h-screen bg-alpine-black-primary">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-alpine-text-primary mb-2">
              Execution Dashboard
            </h1>
            <p className="text-alpine-text-secondary">
              Admin-only monitoring and control center
            </p>
          </div>
          <div className="flex items-center gap-2 text-alpine-neon-cyan">
            <Lock className="w-5 h-5" />
            <span className="text-sm font-semibold">Admin Only</span>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-alpine-text-secondary text-sm">Execution Rate</span>
              <TrendingUp className="w-5 h-5 text-alpine-neon-cyan" />
            </div>
            <div className="text-3xl font-bold text-alpine-neon-cyan">
              {metrics?.execution_rate?.toFixed(1) || "0"}%
            </div>
          </div>

          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-alpine-text-secondary text-sm">Queue Pending</span>
              <Clock className="w-5 h-5 text-alpine-orange" />
            </div>
            <div className="text-3xl font-bold text-alpine-orange">
              {queue?.stats?.pending || 0}
            </div>
          </div>

          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-alpine-text-secondary text-sm">Queue Ready</span>
              <CheckCircle className="w-5 h-5 text-alpine-semantic-success" />
            </div>
            <div className="text-3xl font-bold text-alpine-semantic-success">
              {queue?.stats?.ready || 0}
            </div>
          </div>

          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-alpine-text-secondary text-sm">Signals Executed</span>
              <CheckCircle className="w-5 h-5 text-alpine-neon-cyan" />
            </div>
            <div className="text-3xl font-bold text-alpine-neon-cyan">
              {metrics?.signals_executed || 0}
            </div>
          </div>
        </div>

        {/* Queue Status */}
        {queue && (
          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-alpine-text-primary mb-4">Queue Status</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(queue.stats || {}).map(([status, count]: [string, any]) => (
                <div key={status} className="text-center">
                  <div className="text-2xl font-bold text-alpine-text-primary">{count}</div>
                  <div className="text-sm text-alpine-text-secondary capitalize">{status}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Rejection Reasons */}
        {rejectionReasons && Object.keys(rejectionReasons.reasons || {}).length > 0 && (
          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-alpine-text-primary mb-4">Rejection Reasons (Last {rejectionReasons.hours}h)</h2>
            <div className="space-y-2">
              {Object.entries(rejectionReasons.reasons)
                .sort(([, a]: [string, any], [, b]: [string, any]) => b - a)
                .slice(0, 10)
                .map(([reason, count]: [string, any]) => (
                  <div key={reason} className="flex items-center justify-between p-3 bg-alpine-black-primary rounded-lg">
                    <span className="text-alpine-text-secondary text-sm flex-1 truncate mr-4">{reason}</span>
                    <span className="text-alpine-text-primary font-semibold">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Queue Signals Table */}
        {queue && queue.signals && queue.signals.length > 0 && (
          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-alpine-text-primary mb-4">Queued Signals</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-alpine-black-border">
                    <th className="text-left p-2 text-alpine-text-secondary text-sm">Symbol</th>
                    <th className="text-left p-2 text-alpine-text-secondary text-sm">Action</th>
                    <th className="text-left p-2 text-alpine-text-secondary text-sm">Confidence</th>
                    <th className="text-left p-2 text-alpine-text-secondary text-sm">Status</th>
                    <th className="text-left p-2 text-alpine-text-secondary text-sm">Queued</th>
                  </tr>
                </thead>
                <tbody>
                  {queue.signals.slice(0, 20).map((signal: any) => (
                    <tr key={signal.signal_id} className="border-b border-alpine-black-border">
                      <td className="p-2 text-alpine-text-primary">{signal.symbol}</td>
                      <td className="p-2 text-alpine-text-primary">{signal.action}</td>
                      <td className="p-2 text-alpine-text-primary">{signal.confidence.toFixed(1)}%</td>
                      <td className="p-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          signal.status === 'ready' ? 'bg-alpine-semantic-success/20 text-alpine-semantic-success' :
                          signal.status === 'pending' ? 'bg-alpine-orange/20 text-alpine-orange' :
                          'bg-alpine-text-secondary/20 text-alpine-text-secondary'
                        }`}>
                          {signal.status}
                        </span>
                      </td>
                      <td className="p-2 text-alpine-text-secondary text-sm">
                        {new Date(signal.queued_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Account States */}
        {accounts && Object.keys(accounts).length > 0 && (
          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-xl p-6">
            <h2 className="text-xl font-bold text-alpine-text-primary mb-4">Account States</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(accounts).map(([executorId, state]: [string, any]) => (
                <div key={executorId} className="border border-alpine-black-border rounded-lg p-4">
                  <h3 className="font-semibold text-alpine-text-primary mb-2 capitalize">
                    {executorId.replace('_', ' ')}
                  </h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-alpine-text-secondary">Buying Power:</span>
                      <span className={`font-semibold ${
                        (state.buying_power || 0) > 0 ? 'text-alpine-semantic-success' : 'text-alpine-semantic-error'
                      }`}>
                        ${state.buying_power?.toFixed(2) || "0.00"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-alpine-text-secondary">Portfolio Value:</span>
                      <span className="text-alpine-text-primary">
                        ${state.portfolio_value?.toFixed(2) || "0.00"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-alpine-text-secondary">Positions:</span>
                      <span className="text-alpine-text-primary">
                        {state.positions_count || 0}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-alpine-text-secondary mt-2 pt-2 border-t border-alpine-black-border">
                      <span>Last Update:</span>
                      <span>{new Date(state.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
