"""
Teams Bot Server
Web server to host the Teams bot endpoint
"""
import os
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from teams_bot import TeamsPRBot
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Bot adapter settings
SETTINGS = BotFrameworkAdapterSettings(
    app_id=os.getenv("TEAMS_APP_ID"),
    app_password=os.getenv("TEAMS_APP_PASSWORD")
)

# Create adapter and bot
ADAPTER = BotFrameworkAdapter(SETTINGS)
BOT = TeamsPRBot()


async def messages(req: Request) -> Response:
    """Handle incoming messages from Teams"""
    
    # Main bot message handler
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    try:
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        if response:
            return Response(body=response.body, status=response.status)
        return Response(status=201)
    except Exception as exception:
        print(f"Error processing activity: {exception}")
        return Response(status=500, text=str(exception))


async def health(req: Request) -> Response:
    """Health check endpoint"""
    return Response(text="PR Creator Bot is running!", status=200)


def init_func(argv):
    """Initialize the web app"""
    app = web.Application()
    app.router.add_post("/api/messages", messages)
    app.router.add_get("/health", health)
    return app


if __name__ == "__main__":
    app = init_func(None)
    
    port = int(os.getenv("PORT", 3978))
    print(f"🚀 Teams Bot server starting on port {port}...")
    print(f"📡 Endpoint: http://localhost:{port}/api/messages")
    
    try:
        web.run_app(app, host="0.0.0.0", port=port)
    except Exception as error:
        raise error
