"""
Report repository for LazyPay application.
"""

from datetime import datetime
from typing import Optional, Dict, List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from bson import ObjectId

from app.modules.reports.models import (
    FeeCollectionReport,
    UserDuesReport,
    UsersAtCreditLimitReport,
    TotalDuesReport,
    ReportFilter
)


class ReportRepository:
    """Repository for report-related database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def get_fee_collection_by_merchant_name(
        self,
        merchant_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> FeeCollectionReport:
        """Get fee collection report for a specific merchant."""
        
        # Build aggregation pipeline
        match_conditions = {
            "type": "PURCHASE",
            "status": "APPROVED",
            "fee_amount": {"$exists": True, "$ne": 0}
        }
        
        # Add date filters if provided
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            match_conditions["created_at"] = date_filter

        # First, get merchant ID by name
        merchant = await self.database.merchants.find_one(
            {"name": merchant_name},
            session=session
        )
        
        if not merchant:
            raise ValueError(f"Merchant '{merchant_name}' not found")
        
        merchant_id = merchant["_id"]
        match_conditions["merchant_id"] = merchant_id

        # Aggregate fee collection data
        pipeline = [
            {"$match": match_conditions},
            {
                "$group": {
                    "_id": None,
                    "fee_collected": {"$sum": "$fee_amount"},
                    "total_transactions": {"$sum": 1}
                }
            }
        ]

        result = await self.database.transactions.aggregate(
            pipeline, session=session
        ).to_list(1)

        if not result:
            return FeeCollectionReport(
                merchant_name=merchant_name,
                fee_collected=0.0,
                total_transactions=0,
                period_start=start_date,
                period_end=end_date
            )

        data = result[0]
        return FeeCollectionReport(
            merchant_name=merchant_name,
            fee_collected=data["fee_collected"],
            total_transactions=data["total_transactions"],
            period_start=start_date,
            period_end=end_date
        )

    async def get_user_dues_by_name(
        self,
        user_name: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> UserDuesReport:
        """Get dues report for a specific user."""
        
        # Get user by name
        user = await self.database.users.find_one(
            {"name": user_name},
            session=session
        )
        
        if not user:
            raise ValueError(f"User '{user_name}' not found")
        
        user_id = user["_id"]
        
        # Get user balance
        balance = await self.database.user_balances.find_one(
            {"user_id": user_id},
            session=session
        )
        
        if not balance:
            return UserDuesReport(
                user_name=user_name,
                dues=0.0,
                total_purchases=0.0,
                total_payments=0.0,
                credit_limit=user.get("credit_limit", 0.0),
                available_credit=user.get("credit_limit", 0.0)
            )

        outstanding_amount = balance.get("outstanding_amount", 0.0)
        total_purchases = balance.get("total_purchases", 0.0)
        total_payments = balance.get("total_payments", 0.0)
        credit_limit = user.get("credit_limit", 0.0)
        available_credit = max(0.0, credit_limit - outstanding_amount)

        return UserDuesReport(
            user_name=user_name,
            dues=outstanding_amount,
            total_purchases=total_purchases,
            total_payments=total_payments,
            credit_limit=credit_limit,
            available_credit=available_credit
        )

    async def get_users_at_credit_limit(
        self,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> UsersAtCreditLimitReport:
        """Get list of users who have reached their credit limit."""
        
        # Aggregate users at credit limit
        pipeline = [
            {
                "$lookup": {
                    "from": "user_balances",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "balance"
                }
            },
            {
                "$unwind": {
                    "path": "$balance",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$match": {
                    "status": "ACTIVE",
                    "$expr": {
                        "$gte": [
                            "$balance.outstanding_amount",
                            "$credit_limit"
                        ]
                    }
                }
            },
            {
                "$project": {
                    "name": 1
                }
            }
        ]

        results = await self.database.users.aggregate(
            pipeline, session=session
        ).to_list(None)

        user_names = [user["name"] for user in results]
        
        return UsersAtCreditLimitReport(
            users=user_names,
            total_count=len(user_names)
        )

    async def get_total_dues(
        self,
        include_inactive_users: bool = False,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> TotalDuesReport:
        """Get total dues across all users."""
        
        # Build match conditions
        match_conditions = {}
        if not include_inactive_users:
            match_conditions["status"] = "ACTIVE"

        # Aggregate total dues
        pipeline = [
            {
                "$lookup": {
                    "from": "user_balances",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "balance"
                }
            },
            {
                "$unwind": {
                    "path": "$balance",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$match": {
                    **match_conditions,
                    "$expr": {
                        "$gt": ["$balance.outstanding_amount", 0]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$balance.outstanding_amount"},
                    "total_users": {"$sum": 1},
                    "details": {
                        "$push": {
                            "user_name": "$name",
                            "dues": "$balance.outstanding_amount"
                        }
                    }
                }
            }
        ]

        result = await self.database.users.aggregate(
            pipeline, session=session
        ).to_list(1)

        if not result:
            return TotalDuesReport(
                total=0.0,
                details={},
                total_users_with_dues=0
            )

        data = result[0]
        details = {
            item["user_name"]: item["dues"] 
            for item in data["details"]
        }

        return TotalDuesReport(
            total=data["total"],
            details=details,
            total_users_with_dues=data["total_users"]
        )

    async def get_merchant_names(
        self,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> List[str]:
        """Get list of all merchant names."""
        
        merchants = await self.database.merchants.find(
            {}, {"name": 1}, session=session
        ).to_list(None)
        
        return [merchant["name"] for merchant in merchants]

    async def get_user_names(
        self,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> List[str]:
        """Get list of all user names."""
        
        users = await self.database.users.find(
            {}, {"name": 1}, session=session
        ).to_list(None)
        
        return [user["name"] for user in users]
