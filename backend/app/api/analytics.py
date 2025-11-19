"""Analytics endpoints for tracking engagement and platform metrics."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.models import (
    Resource,
    ResourceAnalytics,
    ResourceAnalyticsResponse,
    User,
    UserRole,
)
from app.services.database import get_session

router = APIRouter(prefix="/api/v1", tags=["analytics"])


def get_or_create_analytics(
    resource_id: UUID,
    session: Session,
) -> ResourceAnalytics:
    """Get or create analytics record for a resource.

    Args:
        resource_id: Resource ID
        session: Database session

    Returns:
        Analytics record
    """
    analytics = session.exec(
        select(ResourceAnalytics).where(ResourceAnalytics.resource_id == resource_id)
    ).first()

    if not analytics:
        analytics = ResourceAnalytics(resource_id=resource_id)
        session.add(analytics)
        session.commit()
        session.refresh(analytics)

    return analytics


# Resource Analytics Endpoints


@router.post("/resources/{resource_id}/view", response_model=dict, status_code=status.HTTP_200_OK)
def track_resource_view(
    resource_id: UUID,
    session: Session = Depends(get_session),
) -> dict:
    """Track a view of a resource.

    Args:
        resource_id: Resource ID being viewed
        session: Database session

    Returns:
        Updated view count

    Raises:
        HTTPException: If resource not found
    """
    # Verify resource exists
    resource = session.exec(select(Resource).where(Resource.id == resource_id)).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Get or create analytics
    analytics = get_or_create_analytics(resource_id, session)

    # Increment view count
    analytics.view_count += 1
    from datetime import UTC, datetime
    analytics.last_viewed = datetime.now(UTC)

    session.add(analytics)
    session.commit()
    session.refresh(analytics)

    return {
        "resource_id": str(resource_id),
        "view_count": analytics.view_count,
        "status": "tracked",
    }


@router.post("/resources/{resource_id}/tried", response_model=dict)
def track_resource_tried(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Mark that a user tried implementing a resource.

    Args:
        resource_id: Resource ID being tried
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated tried count

    Raises:
        HTTPException: If resource not found
    """
    # Verify resource exists
    resource = session.exec(select(Resource).where(Resource.id == resource_id)).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Get or create analytics
    analytics = get_or_create_analytics(resource_id, session)

    # Increment tried count
    analytics.tried_count += 1

    session.add(analytics)
    session.commit()
    session.refresh(analytics)

    return {
        "resource_id": str(resource_id),
        "tried_count": analytics.tried_count,
        "status": "tracked",
    }


@router.post("/resources/{resource_id}/save", response_model=dict)
def track_resource_save(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Mark that a user saved/bookmarked a resource.

    Args:
        resource_id: Resource ID being saved
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated save count

    Raises:
        HTTPException: If resource not found
    """
    # Verify resource exists
    resource = session.exec(select(Resource).where(Resource.id == resource_id)).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Get or create analytics
    analytics = get_or_create_analytics(resource_id, session)

    # Increment save count
    analytics.save_count += 1

    session.add(analytics)
    session.commit()
    session.refresh(analytics)

    return {
        "resource_id": str(resource_id),
        "save_count": analytics.save_count,
        "status": "tracked",
    }


@router.get("/resources/{resource_id}/analytics", response_model=ResourceAnalyticsResponse)
def get_resource_analytics(
    resource_id: UUID,
    current_user: User | None = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ResourceAnalyticsResponse:
    """Get analytics for a resource (author can see all details).

    Args:
        resource_id: Resource ID
        current_user: Current user (for authorization)
        session: Database session

    Returns:
        Analytics data

    Raises:
        HTTPException: If resource not found
    """
    # Verify resource exists
    resource = session.exec(select(Resource).where(Resource.id == resource_id)).first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    # Get or create analytics
    analytics = get_or_create_analytics(resource_id, session)

    return analytics


# Platform Analytics Endpoints


@router.get("/admin/analytics", response_model=dict)
def get_platform_analytics(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Get platform-wide analytics (admin only).

    Args:
        current_user: Current authenticated user (must be admin)
        session: Database session

    Returns:
        Platform analytics

    Raises:
        HTTPException: If not authorized
    """
    # Check admin access
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view platform analytics",
        )

    # Get all analytics
    all_analytics = session.exec(select(ResourceAnalytics)).all()
    resources = session.exec(select(Resource)).all()

    # Calculate metrics
    total_views = sum(a.view_count for a in all_analytics)
    total_saves = sum(a.save_count for a in all_analytics)
    total_tried = sum(a.tried_count for a in all_analytics)
    total_forks = sum(a.fork_count for a in all_analytics)
    total_comments = sum(a.comment_count for a in all_analytics)

    # Find top resources
    top_viewed = sorted(all_analytics, key=lambda a: a.view_count, reverse=True)[:5]

    return {
        "platform_stats": {
            "total_resources": len(resources),
            "total_views": total_views,
            "total_saves": total_saves,
            "total_tried": total_tried,
            "total_forks": total_forks,
            "total_comments": total_comments,
            "avg_views_per_resource": total_views / len(resources) if resources else 0,
            "avg_saves_per_resource": total_saves / len(resources) if resources else 0,
        },
        "top_resources": [
            {
                "resource_id": str(a.resource_id),
                "view_count": a.view_count,
                "save_count": a.save_count,
                "tried_count": a.tried_count,
            }
            for a in top_viewed
        ],
    }


@router.get("/admin/analytics/by-discipline", response_model=dict)
def get_analytics_by_discipline(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Get analytics broken down by discipline (admin only).

    Args:
        current_user: Current authenticated user (must be admin)
        session: Database session

    Returns:
        Analytics by discipline

    Raises:
        HTTPException: If not authorized
    """
    # Check admin access
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view analytics",
        )

    # Get all resources grouped by discipline
    resources = session.exec(select(Resource)).all()

    discipline_stats: dict = {}
    for resource in resources:
        if resource.discipline:
            if resource.discipline not in discipline_stats:
                discipline_stats[resource.discipline] = {
                    "count": 0,
                    "total_views": 0,
                    "total_saves": 0,
                }

            discipline_stats[resource.discipline]["count"] += 1

            # Get analytics
            analytics = session.exec(
                select(ResourceAnalytics).where(ResourceAnalytics.resource_id == resource.id)
            ).first()
            if analytics:
                discipline_stats[resource.discipline]["total_views"] += analytics.view_count
                discipline_stats[resource.discipline]["total_saves"] += analytics.save_count

    return {"by_discipline": discipline_stats}
