from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import FileResponse
from app.database import client as database_client
from app.dependencies import init_dialogue_manager
import os

from app.admin.bots.routes import router as bots_router
from app.admin.entities.routes import router as entities_router
from app.admin.intents.routes import router as intents_router
from app.admin.train.routes import router as train_router
from app.admin.test.routes import router as test_router
from app.admin.integrations.routes import router as integrations_router
from app.admin.chatlogs.routes import router as chatlogs_router


from app.bot.channels.rest.routes import router as rest_router
from app.bot.channels.facebook.routes import router as facebook_router


@asynccontextmanager
async def lifespan(_):
    await init_dialogue_manager()
    yield
    database_client.close()


app = FastAPI(title="AI Chatbot Framework", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the widget
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Check if frontend build exists and mount it
frontend_build_path = "frontend/.next/standalone"
frontend_static_path = "frontend/.next/static"

if os.path.exists(frontend_build_path):
    # Mount Next.js static files
    if os.path.exists(frontend_static_path):
        app.mount("/_next/static", StaticFiles(directory=frontend_static_path), name="nextjs_static")
    
    # Mount public files
    frontend_public_path = "frontend/public"
    if os.path.exists(frontend_public_path):
        app.mount("/images", StaticFiles(directory=f"{frontend_public_path}/images"), name="public_images")


@app.get("/ready")
async def ready():
    return {"status": "ok"}


@app.get("/health")
async def health():
    """Check application health including database connectivity."""
    from app.dependencies import get_dialogue_manager
    
    health_status = {
        "status": "ok",
        "database": "disconnected",
        "dialogue_manager": "not_initialized"
    }
    
    # Check dialogue manager
    dialogue_manager = await get_dialogue_manager()
    if dialogue_manager is not None:
        health_status["dialogue_manager"] = "initialized"
    
    # Check database connectivity
    try:
        from app.database import client as database_client
        # Try to ping the database
        await database_client.admin.command('ping')
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/api")
async def api_root():
    return {"message": "Welcome to AI Chatbot Framework API"}


# admin apis
admin_router = APIRouter(prefix="/admin")
admin_router.include_router(bots_router)
admin_router.include_router(intents_router)
admin_router.include_router(entities_router)
admin_router.include_router(train_router)
admin_router.include_router(test_router)
admin_router.include_router(integrations_router)
admin_router.include_router(chatlogs_router)


app.include_router(admin_router)

bot_router = APIRouter(prefix="/bots/channels", tags=["channels"])
bot_router.include_router(rest_router, tags=["rest"])
bot_router.include_router(facebook_router, tags=["facebook"])


app.include_router(bot_router)


# Root route - redirect to admin panel
@app.get("/")
async def root():
    """Redirect to admin panel."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/admin-panel", status_code=307)


# Serve a simple admin panel interface
@app.get("/admin-panel")
async def admin_panel():
    """Serve a simple admin panel interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Chatbot Framework - Admin Panel</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }
            .header {
                background: white;
                border-radius: 10px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                text-align: center;
            }
            .header h1 {
                color: #4a5568;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .header p {
                color: #718096;
                font-size: 1.1em;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 10px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.2);
            }
            .card h3 {
                color: #4a5568;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .card p {
                color: #718096;
                margin-bottom: 15px;
                line-height: 1.5;
            }
            .btn {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                transition: background 0.2s;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }
            .btn:hover {
                background: #5a67d8;
            }
            .btn-secondary {
                background: #48bb78;
            }
            .btn-secondary:hover {
                background: #38a169;
            }
            .api-section {
                background: white;
                border-radius: 10px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .api-endpoint {
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
            }
            .method {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #48bb78; color: white; }
            .post { background: #ed8936; color: white; }
            .put { background: #4299e1; color: white; }
            .delete { background: #f56565; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 AI Chatbot Framework</h1>
                <p>Admin Panel & API Management</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>📊 Bot Management</h3>
                    <p>Create, configure, and manage your chatbots. Set up intents, entities, and training data.</p>
                    <a href="/admin/bots" class="btn">Manage Bots</a>
                </div>
                
                <div class="card">
                    <h3>🎯 Intents</h3>
                    <p>Define what your bot can understand. Create intents and add training examples.</p>
                    <a href="/admin/intents" class="btn">Manage Intents</a>
                </div>
                
                <div class="card">
                    <h3>🏷️ Entities</h3>
                    <p>Extract specific information from user messages. Define custom entities and synonyms.</p>
                    <a href="/admin/entities" class="btn">Manage Entities</a>
                </div>
                
                <div class="card">
                    <h3>🚀 Training</h3>
                    <p>Train your bot's machine learning models with your configured data.</p>
                    <a href="/admin/train" class="btn btn-secondary">Train Models</a>
                </div>
                
                <div class="card">
                    <h3>🔧 Integrations</h3>
                    <p>Connect your bot to various channels like Facebook Messenger, web widgets, and more.</p>
                    <a href="/admin/integrations" class="btn">Setup Integrations</a>
                </div>
                
                <div class="card">
                    <h3>💬 Chat Logs</h3>
                    <p>Monitor conversations and analyze bot performance with detailed chat logs.</p>
                    <a href="/admin/chatlogs" class="btn">View Logs</a>
                </div>
            </div>
            
            <div class="api-section">
                <h3>🔌 API Endpoints</h3>
                <p>Use these endpoints to interact with your chatbot programmatically:</p>
                
                <div class="api-endpoint">
                    <span class="method post">POST</span>
                    <strong>/bots/channels/rest/webhook</strong> - Send messages to your bot
                </div>
                
                <div class="api-endpoint">
                    <span class="method get">GET</span>
                    <strong>/admin/bots</strong> - List all bots
                </div>
                
                <div class="api-endpoint">
                    <span class="method get">GET</span>
                    <strong>/admin/intents</strong> - List all intents
                </div>
                
                <div class="api-endpoint">
                    <span class="method get">GET</span>
                    <strong>/admin/entities</strong> - List all entities
                </div>
                
                <div class="api-endpoint">
                    <span class="method post">POST</span>
                    <strong>/admin/train</strong> - Train the bot models
                </div>
                
                <p style="margin-top: 20px;">
                    <a href="/docs" class="btn">📖 View Full API Documentation</a>
                    <a href="/api" class="btn btn-secondary">🔍 Test API</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)
