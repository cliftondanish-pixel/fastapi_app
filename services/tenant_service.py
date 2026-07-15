from pytest import Session
from fastapi import HTTPException

from models.tenant import Tenant
from models.user import User
from schemas.tenant import CreateTenantUserRequest, UpdateTenantUserRequest, UpdateUserStatusRequest
from services.password_service import validate_password, hash_password


def create_tenant_user(
    db: Session,
    current_user: User,
    request: CreateTenantUserRequest
):
    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization administrators can create users"
        )
        
    if current_user.role != "Tenant Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Tenant Admin can create organization users"
        )
    
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="Organization not found"
        )
        
    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
        )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
        
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )
        
    validate_password(request.password)
    
    hashed_password = hash_password(request.password)
    
    new_user = User(
    full_name=request.full_name,
    email=request.email,
    password_hash=hashed_password,
    account_type="Organization",
    tenant_id=current_user.tenant_id,
    role="Tenant User",
    is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Organization user created successfully",
        "user_id": new_user.id
    }
    
def get_tenant_users(
    db: Session,
    current_user: User
):
    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization administrators can create users"
        )
    
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="Organization not found"
        )
        
    users = (
        db.query(User)
        .filter(
            User.tenant_id == current_user.tenant_id
        )
        .all()
    )
    
    return users

def get_tenant_user(
    db: Session,
    current_user: User,
    user_id: int
):
    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization administrators can access tenant users"
        )
        
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="Organization not found"
        )
        
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
        .first()
    )
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    return user

def update_tenant_user(
    db: Session,
    current_user: User,
    user_id: int,
    request: UpdateTenantUserRequest
):
    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization users can access this endpoint"
        )

    if current_user.role != "Tenant Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Tenant Admin can update organization users"
        )
    
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="Organization not found"
        )
    
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if request.email != user.email:
        existing = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
    user.full_name = request.full_name
    user.email = request.email

    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully"
    }
    
def update_user_status(
    db: Session,
    current_user: User,
    user_id: int,
    request: UpdateUserStatusRequest
):
    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization users can access this endpoint"
        )

    if current_user.role != "Tenant Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Tenant Admin can change user status"
        )
    
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="Organization not found"
        )
    
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    user.is_active = request.is_active
    
    db.commit()
    db.refresh(user)

    return {
        "message": "User status updated successfully"
    }
    
def delete_tenant_user(
    db: Session,
    current_user: User,
    user_id: int
):
    
    if current_user.account_type != "Organization":
        raise HTTPException(
            status_code=403,
            detail="Only organization users can access this endpoint"
        )

    if current_user.role != "Tenant Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Tenant Admin can delete organization users"
        )
    
    user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tenant_id == current_user.tenant_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Don't allow deleting yourself 
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account"
        )
    
    tenant = (
        db.query(Tenant)
        .filter(Tenant.id == current_user.tenant_id)
        .first()
    )

    if tenant and tenant.owner_user_id == user.id:
        raise HTTPException(
            status_code=400,
            detail="Organization owner cannot be deleted"
        )
    
    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }