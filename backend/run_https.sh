#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CERT_DIR="${PROJECT_ROOT}/backend/certs"
CERT_FILE="${CERT_DIR}/dev-cert.pem"
KEY_FILE="${CERT_DIR}/dev-key.pem"
IP_ADDR="${IP_ADDR:-$(ipconfig getifaddr en0 || ipconfig getifaddr en1 || echo 127.0.0.1)}"
PORT="${PORT:-8443}"

mkdir -p "${CERT_DIR}"

if [[ ! -f "${CERT_FILE}" || ! -f "${KEY_FILE}" ]]; then
  TMP_CONF="$(mktemp)"
  cat > "${TMP_CONF}" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = dn

[dn]
C = TR
ST = TR
L = Mersin
O = Sektor Rehberim
OU = Dev
CN = localhost

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
IP.2 = ${IP_ADDR}
EOF

  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${KEY_FILE}" \
    -out "${CERT_FILE}" \
    -config "${TMP_CONF}" >/dev/null 2>&1
  rm -f "${TMP_CONF}"
fi

echo "HTTPS app starting on https://0.0.0.0:${PORT}"
echo "Local: https://localhost:${PORT}"
echo "Phone (same Wi-Fi): https://${IP_ADDR}:${PORT}"

exec "${PROJECT_ROOT}/.venv/bin/uvicorn" backend.app.main:app \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --ssl-keyfile "${KEY_FILE}" \
  --ssl-certfile "${CERT_FILE}"

