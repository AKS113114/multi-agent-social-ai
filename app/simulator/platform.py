import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import PlatformPostModel, PlatformCommentModel, PostModel
from app.simulator.engagement import EngagementSimulator
from app.simulator.audience import AudienceSimulator

class MockPlatformService:
    """
    Mock Social Media Platform API and Persistent Storage Manager.
    """

    @staticmethod
    def publish_approved_post(db: Session, post: PostModel) -> PlatformPostModel:
        """
        Publishes an approved post to the mock platform and generates simulated engagement + comments.
        """
        platform_id = f"plat_{uuid.uuid4().hex[:10]}"
        
        # Run simulator engagement calculation
        sim_results = EngagementSimulator.simulate_post_engagement(
            channel=post.channel,
            scheduled_time=post.scheduled_time or "18:00",
            format_type=post.format,
            copy=post.copy,
            cta=post.cta or "",
            hashtags=post.hashtags or [],
            content_pillar=post.content_pillar or "",
            seed=hash(post.id) % 10000
        )

        platform_post = PlatformPostModel(
            id=platform_id,
            campaign_id=post.campaign_id,
            week_number=post.week_number,
            channel=post.channel,
            post_copy=post.copy,
            hook=post.hook,
            cta=post.cta,
            hashtags=post.hashtags,
            format=post.format,
            scheduled_time=post.scheduled_time,
            published_at=datetime.utcnow(),
            impressions=sim_results["impressions"],
            likes=sim_results["likes"],
            comments_count=sim_results["comments_count"],
            shares=sim_results["shares"],
            saves=sim_results["saves"],
            clicks=sim_results["clicks"],
            follower_delta=sim_results["follower_delta"],
            engagement_rate=sim_results["engagement_rate"]
        )

        db.add(platform_post)
        
        # Update post reference
        post.is_published = True
        post.platform_post_id = platform_id

        # Generate audience comments for this platform post
        generated_comments = AudienceSimulator.generate_comments_for_post(
            channel=post.channel,
            copy=post.copy,
            comment_count=sim_results["comments_count"],
            seed=hash(platform_id) % 10000
        )

        for c_data in generated_comments:
            comment_obj = PlatformCommentModel(
                id=f"cmt_{uuid.uuid4().hex[:8]}",
                platform_post_id=platform_id,
                author=c_data["author"],
                content=c_data["content"],
                sentiment=c_data["sentiment"],
                is_sensitive=c_data["is_sensitive"],
                response_status="PENDING"
            )
            db.add(comment_obj)

        db.commit()
        db.refresh(platform_post)
        return platform_post

    @staticmethod
    def get_campaign_platform_posts(db: Session, campaign_id: str, week_number: Optional[int] = None) -> List[PlatformPostModel]:
        query = db.query(PlatformPostModel).filter(PlatformPostModel.campaign_id == campaign_id)
        if week_number is not None:
            query = query.filter(PlatformPostModel.week_number == week_number)
        return query.all()

    @staticmethod
    def get_post_comments(db: Session, platform_post_id: str) -> List[PlatformCommentModel]:
        return db.query(PlatformCommentModel).filter(PlatformCommentModel.platform_post_id == platform_post_id).all()

    @staticmethod
    def get_campaign_analytics_summary(db: Session, campaign_id: str, week_number: int) -> Dict[str, Any]:
        posts = MockPlatformService.get_campaign_platform_posts(db, campaign_id, week_number)
        if not posts:
            return {
                "total_posts": 0,
                "total_impressions": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_saves": 0,
                "total_clicks": 0,
                "total_follower_delta": 0,
                "avg_engagement_rate": 0.0
            }

        total_imp = sum(p.impressions for p in posts)
        total_likes = sum(p.likes for p in posts)
        total_cmts = sum(p.comments_count for p in posts)
        total_shares = sum(p.shares for p in posts)
        total_saves = sum(p.saves for p in posts)
        total_clicks = sum(p.clicks for p in posts)
        total_followers = sum(p.follower_delta for p in posts)
        avg_er = round(sum(p.engagement_rate for p in posts) / len(posts), 2)

        return {
            "total_posts": len(posts),
            "total_impressions": total_imp,
            "total_likes": total_likes,
            "total_comments": total_cmts,
            "total_shares": total_shares,
            "total_saves": total_saves,
            "total_clicks": total_clicks,
            "total_follower_delta": total_followers,
            "avg_engagement_rate": avg_er
        }
