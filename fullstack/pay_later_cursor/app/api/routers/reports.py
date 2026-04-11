"""
Reports API router for LazyPay application.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse

from app.modules.reports.service import ReportService
from app.modules.reports.schemas import (
    FeeCollectionResponse,
    UserDuesResponse,
    UsersAtCreditLimitResponse,
    TotalDuesResponse,
    ReportErrorResponse
)
from app.api.dependencies import get_report_service
from app.auth.dependencies import get_current_active_user
from app.auth.models import UserAuth
from app.rbac.middleware import (
    require_reports_read, require_reports_export, require_admin_role
)
from app.common.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/fee/{merchant_name}",
    response_model=FeeCollectionResponse,
    summary="Get fee collection report for a merchant",
    description="Retrieve the total fee collected for a specific merchant",
    responses={
        200: {
            "description": "Fee collection report retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "fee_collected": 10.5,
                        "total_transactions": 5,
                        "period_start": "2025-08-01T00:00:00",
                        "period_end": "2025-08-31T23:59:59"
                    }
                }
            }
        },
        404: {
            "description": "Merchant not found",
            "model": ReportErrorResponse
        },
        422: {
            "description": "Validation error",
            "model": ReportErrorResponse
        }
    }
)
async def get_fee_collection_report(
    merchant_name: str,
    start_date: Optional[datetime] = Query(None, description="Report start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Report end date (ISO format)"),
    current_user: UserAuth = Depends(require_reports_read),
    report_service: ReportService = Depends(get_report_service)
) -> FeeCollectionResponse:
    """
    Get fee collection report for a specific merchant.
    Requires reports:read permission.
    
    - **merchant_name**: Name of the merchant
    - **start_date**: Optional start date for the report period
    - **end_date**: Optional end date for the report period
    
    Returns the total fee collected and number of transactions for the merchant.
    """
    try:
        return await report_service.get_fee_collection_report(
            merchant_name=merchant_name,
            start_date=start_date,
            end_date=end_date
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/dues/{user_name}",
    response_model=UserDuesResponse,
    summary="Get dues report for a user",
    description="Retrieve the outstanding dues for a specific user",
    responses={
        200: {
            "description": "User dues report retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "dues": 200.0,
                        "total_purchases": 500.0,
                        "total_payments": 300.0,
                        "credit_limit": 1000.0,
                        "available_credit": 800.0
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "model": ReportErrorResponse
        },
        422: {
            "description": "Validation error",
            "model": ReportErrorResponse
        }
    }
)
async def get_user_dues_report(
    user_name: str,
    include_details: bool = Query(False, description="Include detailed breakdown"),
    current_user: UserAuth = Depends(require_reports_read),
    report_service: ReportService = Depends(get_report_service)
) -> UserDuesResponse:
    """
    Get dues report for a specific user.
    
    - **user_name**: Name of the user
    - **include_details**: Whether to include detailed breakdown (purchases, payments, credit info)
    
    Returns the outstanding dues for the user.
    """
    try:
        return await report_service.get_user_dues_report(
            user_name=user_name,
            include_details=include_details
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/users-at-credit-limit",
    response_model=UsersAtCreditLimitResponse,
    summary="Get users at credit limit",
    description="Retrieve list of users who have reached their credit limit",
    responses={
        200: {
            "description": "Users at credit limit report retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "users": ["user1", "user3"],
                        "total_count": 2
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": ReportErrorResponse
        }
    }
)
async def get_users_at_credit_limit_report(
    current_user: UserAuth = Depends(require_admin_role),
    report_service: ReportService = Depends(get_report_service)
) -> UsersAtCreditLimitResponse:
    """
    Get report of users who have reached their credit limit.
    
    Returns a list of usernames who have outstanding dues equal to or exceeding their credit limit.
    """
    try:
        return await report_service.get_users_at_credit_limit_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/total-dues",
    response_model=TotalDuesResponse,
    summary="Get total dues report",
    description="Retrieve total outstanding dues across all users",
    responses={
        200: {
            "description": "Total dues report retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total": 400.0,
                        "details": {
                            "user1": 300.0,
                            "user3": 100.0
                        },
                        "total_users_with_dues": 2
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "model": ReportErrorResponse
        }
    }
)
async def get_total_dues_report(
    include_inactive_users: bool = Query(False, description="Include inactive users in the report"),
    current_user: UserAuth = Depends(require_admin_role),
    report_service: ReportService = Depends(get_report_service)
) -> TotalDuesResponse:
    """
    Get total dues report across all users.
    
    - **include_inactive_users**: Whether to include inactive users in the calculation
    
    Returns the total outstanding dues and breakdown by user.
    """
    try:
        return await report_service.get_total_dues_report(
            include_inactive_users=include_inactive_users
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/available-merchants",
    summary="Get available merchant names",
    description="Retrieve list of all available merchant names for reports",
    responses={
        200: {
            "description": "Available merchants retrieved successfully",
            "content": {
                "application/json": {
                    "example": ["Merchant A", "Merchant B", "Merchant C"]
                }
            }
        }
    }
)
async def get_available_merchants(
    report_service: ReportService = Depends(get_report_service)
):
    """
    Get list of available merchant names for reports.
    
    Returns a list of all merchant names that can be used in fee collection reports.
    """
    try:
        merchants = await report_service.get_available_merchants()
        return merchants
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/available-users",
    summary="Get available user names",
    description="Retrieve list of all available user names for reports",
    responses={
        200: {
            "description": "Available users retrieved successfully",
            "content": {
                "application/json": {
                    "example": ["user1", "user2", "user3"]
                }
            }
        }
    }
)
async def get_available_users(
    report_service: ReportService = Depends(get_report_service)
):
    """
    Get list of available user names for reports.
    
    Returns a list of all user names that can be used in dues reports.
    """
    try:
        users = await report_service.get_available_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
