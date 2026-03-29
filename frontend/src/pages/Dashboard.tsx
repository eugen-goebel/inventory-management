import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Package, Euro, AlertTriangle, ArrowLeftRight } from "lucide-react";
import { fetchAnalytics } from "../api/client";
import type { DashboardAnalytics } from "../types";
import KpiCard from "../components/KpiCard";
import LoadingSpinner from "../components/LoadingSpinner";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"];

function formatEur(value: number): string {
  return value.toLocaleString("de-DE", { style: "currency", currency: "EUR" });
}

function formatNumber(value: number): string {
  return value.toLocaleString("de-DE");
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error)
    return <div className="text-red-600 bg-red-50 p-4 rounded">{error}</div>;
  if (!data) return null;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KpiCard
          title="Total Products"
          value={formatNumber(data.total_products)}
          icon={Package}
          color="border-blue-500"
        />
        <KpiCard
          title="Stock Value"
          value={formatEur(data.total_stock_value)}
          icon={Euro}
          color="border-green-500"
        />
        <KpiCard
          title="Low Stock Alerts"
          value={formatNumber(data.low_stock_count)}
          icon={AlertTriangle}
          color={data.low_stock_count > 0 ? "border-red-500" : "border-red-300"}
        />
        <KpiCard
          title="Movements Today"
          value={formatNumber(data.total_movements_today)}
          icon={ArrowLeftRight}
          color="border-purple-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Stock Value by Category
          </h2>
          {data.stock_by_category.length === 0 ? (
            <p className="text-gray-500 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.stock_by_category}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" fontSize={12} />
                <YAxis
                  fontSize={12}
                  tickFormatter={(v: number) => formatEur(v)}
                />
                <Tooltip
                  formatter={(value: number) => formatEur(value)}
                  labelStyle={{ fontWeight: 600 }}
                />
                <Bar dataKey="total_value" radius={[4, 4, 0, 0]}>
                  {data.stock_by_category.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Top 10 Products by Value
          </h2>
          {data.top_products.length === 0 ? (
            <p className="text-gray-500 text-sm">No data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.top_products} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  fontSize={12}
                  tickFormatter={(v: number) => formatEur(v)}
                />
                <YAxis
                  dataKey="name"
                  type="category"
                  width={120}
                  fontSize={11}
                />
                <Tooltip
                  formatter={(value: number) => formatEur(value)}
                  labelStyle={{ fontWeight: 600 }}
                />
                <Bar dataKey="stock_value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Movements
        </h2>
        {data.recent_movements.length === 0 ? (
          <p className="text-gray-500 text-sm">No recent movements</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-3 font-medium">Date</th>
                  <th className="pb-3 font-medium">Product</th>
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium text-right">Quantity</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_movements.map((m, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-3 text-gray-600">
                      {formatDate(m.created_at)}
                    </td>
                    <td className="py-3 text-gray-900">{m.product_name}</td>
                    <td className="py-3">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                          m.movement_type === "in"
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {m.movement_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 text-right text-gray-900">
                      {formatNumber(m.quantity)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
