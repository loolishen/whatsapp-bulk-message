#!/bin/bash
#
# Run Migrations in Cloud Shell
# This script connects to Cloud SQL and runs Django migrations
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🗄️  Starting Cloud SQL Proxy and Running Migrations${NC}"
echo ""

# Step 1: Check if Cloud SQL Proxy is already running
if pgrep -f "cloud_sql_proxy" > /dev/null; then
    echo -e "${YELLOW}⚠️  Cloud SQL Proxy is already running. Stopping it first...${NC}"
    pkill -f "cloud_sql_proxy" || true
    sleep 2
fi

# Step 2: Start Cloud SQL Proxy in background
echo -e "${GREEN}🔌 Starting Cloud SQL Proxy...${NC}"
cloud_sql_proxy -instances=whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-db=tcp:5432 > /tmp/cloud_sql_proxy.log 2>&1 &
PROXY_PID=$!

# Wait for proxy to be ready
echo "Waiting for Cloud SQL Proxy to start..."
sleep 5

# Check if proxy is running
if ps -p $PROXY_PID > /dev/null; then
    echo -e "${GREEN}✅ Cloud SQL Proxy is running (PID: $PROXY_PID)${NC}"
else
    echo -e "${RED}❌ Failed to start Cloud SQL Proxy${NC}"
    echo "Check logs: cat /tmp/cloud_sql_proxy.log"
    exit 1
fi

# Step 3: Run migrations
echo ""
echo -e "${GREEN}🚀 Running Django migrations...${NC}"
cd ~/app-full

python manage.py migrate

# Check if migration succeeded
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Migrations completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Migrations failed!${NC}"
    exit 1
fi

# Step 4: Stop Cloud SQL Proxy
echo ""
echo -e "${YELLOW}Stopping Cloud SQL Proxy...${NC}"
kill $PROXY_PID 2>/dev/null || true
sleep 2

echo -e "${GREEN}✅ All done!${NC}"
echo ""
echo "Your conversation flow models are now ready!"
echo "Visit: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/admin/"

