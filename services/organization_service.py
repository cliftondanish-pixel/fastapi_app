from fastapi import HTTPException
from pytest import Session
from models.tenant import Tenant
from models.user import User
from schemas.organization import UpdateOrganizationProfileRequest

def get_organization_profile(
    db: Session,
    current_user: User
):

    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization users can access organization profile"
        )

    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
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

    return tenant

def update_organization_profile(
    db: Session,
    current_user: User,
    request: UpdateOrganizationProfileRequest
):

    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization users can update organization profile"
        )

    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == current_user.tenant_id)
        .first()
    )

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    if current_user.role != "Tenant Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Tenant Admin can update organization profile"
        )

    tenant.organization_name = request.organization_name

    db.commit()
    db.refresh(tenant)

    return {
        "message": "Organization profile updated successfully"
    }