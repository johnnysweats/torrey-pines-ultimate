#!/bin/bash

echo "🚀 Deploying Torrey Pines Waitlist to Railway"
echo "=============================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

# Initialize Railway project if not already done
if [ ! -f ".railway/project.json" ]; then
    echo "📁 Initializing Railway project..."
    railway init
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment complete!"
echo "📱 Your app will be available at the URL shown above"
echo "🌐 You can access it from your phone to run the waitlist automation"
echo ""
echo "📋 Next steps:"
echo "1. Open the URL on your phone"
echo "2. Fill in your information or use 'Fill John's Info'"
echo "3. Select course and players"
echo "4. Set target time and start automation"
echo ""
