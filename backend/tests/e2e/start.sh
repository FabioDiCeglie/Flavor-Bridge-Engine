#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

PORT=${PORT:-8787}
API_URL="http://localhost:$PORT"
export API_URL

# Check if httpx is installed
if ! python3 -c "import httpx" 2>/dev/null; then
    echo "Installing httpx..."
    pip3 install httpx -q
fi

# Start server in background
echo "🚀 Starting server on port $PORT..."
cd "$BACKEND_DIR"
npx wrangler dev --port $PORT &
SERVER_PID=$!

# Wait for server to be ready
echo -n "Waiting for server"
for i in {1..30}; do
    if curl -s "$API_URL/health" > /dev/null 2>&1; then
        echo " ✓"
        break
    fi
    echo -n "."
    sleep 1
done

# Check if server started
if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo " ✗ Failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Run tests
python3 "$SCRIPT_DIR/test_api.py"
TEST_EXIT=$?

# Stop server
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null

exit $TEST_EXIT
