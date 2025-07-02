# Deploying AI Chatbot Framework on Render

This guide provides step-by-step instructions for deploying the AI Chatbot Framework on Render.

## Prerequisites

1. A Render account (https://render.com)
2. A MongoDB database (you can use MongoDB Atlas free tier)
3. Git repository with the AI Chatbot Framework code

## Step 1: Set Up MongoDB

1. Create a MongoDB database (recommended: MongoDB Atlas free tier)
2. Create a database named `ai-chatbot-framework`
3. Get your MongoDB connection string (it should look like `mongodb+srv://username:password@cluster.mongodb.net/`)

## Step 2: Deploy on Render

### Option 1: Deploy from GitHub

1. Fork the AI Chatbot Framework repository to your GitHub account
2. In Render, go to "New" > "Web Service"
3. Connect your GitHub account and select the forked repository
4. Configure the following settings:
   - **Name**: ai-chatbot-framework (or your preferred name)
   - **Environment**: Python
   - **Build Command**: `./render-setup.sh`
   - **Start Command**: `python run.py`

5. Add the following environment variables:
   - `MONGODB_HOST`: Your MongoDB connection string
   - `MONGODB_DATABASE`: ai-chatbot-framework
   - `APPLICATION_ENV`: Production
   - `PORT`: 10000 (or your preferred port)

6. Click "Create Web Service"

### Option 2: Manual Deployment

1. Download the latest release of AI Chatbot Framework
2. Extract the files
3. In Render, go to "New" > "Web Service"
4. Choose "Upload Files"
5. Upload the extracted files
6. Configure as in Option 1 above

## Step 3: Verify Deployment

1. Once deployed, Render will provide a URL for your application
2. Visit the URL to access the admin panel
3. If you see the admin panel but clicking on links doesn't work, check the following:
   - Verify MongoDB connection in the Render logs
   - Check if the frontend is properly built
   - Ensure environment variables are set correctly

## Troubleshooting

### Database Connection Issues

If you're having trouble connecting to MongoDB:

1. Check the MongoDB connection string in your environment variables
2. Ensure your MongoDB Atlas IP whitelist includes Render's IPs
3. Check the Render logs for any connection errors

### Admin Panel Not Working

If the admin panel loads but clicking on links doesn't work:

1. Check the browser console for any JavaScript errors
2. Verify that the frontend was built correctly during deployment
3. Check the Render logs for any API errors

### Application Crashes on Startup

If the application crashes immediately:

1. Check the Render logs for error messages
2. Verify that all required environment variables are set
3. Make sure your MongoDB connection string is correct

## Health Check

You can run the included health check script to verify your MongoDB connection:

```bash
python health_check.py
```

This will check if your MongoDB connection is working and if any bots exist in the database.

## Creating Your First Bot

After deployment, you'll need to create a bot:

1. Access the admin panel at your Render URL
2. Go to "Bot Management"
3. Create a new bot or import an example bot from the examples folder

## Support

If you continue to experience issues, please open an issue on the GitHub repository with:

1. Your Render logs
2. Any error messages you're seeing
3. Steps you've taken to troubleshoot

## Advanced Configuration

For advanced configuration options, refer to the main README.md file in the repository.