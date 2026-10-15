import React, { useState } from "react";

const STATUSES = ["scheduled", "completed", "cancelled"];
const PRIORITIES = ["low", "normal", "urgent"];

function toDatetimeLocal(iso) {
  if (!iso) return "";
  // Trim to "YYYY-MM-DDTHH:MM" for the datetime-local input
  return new Date(iso).toISOString().slice(0, 16);
}

export default function AppointmentModal({ initial, onSave, onClose }) {
  const [form, setForm] = useState({
    patient_name: initial?.patient_name ?? "",
    doctor: initial?.doctor ?? "",
    scheduled_at: toDatetimeLocal(initial?.scheduled_at),
    notes: initial?.notes ?? "",
    status: initial?.status ?? "scheduled",
    priority: initial?.priority ?? "normal",
  });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: null }));
  }

  function validate() {
    const errs = {};
    if (!form.patient_name.trim()) errs.patient_name = "Required";
    if (!form.doctor.trim()) errs.doctor = "Required";
    if (!form.scheduled_at) errs.scheduled_at = "Required";
    return errs;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setSaving(true);
    try {
      await onSave({
        ...form,
        notes: form.notes.trim() || null,
        scheduled_at: new Date(form.scheduled_at).toISOString(),
      });
    } catch (err) {
      setErrors({ _global: err.message });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h3>{initial ? "Edit Appointment" : "New Appointment"}</h3>
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-row">
            <div className="form-group">
              <label>Patient Name *</label>
              <input
                type="text"
                value={form.patient_name}
                onChange={(e) => set("patient_name", e.target.value)}
                placeholder="e.g. Alice Smith"
              />
              {errors.patient_name && <div className="error-msg">{errors.patient_name}</div>}
            </div>
            <div className="form-group">
              <label>Doctor *</label>
              <input
                type="text"
                value={form.doctor}
                onChange={(e) => set("doctor", e.target.value)}
                placeholder="e.g. Dr. Chen"
              />
              {errors.doctor && <div className="error-msg">{errors.doctor}</div>}
            </div>
          </div>

          <div className="form-group">
            <label>Scheduled At *</label>
            <input
              type="datetime-local"
              value={form.scheduled_at}
              onChange={(e) => set("scheduled_at", e.target.value)}
            />
            {errors.scheduled_at && <div className="error-msg">{errors.scheduled_at}</div>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Status</label>
              <select value={form.status} onChange={(e) => set("status", e.target.value)}>
                {STATUSES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Priority</label>
              <select value={form.priority} onChange={(e) => set("priority", e.target.value)}>
                {PRIORITIES.map((p) => <option key={p}>{p}</option>)}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => set("notes", e.target.value)}
              placeholder="Optional notes…"
            />
          </div>

          {errors._global && <div className="error-msg">{errors._global}</div>}

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving…" : initial ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
