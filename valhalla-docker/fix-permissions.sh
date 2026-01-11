#!/bin/bash
# Bash script to fix permissions for Valhalla volumes
# Configures permissions for UID 59999 and GID 59999

echo "========================================"
echo "Valhalla Permissions Fix"
echo "========================================"
echo ""
echo "Configuring permissions for UID: 59999, GID: 59999"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠ Note: Not running as root (sudo)"
    echo "  Some permission changes may require sudo"
    echo ""
fi

# Create valhalla user/group if they don't exist
if ! getent group 59999 > /dev/null 2>&1; then
    echo "Creating group with GID 59999..."
    if command -v groupadd > /dev/null 2>&1; then
        sudo groupadd -g 59999 valhalla || echo "  ⚠ Could not create group (may already exist)"
    fi
fi

if ! getent passwd 59999 > /dev/null 2>&1; then
    echo "Creating user with UID 59999..."
    if command -v useradd > /dev/null 2>&1; then
        sudo useradd -u 59999 -g 59999 -r -s /bin/false valhalla || echo "  ⚠ Could not create user (may already exist)"
    fi
fi

# Fix permissions on local directories
directories=("config" "scripts" "or-tools")

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "Setting permissions on $dir..."
        if sudo chown -R 59999:59999 "$dir" 2>/dev/null; then
            echo "  ✓ Permissions set for $dir"
        else
            echo "  ⚠ Could not set permissions on $dir (may require sudo)"
        fi
    else
        echo "  ℹ Directory $dir does not exist (optional)"
    fi
done

echo ""
echo "✓ Permission configuration complete!"
echo ""

echo "Note: On Linux/Mac:"
echo "  - Valhalla container runs as UID 59999:GID 59999"
echo "  - Make sure volume mounts have appropriate permissions"
echo "  - If using bind mounts, ensure directories are accessible"
echo ""

echo "After starting the container, if you see permission errors:"
echo "  1. Check volume mount paths exist and are accessible"
echo "  2. Verify permissions: ls -la <volume_path>"
echo "  3. Check container logs: docker compose logs valhalla"
echo ""

echo "To verify Valhalla is running correctly:"
echo "  docker compose ps"
echo "  curl http://localhost:8002/status"
echo ""
