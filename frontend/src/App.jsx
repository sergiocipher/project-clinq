import React, { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import AppointmentModal from "./components/AppointmentModal.jsx";

const APP_VERSION = import.meta.env.VITE_APP_VERSION ?? "dev";

function Badge({ type, value }) {
  return <span className={`badge badge-${value}`}>{value}</span>;
}

function KpiCard({ label, value, color }) {
  return (
    <div className="kpi-card">
      <div className="label">{label}</div>
      <div className="value" style={color ? { color } : {}}>
        {value ?? "—"}
      </div>
    </div>
  );
}

const STATUS_FILTERS = ["all", "scheduled", "completed", "cancelled"];

export default function App() {
  const [appointments, setAppointments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null); // null = create, object = edit
  const [deleteTarget, setDeleteTarget] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (statusFilter !== "all") params.status = statusFilter;
      if (search.trim()) params.q = search.trim();
      const [data, statsData] = await Promise.all([
        api.list(params),
        api.stats(),
      ]);
      setAppointments(data);
      setStats(statsData);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, search]);

  useEffect(() => {
    load();
  }, [load]);

  function handleNew() {
    setEditing(null);
    setModalOpen(true);
  }
  function handleEdit(appt) {
    setEditing(appt);
    setModalOpen(true);
  }
  async function handleDelete(appt) {
    if (!window.confirm(`Delete appointment for ${appt.patient_name}?`)) return;
    await api.remove(appt.id);
    load();
  }
  async function handleSave(data) {
    if (editing) {
      await api.update(editing.id, data);
    } else {
      await api.create(data);
    }
    setModalOpen(false);
    load();
  }

  const recent = [...appointments]
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    .slice(0, 5);

  return (
    <div className="layout">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>ClinQ</h1>
          <p>Appointment Booking</p>
        </div>
        <nav className="sidebar-nav">
          <a href="#" className="active">📅 Appointments</a>
          <a href="#">📊 Analytics</a>
          <a href="#">👨‍⚕️ Doctors</a>
          <a href="#">⚙️ Settings</a>
        </nav>
        <div className="sidebar-footer">
          build: {APP_VERSION.slice(0, 7)}
        </div>
      </aside>

      {/* ── Main ────────────────────────────────────────────── */}
      <div className="main">
        <header className="topbar">
          <h2>Appointments</h2>
          <button className="btn btn-primary" onClick={handleNew}>
            + New Appointment
          </button>
        </header>

        <div className="content">
          {/* KPI cards */}
          {stats && (
            <div className="kpi-grid">
              <KpiCard label="Total" value={stats.total} />
              <KpiCard
                label="Scheduled"
                value={stats.by_status.scheduled}
                color="var(--accent)"
              />
              <KpiCard
                label="Completed"
                value={stats.by_status.completed}
                color="var(--success)"
              />
              <KpiCard
                label="Cancelled"
                value={stats.by_status.cancelled}
                color="var(--danger)"
              />
              <KpiCard
                label="Upcoming"
                value={stats.upcoming_count}
                color="var(--warn)"
              />
            </div>
          )}

          {/* Toolbar */}
          <div className="toolbar">
            <input
              type="text"
              placeholder="Search patient or doctor…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <div className="chips">
              {STATUS_FILTERS.map((s) => (
                <button
                  key={s}
                  className={`chip ${statusFilter === s ? "active" : ""}`}
                  onClick={() => setStatusFilter(s)}
                >
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Table / states */}
          {error ? (
            <div className="error-state">
              <div className="err-icon">⚠️</div>
              <p>{error}</p>
              <button className="btn btn-secondary" onClick={load}>
                Retry
              </button>
            </div>
          ) : loading ? (
            <div className="table-wrap">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton skeleton-row" />
              ))}
            </div>
          ) : appointments.length === 0 ? (
            <div className="empty-state">No appointments found.</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Scheduled At</th>
                    <th>Status</th>
                    <th>Priority</th>
                    <th>Notes</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((a) => (
                    <tr key={a.id}>
                      <td data-label="Patient">{a.patient_name}</td>
                      <td data-label="Doctor">{a.doctor}</td>
                      <td data-label="Scheduled At">
                        {new Date(a.scheduled_at).toLocaleString()}
                      </td>
                      <td data-label="Status">
                        <Badge value={a.status} />
                      </td>
                      <td data-label="Priority">
                        <Badge value={a.priority} />
                      </td>
                      <td data-label="Notes">
                        {a.notes ? (
                          <span title={a.notes}>
                            {a.notes.length > 40
                              ? a.notes.slice(0, 40) + "…"
                              : a.notes}
                          </span>
                        ) : (
                          <span style={{ color: "var(--muted)" }}>—</span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: 4 }}>
                          <button
                            className="btn btn-icon"
                            title="Edit"
                            onClick={() => handleEdit(a)}
                          >
                            ✏️
                          </button>
                          <button
                            className="btn btn-icon"
                            title="Delete"
                            onClick={() => handleDelete(a)}
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Recent activity */}
          {!loading && !error && recent.length > 0 && (
            <div className="activity-section">
              <h3>Recent Activity</h3>
              <div className="activity-list">
                {recent.map((a) => (
                  <div className="activity-item" key={a.id}>
                    <div>
                      <div className="name">{a.patient_name}</div>
                      <div className="meta">Dr. {a.doctor}</div>
                    </div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <Badge value={a.status} />
                      <span className="meta">
                        {new Date(a.updated_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Modal ───────────────────────────────────────────── */}
      {modalOpen && (
        <AppointmentModal
          initial={editing}
          onSave={handleSave}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}
