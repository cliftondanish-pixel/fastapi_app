from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.dashboard import IndividualDashboardResponse, OrganizationDashboardResponse
from services.dashboard_service import get_individual_dashboard, get_organization_dashboard

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get(
    "/individual",
    response_model=IndividualDashboardResponse
)
def individual_dashboard(
    current_user: User = Depends(get_current_user)
):
    return get_individual_dashboard(current_user)

@router.get(
    "/organization",
    response_model=OrganizationDashboardResponse
)
def organization_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_organization_dashboard(
        db,
        current_user
    )