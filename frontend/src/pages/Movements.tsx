import { useEffect, useState, useCallback } from "react";
import { Plus } from "lucide-react";
import {
  fetchMovements,
  fetchProducts,
  createMovement,
} from "../api/client";
import type { Movement, MovementCreate, Product } from "../types";
import Modal from "../components/Modal";
import LoadingSpinner from "../components/LoadingSpinner";

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

const emptyForm: MovementCreate = {
  product_id: 0,
  movement_type: "in",
  quantity: 1,
  reference: "",
  notes: "",
};

export default function Movements() {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [filterProduct, setFilterProduct] = useState<number | undefined>(
    undefined
  );
  const [filterType, setFilterType] = useState("all");

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<MovementCreate>(emptyForm);
  const [saving, setSaving] = useState(false);

  const loadMovements = useCallback(() => {
    setLoading(true);
    fetchMovements({
      product_id: filterProduct,
      movement_type: filterType !== "all" ? filterType : undefined,
    })
      .then(setMovements)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [filterProduct, filterType]);

  useEffect(() => {
    loadMovements();
  }, [loadMovements]);

  useEffect(() => {
    fetchProducts().then(setProducts).catch(() => {});
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await createMovement(form);
      setModalOpen(false);
      setForm(emptyForm);
      loadMovements();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to record movement");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Movements</h1>
        <button
          onClick={() => {
            setForm(emptyForm);
            setModalOpen(true);
          }}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          Record Movement
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <select
            value={filterProduct ?? ""}
            onChange={(e) =>
              setFilterProduct(
                e.target.value ? Number(e.target.value) : undefined
              )
            }
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Products</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Types</option>
            <option value="in">IN</option>
            <option value="out">OUT</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="text-red-600 bg-red-50 p-4 rounded mb-4">{error}</div>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-left text-gray-500">
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Product</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium text-right">Quantity</th>
                <th className="px-4 py-3 font-medium">Reference</th>
                <th className="px-4 py-3 font-medium">Notes</th>
              </tr>
            </thead>
            <tbody>
              {movements.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-4 py-8 text-center text-gray-500"
                  >
                    No movements found
                  </td>
                </tr>
              ) : (
                movements.map((m) => (
                  <tr
                    key={m.id}
                    className="border-b last:border-0 hover:bg-gray-50"
                  >
                    <td className="px-4 py-3 text-gray-600">
                      {formatDate(m.created_at)}
                    </td>
                    <td className="px-4 py-3 text-gray-900 font-medium">
                      {m.product_name}
                    </td>
                    <td className="px-4 py-3">
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
                    <td className="px-4 py-3 text-right text-gray-900">
                      {formatNumber(m.quantity)}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{m.reference}</td>
                    <td className="px-4 py-3 text-gray-600">{m.notes}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Record Movement Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Record Movement"
      >
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Product
            </label>
            <select
              required
              value={form.product_id}
              onChange={(e) =>
                setForm({ ...form, product_id: Number(e.target.value) })
              }
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={0} disabled>
                Select a product
              </option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.sku})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="movement_type"
                  value="in"
                  checked={form.movement_type === "in"}
                  onChange={() => setForm({ ...form, movement_type: "in" })}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700">Stock In</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="movement_type"
                  value="out"
                  checked={form.movement_type === "out"}
                  onChange={() => setForm({ ...form, movement_type: "out" })}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700">Stock Out</span>
              </label>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantity
            </label>
            <input
              type="number"
              required
              min="1"
              value={form.quantity}
              onChange={(e) =>
                setForm({ ...form, quantity: Number(e.target.value) })
              }
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reference
            </label>
            <input
              type="text"
              value={form.reference}
              onChange={(e) => setForm({ ...form, reference: e.target.value })}
              placeholder="e.g. PO-2024-001"
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              rows={3}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setModalOpen(false)}
              className="px-4 py-2 text-sm text-gray-700 border rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Record"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
