from fastapi import Depends, APIRouter
from pytest import Session

from core.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.tenant import CreateTenantUserRequest, TenantUserResponse, UpdateTenantUserRequest, UpdateUserStatusRequest
from services.tenant_service import create_tenant_user, delete_tenant_user, get_tenant_user, get_tenant_users, update_tenant_user, update_user_status

router = APIRouter()


@router.post("/create-user")
def create_user(
    request: CreateTenantUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_tenant_user(
        db,
        current_user,
        request
    )
    
@router.get(
    "/users",
    response_model=list[TenantUserResponse]
)
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_tenant_users(
        db,
        current_user
    )
    
@router.get(
    "/users/{user_id}",
    response_model=TenantUserResponse
)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_tenant_user(
        db,
        current_user,
        user_id
    )
    
@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    request: UpdateTenantUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_tenant_user(
        db,
        current_user,
        user_id,
        request
    )
    
@router.patch("/users/{user_id}/status")
def change_status(
    user_id: int,
    request: UpdateUserStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_user_status(
        db,
        current_user,
        user_id,
        request
    )
    
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_tenant_user(
        db,
        current_user,
        user_id
    )