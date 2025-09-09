# YFPY Fork Setup Guide

This guide will help you set up your own Yahoo Fantasy Sports API credentials for this YFPY fork.

## Step 1: Create a Yahoo Developer App

1. **Log in to Yahoo**: Go to [Yahoo Developer Network](https://developer.yahoo.com/apps/create/) and log in with your Yahoo account.

2. **Create a New App**: Click "Create App" and fill out the form with these settings:
   - **Application Name**: `yfpy` (or any name you prefer)
   - **Application Type**: Select `Installed Application`
   - **Description**: Optional - describe what your app does
   - **Home Page URL**: Optional - can be your GitHub repo or personal website
   - **Redirect URI(s)**: `https://localhost:8080` (this is required)
   - **API Permissions**: Check `Fantasy Sports` and leave `Read` selected

3. **Get Your Credentials**: After creating the app, you'll see:
   - **Client ID** (this is your `YAHOO_CONSUMER_KEY`)
   - **Client Secret** (this is your `YAHOO_CONSUMER_SECRET`)

## Step 2: Configure Environment Variables

1. **Copy the template**: The `.env.template` file has been copied to `.env` for you.

2. **Edit the .env file**: Replace the placeholder values with your actual credentials:
   ```bash
   # Replace these with your actual values from Step 1
   YAHOO_CONSUMER_KEY=your_actual_client_id_here
   YAHOO_CONSUMER_SECRET=your_actual_client_secret_here
   ```

3. **Optional - Configure Your League**: You can also set your own league and team:
   ```bash
   # Add these lines to your .env file if you want to use your own league
   YAHOO_LEAGUE_ID=your_league_id_here
   YAHOO_TEAM_NAME=your_team_name_here
   ```

## Step 3: Find Your League ID

To find your Yahoo Fantasy League ID:

1. Go to your Yahoo Fantasy league in a web browser
2. Look at the URL - it will be something like: `https://football.fantasysports.yahoo.com/f1/123456/`
3. The number after `/f1/` is your league ID (e.g., `123456`)

## Step 4: Test Your Setup

1. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the quickstart**:
   ```bash
   python quickstart/quickstart.py
   ```

3. **First-time authentication**: The first time you run this, a browser window will open asking you to authorize the app. Click "Allow" and copy the verification code back to the terminal.

## Troubleshooting

- **"Invalid credentials" error**: Double-check your Client ID and Client Secret in the .env file
- **"League not found" error**: Make sure your league ID is correct and you have access to that league
- **Browser doesn't open**: If running in Docker or headless environment, the app will print a URL for you to copy to your browser

## Security Notes

- **Never commit your .env file**: It contains sensitive credentials
- **Keep your credentials private**: Don't share your Client ID and Client Secret
- **The .env file is already in .gitignore**: Your credentials won't be accidentally committed

## Next Steps

Once you have your credentials set up, you can:
- Modify the quickstart.py file to query different data
- Create your own scripts using the YFPY library
- Explore the various API endpoints available

For more detailed documentation, see the [YFPY documentation](https://yfpy.uberfastman.com).
