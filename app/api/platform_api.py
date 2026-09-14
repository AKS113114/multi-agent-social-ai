from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import PlatformPostModel, PlatformCommentModel
from app.simulator.platform import MockPlatformService

router = APIRouter(prefix="/api/platform", tags=["Mock Platform"])

class AddCommentRequest(BaseModel):
    author: str
    content: str

@router.get("/feed")
def get_platform_feed(channel: Optional[str] = None, campaign_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PlatformPostModel)
    if channel:
        query = query.filter(PlatformPostModel.channel == channel)
    if campaign_id:
        query = query.filter(PlatformPostModel.campaign_id == campaign_id)
    
    posts = query.order_by(PlatformPostModel.published_at.desc()).all()
    return [
        {
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
            "published_at": p.published_at.isoformat() if p.published_at else None,
            "metrics": {
                "impressions": p.impressions,
                "likes": p.likes,
                "comments_count": p.comments_count,
                "shares": p.shares,
                "saves": p.saves,
                "clicks": p.clicks,
                "follower_delta": p.follower_delta,
                "engagement_rate": p.engagement_rate
            }
        } for p in posts
    ]

@router.get("/posts/{post_id}")
def get_platform_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(PlatformPostModel).filter(PlatformPostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Platform post not found")
    return post

@router.get("/posts/{post_id}/comments")
def get_post_comments(post_id: str, db: Session = Depends(get_db)):
    comments = MockPlatformService.get_post_comments(db, post_id)
    return [
        {
            "id": c.id,
            "author": c.author,
            "content": c.content,
            "sentiment": c.sentiment,
            "is_sensitive": c.is_sensitive,
            "community_response": c.community_response,
            "response_status": c.response_status,
            "created_at": c.created_at.isoformat() if c.created_at else None
        } for c in comments
    ]
