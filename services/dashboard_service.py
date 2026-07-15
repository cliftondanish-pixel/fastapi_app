from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.user import User
from models.tenant import Tenant

def get_individual_dashboard(current_user: User):

    if current_user.account_type != "Individual":
        raise HTTPException(
            status_code=403,
            detail="Only individual users can access this dashboard"
        )

    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "account_type": current_user.account_type,
        "is_active": current_user.is_active
    }
    
def get_organization_dashboard(
    db: Session,
    current_user: User
):

    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization users can access this dashboard"
        )

    tenant = (
        db.query(Tenant)
        .filter(
            Tenant.id == current_user.tenant_id
        )
        .first()
    )

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    total_users = (
        db.query(User)
        .filter(User.tenant_id == tenant.id)
        .count()
    )

    active_users = (
        db.query(User)
        .filter(
            User.tenant_id == tenant.id,
            User.is_active.is_(True)
        )
        .count()
    )

    inactive_users = (
        db.query(User)
        .filter(
            User.tenant_id == tenant.id,
            User.is_active.is_(False)
        )
        .count()
    )

    return {
        "organization_name": tenant.organization_name,
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "status": tenant.status
    }