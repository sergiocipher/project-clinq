#!/bin/sh
# WHY THIS FILE EXISTS:
# Posts realistic sample appointments so the UI screenshots look like a
# real clinic system rather than an empty table. Safe to run multiple times
# (it only adds records, never deletes).
# Usage: bash scripts/seed.sh http://localhost:8000
set -e

BASE_URL="${1:-http://localhost:8000}"
ENDPOINT="${BASE_URL}/api/appointments"

echo "Seeding appointments to ${ENDPOINT}..."

post() {
  curl -sf -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d "$1" > /dev/null && echo "  ✓ created: $(echo "$1" | grep -o '"patient_name":"[^"]*"')"
}

post '{"patient_name":"Alice Sharma","doctor":"Dr. Priya Nair","scheduled_at":"2025-07-01T09:00:00","status":"scheduled","priority":"normal","notes":"Annual blood work follow-up"}'
post '{"patient_name":"Bob Fernandez","doctor":"Dr. Ankit Gupta","scheduled_at":"2025-07-01T10:30:00","status":"scheduled","priority":"urgent","notes":"Chest pain — ECG required"}'
post '{"patient_name":"Carol Mehta","doctor":"Dr. Priya Nair","scheduled_at":"2025-06-28T14:00:00","status":"completed","priority":"low","notes":"Routine vaccination"}'
post '{"patient_name":"David Okonkwo","doctor":"Dr. Ravi Sharma","scheduled_at":"2025-06-29T11:00:00","status":"completed","priority":"normal","notes":"Post-surgery review"}'
post '{"patient_name":"Eva Lindqvist","doctor":"Dr. Ankit Gupta","scheduled_at":"2025-07-03T08:30:00","status":"scheduled","priority":"normal","notes":""}'
post '{"patient_name":"Fatima Al-Hassan","doctor":"Dr. Ravi Sharma","scheduled_at":"2025-06-30T16:00:00","status":"cancelled","priority":"low","notes":"Patient rescheduled"}'
post '{"patient_name":"George Tanaka","doctor":"Dr. Priya Nair","scheduled_at":"2025-07-05T09:30:00","status":"scheduled","priority":"urgent","notes":"Diabetic review — HbA1c results"}'
post '{"patient_name":"Hannah Reyes","doctor":"Dr. Ankit Gupta","scheduled_at":"2025-07-02T13:00:00","status":"scheduled","priority":"normal","notes":"Hypertension check"}'
post '{"patient_name":"Ivan Petrov","doctor":"Dr. Ravi Sharma","scheduled_at":"2025-06-27T15:00:00","status":"completed","priority":"normal","notes":"Physiotherapy assessment"}'
post '{"patient_name":"Julia Nakamura","doctor":"Dr. Priya Nair","scheduled_at":"2025-07-07T10:00:00","status":"scheduled","priority":"low","notes":"Prenatal check-up week 20"}'

echo "Done. Run 'curl ${BASE_URL}/api/appointments/stats' to verify."
