# Setup Guide: OpenAI + Supabase Configuration

This guide will help you set up the AI Chatbot Framework with OpenAI APIs and Supabase PostgreSQL database.

## Prerequisites

1. **OpenAI API Account**: Get your API key from [OpenAI Platform](https://platform.openai.com/)
2. **Supabase Account**: Create a project at [Supabase](https://supabase.com/)
3. **Docker & Docker Compose**: Ensure you have Docker installed

## Step 1: Supabase Setup

1. **Create a new Supabase project**
   - Go to [Supabase Dashboard](https://app.supabase.com/)
   - Click "New Project"
   - Choose your organization and set project details

2. **Get Database Connection Details**
   - Go to Settings → Database
   - Copy the connection string and details:
     - Host: `db.[YOUR-PROJECT-REF].supabase.co`
     - Database: `postgres`
     - Port: `5432`
     - User: `postgres`
     - Password: [Your database password]

3. **Enable Row Level Security (Optional)**
   - For production, consider enabling RLS on your tables
   - This adds an extra layer of security

## Step 2: Environment Configuration

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` file with your credentials**:
   ```env
   # Supabase PostgreSQL Configuration
   SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   SUPABASE_HOST=db.[YOUR-PROJECT-REF].supabase.co
   SUPABASE_PORT=5432
   SUPABASE_DATABASE=postgres
   SUPABASE_USER=postgres
   SUPABASE_PASSWORD=[YOUR-PASSWORD]

   # OpenAI Configuration
   OPENAI_API_KEY=sk-[YOUR-OPENAI-API-KEY]
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_TEMPERATURE=0.7
   OPENAI_MAX_TOKENS=4096

   # Application Configuration
   APPLICATION_ENV=Development
   USE_LLM_NLU=true
   USE_ZERO_SHOT_NLU=true

   # Frontend Configuration
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
   ```

## Step 3: Database Migration

1. **Run the PostgreSQL migration script**:
   ```bash
   python migrate_postgres.py
   ```

   This will:
   - Create all necessary tables in your Supabase database
   - Insert default bot configuration
   - Set up default intents and integrations

## Step 4: Start the Application

1. **Build and start with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.openai.yml up --build
   ```

2. **Access the application**:
   - Backend API: http://localhost:8080
   - Frontend Admin: http://localhost:3000
   - API Documentation: http://localhost:8080/docs

## Step 5: Verify Setup

1. **Test the REST API endpoint**:
   ```bash
   curl -X POST "http://localhost:8080/bots/channels/rest/webbook" \
        -H "Content-Type: application/json" \
        -d '{
          "thread_id": "test-123",
          "text": "Hello",
          "context": {}
        }'
   ```

2. **Check the admin interface**:
   - Go to http://localhost:3000
   - Navigate to different sections (Bots, Intents, Entities)
   - Verify data is loading from Supabase

## Step 6: React Widget Integration

1. **Follow the React Widget Integration Guide**:
   - See `docs/06-react-widget-integration.md`
   - Install the provided React components in your app
   - Configure the API URL to point to your chatbot backend

## Configuration Options

### OpenAI Models
You can use different OpenAI models by updating the `OPENAI_MODEL` environment variable:
- `gpt-3.5-turbo` (recommended for cost-effectiveness)
- `gpt-4` (better quality, higher cost)
- `gpt-4-turbo` (latest model)

### Temperature Settings
Adjust the `OPENAI_TEMPERATURE` (0.0 to 1.0):
- `0.0`: More deterministic responses
- `0.7`: Balanced creativity and consistency
- `1.0`: More creative and varied responses

### Database Configuration
The framework automatically detects PostgreSQL when `DATABASE_URL` is set. You can also manually configure individual connection parameters.

## Production Deployment

### Environment Variables for Production
```env
APPLICATION_ENV=Production
OPENAI_API_KEY=[YOUR-PRODUCTION-API-KEY]
SUPABASE_DATABASE_URL=[YOUR-PRODUCTION-DATABASE-URL]
NEXT_PUBLIC_API_BASE_URL=https://your-domain.com/api
```

### Security Considerations
1. **API Keys**: Store sensitive keys in secure environment variables
2. **Database**: Use connection pooling and SSL connections
3. **CORS**: Restrict CORS origins to your specific domains
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Authentication**: Add authentication for admin endpoints

### Scaling
1. **Database**: Supabase automatically handles scaling
2. **API**: Use multiple backend instances behind a load balancer
3. **Caching**: Implement Redis for session and response caching

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify Supabase credentials
   - Check if your IP is allowed (Supabase allows all by default)
   - Ensure the database URL format is correct

2. **OpenAI API Errors**
   - Verify API key is valid and has sufficient credits
   - Check rate limits on your OpenAI account
   - Ensure the model name is correct

3. **CORS Issues**
   - Update CORS settings in the backend
   - Verify the frontend API URL configuration

4. **Migration Errors**
   - Check database permissions
   - Verify the connection string
   - Look at detailed error messages in logs

### Logs and Debugging
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: Check Supabase dashboard

## Support

For additional help:
1. Check the [main documentation](docs/README.md)
2. Review the [GitHub issues](https://github.com/alfredfrancis/ai-chatbot-framework/issues)
3. Join the [Gitter chat](https://gitter.im/ai-chatbot-framework/Lobby)