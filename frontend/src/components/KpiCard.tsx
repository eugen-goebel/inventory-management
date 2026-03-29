import type { LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  color: string;
}

export default function KpiCard({ title, value, icon: Icon, color }: KpiCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow p-6 border-t-4 ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className="p-3 bg-gray-50 rounded-full">
          <Icon className="w-6 h-6 text-gray-600" />
        </div>
      </div>
    </div>
  );
}
