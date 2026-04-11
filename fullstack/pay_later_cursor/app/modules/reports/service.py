"""
Report service for LazyPay application.
"""

import structlog
from datetime import datetime
from typing import Optional, Dict, List

from app.modules.reports.repository import ReportRepository
from app.modules.reports.models import (
    FeeCollectionReport,
    UserDuesReport,
    UsersAtCreditLimitReport,
    TotalDuesReport
)
from app.modules.reports.schemas import (
    FeeCollectionResponse,
    UserDuesResponse,
    UsersAtCreditLimitResponse,
    TotalDuesResponse
)
from app.common.exceptions import NotFoundError, ValidationError


logger = structlog.get_logger(__name__)


class ReportService:
    """Service for report-related business logic."""

    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository

    async def get_fee_collection_report(
        self,
        merchant_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> FeeCollectionResponse:
        """Get fee collection report for a merchant."""
        
        logger.info(
            "Generating fee collection report",
            merchant_name=merchant_name,
            start_date=start_date,
            end_date=end_date
        )

        try:
            # Validate merchant name
            if not merchant_name or not merchant_name.strip():
                raise ValidationError("Merchant name is required")

            # Validate date range if provided
            if start_date and end_date and start_date > end_date:
                raise ValidationError("Start date cannot be after end date")

            # Get report from repository
            report = await self.report_repository.get_fee_collection_by_merchant_name(
                merchant_name=merchant_name,
                start_date=start_date,
                end_date=end_date
            )

            logger.info(
                "Fee collection report generated successfully",
                merchant_name=merchant_name,
                fee_collected=report.fee_collected,
                total_transactions=report.total_transactions
            )

            return FeeCollectionResponse(
                fee_collected=report.fee_collected,
                total_transactions=report.total_transactions,
                period_start=report.period_start,
                period_end=report.period_end
            )

        except ValueError as e:
            logger.error(
                "Merchant not found for fee collection report",
                merchant_name=merchant_name,
                error=str(e)
            )
            raise NotFoundError(f"Merchant '{merchant_name}' not found")
        except Exception as e:
            logger.error(
                "Error generating fee collection report",
                merchant_name=merchant_name,
                error=str(e)
            )
            raise

    async def get_user_dues_report(
        self,
        user_name: str,
        include_details: bool = False
    ) -> UserDuesResponse:
        """Get dues report for a user."""
        
        logger.info(
            "Generating user dues report",
            user_name=user_name,
            include_details=include_details
        )

        try:
            # Validate user name
            if not user_name or not user_name.strip():
                raise ValidationError("User name is required")

            # Get report from repository
            report = await self.report_repository.get_user_dues_by_name(
                user_name=user_name
            )

            logger.info(
                "User dues report generated successfully",
                user_name=user_name,
                dues=report.dues
            )

            response = UserDuesResponse(dues=report.dues)
            
            # Include additional details if requested
            if include_details:
                response.total_purchases = report.total_purchases
                response.total_payments = report.total_payments
                response.credit_limit = report.credit_limit
                response.available_credit = report.available_credit

            return response

        except ValueError as e:
            logger.error(
                "User not found for dues report",
                user_name=user_name,
                error=str(e)
            )
            raise NotFoundError(f"User '{user_name}' not found")
        except Exception as e:
            logger.error(
                "Error generating user dues report",
                user_name=user_name,
                error=str(e)
            )
            raise

    async def get_users_at_credit_limit_report(self) -> UsersAtCreditLimitResponse:
        """Get report of users who have reached their credit limit."""
        
        logger.info("Generating users at credit limit report")

        try:
            # Get report from repository
            report = await self.report_repository.get_users_at_credit_limit()

            logger.info(
                "Users at credit limit report generated successfully",
                total_count=report.total_count
            )

            return UsersAtCreditLimitResponse(
                users=report.users,
                total_count=report.total_count
            )

        except Exception as e:
            logger.error(
                "Error generating users at credit limit report",
                error=str(e)
            )
            raise

    async def get_total_dues_report(
        self,
        include_inactive_users: bool = False
    ) -> TotalDuesResponse:
        """Get total dues report across all users."""
        
        logger.info(
            "Generating total dues report",
            include_inactive_users=include_inactive_users
        )

        try:
            # Get report from repository
            report = await self.report_repository.get_total_dues(
                include_inactive_users=include_inactive_users
            )

            logger.info(
                "Total dues report generated successfully",
                total=report.total,
                total_users_with_dues=report.total_users_with_dues
            )

            return TotalDuesResponse(
                total=report.total,
                details=report.details,
                total_users_with_dues=report.total_users_with_dues
            )

        except Exception as e:
            logger.error(
                "Error generating total dues report",
                error=str(e)
            )
            raise

    async def get_available_merchants(self) -> List[str]:
        """Get list of available merchant names for reports."""
        
        logger.info("Getting available merchant names")

        try:
            merchants = await self.report_repository.get_merchant_names()
            
            logger.info(
                "Available merchants retrieved successfully",
                count=len(merchants)
            )
            
            return merchants

        except Exception as e:
            logger.error(
                "Error getting available merchants",
                error=str(e)
            )
            raise

    async def get_available_users(self) -> List[str]:
        """Get list of available user names for reports."""
        
        logger.info("Getting available user names")

        try:
            users = await self.report_repository.get_user_names()
            
            logger.info(
                "Available users retrieved successfully",
                count=len(users)
            )
            
            return users

        except Exception as e:
            logger.error(
                "Error getting available users",
                error=str(e)
            )
            raise
