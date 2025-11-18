"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Navigation from "@/components/dashboard/Navigation";
import PerformanceChart from "@/components/dashboard/PerformanceChart";
import {
  TrendingUp,
  Users,
  DollarSign,
  Activity,
  Loader2,
  AlertCircle,
  BarChart3,
  Calendar,
  Download,
} from "lucide-react";

/**
 * Admin Page - Revenue, users, and analytics (admin only)
 */
export default function AdminPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [analytics, setAnalytics] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [revenue, setRevenue] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "users" | "revenue">("overview");

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    const fetchAdminData = async () => {
      if (!session) return;

      try {
        setIsLoading(true);
        const [analyticsRes, usersRes, revenueRes] = await Promise.all([
          fetch("/api/admin/analytics"),
          fetch("/api/admin/users?limit=50"),
          fetch("/api/admin/revenue"),
        ]);

        if (analyticsRes.ok) {
          const data = await analyticsRes.json();
          setAnalytics(data);
        } else if (analyticsRes.status === 403) {
          setError("Admin access required");
        }

        if (usersRes.ok) {
          const data = await usersRes.json();
          setUsers(data.items || []);
        }

        if (revenueRes.ok) {
          const data = await revenueRes.json();
          setRevenue(data);
        }
      } catch (err) {
        console.error("Failed to fetch admin data:", err);
        setError("Failed to load admin data");
      } finally {
        setIsLoading(false);
      }
    };

    if (session) {
      fetchAdminData();
    }
  }, [session]);

  if (status === "loading" || isLoading) {
    return (
      <div className="min-h-screen bg-alpine-black-primary flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-alpine-neon-cyan animate-spin" />
      </div>
    );
  }

  if (status === "unauthenticated") {
    return null;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-alpine-black-primary flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-alpine-semantic-error mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-alpine-text-primary mb-2">Access Denied</h2>
          <p className="text-alpine-text-secondary">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-alpine-black-primary">
      {/* Navigation */}
      <Navigation />

      <main className="container mx-auto px-4 py-6">
        {/* Tabs */}
        <div className="flex items-center gap-2 mb-6 border-b border-alpine-black-border">
          {[
            { id: "overview", label: "Overview" },
            { id: "users", label: "Users" },
            { id: "revenue", label: "Revenue" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 font-semibold transition-colors ${
                activeTab === tab.id
                  ? "text-alpine-neon-cyan border-b-2 border-alpine-neon-cyan"
                  : "text-alpine-text-secondary hover:text-alpine-text-primary"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && analytics && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Total Users"
                value={analytics.total_users}
                icon={<Users className="w-5 h-5" />}
                color="alpine-neoncya-n"
              />
              <StatCard
                title="Active Users"
                value={analytics.active_users}
                icon={<Activity className="w-5 h-5" />}
                color="alpine-neonpin-k"
              />
              <StatCard
                title="New Users (Month)"
                value={analytics.new_users_this_month}
                icon={<TrendingUp className="w-5 h-5" />}
                color="alpine-neon-purple"
              />
              <StatCard
                title="Signals Delivered"
                value={analytics.signals_delivered_this_month}
                icon={<BarChart3 className="w-5 h-5" />}
                color="alpine-semantic-success"
              />
            </div>

            {/* Users by Tier */}
            <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-alpine-text-primary mb-4">Users by Tier</h3>
              <div className="grid grid-cols-3 gap-4">
                {Object.entries(analytics.users_by_tier || {}).map(
                  ([tier, count]: [string, any]) => (
                    <div key={tier} className="text-center p-4 bg-alpine-black-primary rounded-lg">
                      <div className="text-2xl font-black text-alpine-text-primary mb-1">
                        {count}
                      </div>
                      <div className="text-sm text-alpine-text-secondary capitalize">{tier}</div>
                    </div>
                  )
                )}
              </div>
            </div>

            {/* Activity Chart */}
            <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-alpine-text-primary mb-4">Platform Activity</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-alpine-text-secondary mb-1">
                    API Requests (Today)
                  </div>
                  <div className="text-2xl font-black text-alpine-text-primary ">
                    {analytics.api_requests_today?.toLocaleString() || 0}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-alpine-text-secondary mb-1">Error Rate</div>
                  <div className="text-2xl font-black text-alpine-text-primary ">
                    {analytics.error_rate?.toFixed(2)}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === "users" && (
          <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg overflow-hidden">
            <div className="p-4 border-b border-alpine-black-border flex items-center justify-between">
              <h3 className="text-lg font-bold text-alpine-text-primary ">All Users</h3>
              <button className="px-4 py-2 text-sm bg-alpine-black-border hover:bg-alpine-black-border/80 text-alpine-text-primary rounded-lg transition-colors flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-alpine-black-primary border border-alpine-black-border">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-alpine-text-secondary uppercase">
                      Email
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-alpine-text-secondary uppercase">
                      Tier
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-alpine-text-secondary uppercase">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-alpine-text-secondary uppercase">
                      Joined
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-alpine-black-border">
                  {users.map((user: any) => (
                    <tr
                      key={user.id}
                      className="hover:bg-alpine-black-primary/50 transition-colors"
                    >
                      <td className="px-4 py-3 text-alpine-text-primary ">{user.email}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-sm font-semibold rounded bg-alpine-neon-cyan/10 text-alpine-neon-cyan capitalize">
                          {user.tier}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-1 text-sm font-semibold rounded ${
                            user.is_active
                              ? "bg-alpine-neon-cyan/10 text-alpine-neon-cyan"
                              : "bg-alpine-semantic-error/10 text-alpine-semantic-error"
                          }`}
                        >
                          {user.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-alpine-text-secondary">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Revenue Tab */}
        {activeTab === "revenue" && revenue && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title="Total Revenue"
                value={`$${revenue.total_revenue?.toLocaleString() || 0}`}
                icon={<DollarSign className="w-5 h-5" />}
                color="alpine-neoncya-n"
              />
              <StatCard
                title="MRR"
                value={`$${revenue.mrr?.toLocaleString() || 0}`}
                icon={<TrendingUp className="w-5 h-5" />}
                color="alpine-neonpin-k"
              />
              <StatCard
                title="Active Subscriptions"
                value={revenue.active_subscriptions || 0}
                icon={<Users className="w-5 h-5" />}
                color="alpine-neon-purple"
              />
              <StatCard
                title="Churn Rate"
                value={`${revenue.churn_rate?.toFixed(1)}%`}
                icon={<Activity className="w-5 h-5" />}
                color="alpine-semantic-error"
              />
            </div>

            <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
              <h3 className="text-lg font-bold text-alpine-text-primary mb-4">Revenue by Tier</h3>
              <div className="grid grid-cols-3 gap-4">
                {Object.entries(revenue.revenue_by_tier || {}).map(
                  ([tier, amount]: [string, any]) => (
                    <div key={tier} className="text-center p-4 bg-alpine-black-primary rounded-lg">
                      <div className="text-2xl font-black text-alpine-text-primary mb-1">
                        ${amount?.toLocaleString() || 0}
                      </div>
                      <div className="text-sm text-alpine-text-secondary capitalize">{tier}</div>
                    </div>
                  )
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-4">
                <div className="text-sm text-alpine-text-secondary mb-1">Revenue Today</div>
                <div className="text-xl font-black text-alpine-text-primary ">
                  ${revenue.revenue_today?.toFixed(2) || "0.00"}
                </div>
              </div>
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-4">
                <div className="text-sm text-alpine-text-secondary mb-1">Revenue This Week</div>
                <div className="text-xl font-black text-alpine-text-primary ">
                  ${revenue.revenue_this_week?.toFixed(2) || "0.00"}
                </div>
              </div>
              <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-4">
                <div className="text-sm text-alpine-text-secondary mb-1">Revenue This Month</div>
                <div className="text-xl font-black text-alpine-text-primary ">
                  ${revenue.revenue_this_month?.toFixed(2) || "0.00"}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function StatCard({ title, value, icon, color }: any) {
  return (
    <div className="bg-alpine-black-secondary border border-alpine-black-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <div className={`p-2 rounded-lg bg-${color}/10 text-${color}`}>{icon}</div>
      </div>
      <div className="text-2xl font-black text-alpine-text-primary mb-1">{value}</div>
      <div className="text-sm text-alpine-text-secondary">{title}</div>
    </div>
  );
}
