#!/usr/bin/env bash
set -euo pipefail

# 0. Must be root
if [[ $EUID -ne 0 ]]; then
  echo "⚠️  Please run as root (e.g. sudo $0)"
  exit 1
fi

# 1. Remove any old azure-functions repo to avoid 404s
rm -f /etc/apt/sources.list.d/azure-functions.list

# 2. Install prerequisites
apt-get update
apt-get install -y curl apt-transport-https lsb-release gnupg

# 3. Import Microsoft’s package signing key
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
  | gpg --dearmor \
  > /etc/apt/trusted.gpg.d/microsoft.gpg

# 4. Add the Debian Bookworm feed
DEB_MAJOR=$(lsb_release -rs | cut -d'.' -f1)       # "12"
DEB_CODENAME=$(lsb_release -cs)                   # "bookworm"
cat > /etc/apt/sources.list.d/dotnetdev.list <<EOF
deb [arch=amd64] https://packages.microsoft.com/debian/$DEB_MAJOR/prod $DEB_CODENAME main
EOF
# (This is the feed that actually contains azure-functions-core-tools-4) :contentReference[oaicite:1]{index=1}

# 5. Install Core Tools v4
apt-get update
apt-get install -y azure-functions-core-tools-4

# 6. Verify
echo "✅ func version: $(func --version)"
