import os
import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import init_db, get_db
from app.database.seed import seed_database
from app.services.campaign_service import CampaignService
from app.simulator.platform import MockPlatformService
from app.orchestration.state import MessageBus
from app.orchestration.workflow import WorkflowEngine

# Register API Routers
from app.api.campaigns import router as campaigns_router
from app.api.posts import router as posts_router
from app.api.analytics import router as analytics_router
from app.api.agents import router as agents_router
from app.api.platform_api import router as platform_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Social Media AI Company running fully locally on Ollama (gemma3:4b)"
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Mount static & template files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Include API Routers
app.include_router(campaigns_router)
app.include_router(posts_router)
app.include_router(analytics_router)
app.include_router(agents_router)
app.include_router(platform_router)

@app.on_event("startup")
def startup_event():
    init_db()
    try:
        seed_database()
    except Exception as e:
        logger.warning(f"Database seed notice: {e}")

# --- HTML FRONTEND ROUTES ---
@app.get("/")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    campaigns = CampaignService.list_all_campaigns(db)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"active_tab": "dashboard", "campaigns": campaigns}
    )

@app.get("/campaign/{campaign_id}")
def campaign_detail_page(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        campaign = CampaignService.get_campaign_full(db, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return templates.TemplateResponse(
            request=request,
            name="campaign.html",
            context={"active_tab": "dashboard", "campaign": campaign}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign page error for {campaign_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading campaign: {str(e)}")

@app.get("/review/{campaign_id}")
def human_review_page(campaign_id: str, request: Request, db: Session = Depends(get_db)):
    campaign = CampaignService.get_campaign_full(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={"active_tab": "dashboard", "campaign": campaign}
    )

@app.get("/trace")
def trace_page(request: Request, campaign_id: str = None, db: Session = Depends(get_db)):
    campaigns = CampaignService.list_all_campaigns(db)
    selected_id = campaign_id or (campaigns[0].id if campaigns else None)
    traces = MessageBus.get_campaign_traces(db, selected_id) if selected_id else []
    
    return templates.TemplateResponse(
        request=request,
        name="trace.html",
        context={
            "active_tab": "trace",
            "campaigns": campaigns,
            "selected_campaign_id": selected_id,
            "traces": traces
        }
    )

@app.get("/platform")
def platform_page(request: Request, channel: str = None, campaign_id: str = None, db: Session = Depends(get_db)):
    posts = MockPlatformService.get_campaign_platform_posts(db, campaign_id=campaign_id)
    if channel:
        posts = [p for p in posts if p.channel == channel]

    formatted_posts = []
    for p in posts:
        comments = MockPlatformService.get_post_comments(db, p.id)
        formatted_posts.append({
            "id": p.id,
            "campaign_id": p.campaign_id,
            "week_number": p.week_number,
            "channel": p.channel,
            "format": p.format,
            "scheduled_time": p.scheduled_time,
            "hook": p.hook,
            "post_copy": p.post_copy,
            "cta": p.cta,
            "hashtags": p.hashtags,
            "metrics": {
                "impressions": p.impressions,
                "likes": p.likes,
                "comments_count": p.comments_count,
                "shares": p.shares,
                "saves": p.saves,
                "clicks": p.clicks,
                "engagement_rate": p.engagement_rate
            },
            "comments": comments
        })

    return templates.TemplateResponse(
        request=request,
        name="platform.html",
        context={
            "active_tab": "platform",
            "selected_channel": channel,
            "posts": formatted_posts
        }
    )

@app.get("/analytics")
def analytics_page(request: Request, campaign_id: str = None, db: Session = Depends(get_db)):
    campaigns = CampaignService.list_all_campaigns(db)
    selected_campaign = None
    if campaign_id:
        selected_campaign = CampaignService.get_campaign_full(db, campaign_id)
    elif campaigns:
        selected_campaign = campaigns[0]

    comparison = None
    if selected_campaign:
        comparison = WorkflowEngine.compute_week_comparison(db, selected_campaign.id)

    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={
            "active_tab": "analytics",
            "campaigns": campaigns,
            "selected_campaign": selected_campaign,
            "comparison": comparison
        }
    )
