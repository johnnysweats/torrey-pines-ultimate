# Torrey Pines Waitlist - Railway Deployment

This web application allows you to run the Torrey Pines waitlist automation from your phone via Railway.

## Features

- Mobile-friendly web interface
- Automated waitlist registration
- Real-time status updates
- Quick-fill for John's information
- Background processing

## Deployment to Railway

### Method 1: Using Railway CLI

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Initialize and deploy:
   ```bash
   railway init
   railway up
   ```

### Method 2: Using Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository or upload the files
4. Railway will automatically detect the Python app and deploy it

## Environment Variables

No environment variables are required. The app uses default settings.

## Usage

1. Open the deployed URL on your phone
2. Fill in your information or use "Fill John's Info" button
3. Select course and number of players
4. Enter target time in 24-hour format (e.g., 14:30)
5. Click "Start Automation"
6. Monitor the status in real-time

## Important Notes

- The automation runs in the background
- It will wait until the specified time before attempting to join the waitlist
- The app refreshes the waitlist page until the "Join waitlist" button becomes available
- Chrome runs in headless mode on the server
- The app automatically handles timezone conversion to Pacific Time

## Troubleshooting

- If the deployment fails, check the Railway logs
- Ensure all dependencies are properly installed
- The app requires Chrome/Chromium to be available on the server
- Check that the waitlist website is accessible from the server

## File Structure

```
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Web interface
├── requirements.txt    # Python dependencies
├── railway.json        # Railway configuration
├── Procfile           # Process file for Railway
├── nixpacks.toml      # Nixpacks configuration
└── DEPLOYMENT.md      # This file
```
