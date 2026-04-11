from typing import Generator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongo import get_database
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
from app.modules.merchants.repository import MerchantRepository
from app.modules.merchants.service import MerchantService
from app.modules.transactions.repository import TransactionRepository
from app.modules.transactions.service import TransactionService
from app.modules.reports.repository import ReportRepository
from app.modules.reports.service import ReportService
from app.common.idempotency import IdempotencyService
import structlog

# RBAC Dependencies
from app.rbac.repository import RBACRepository
from app.rbac.service import RBACService

logger = structlog.get_logger(__name__)


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    from app.db.mongo import get_database as get_db
    return await get_db()


def get_user_repository(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(database)


def get_merchant_repository(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> MerchantRepository:
    """Get merchant repository instance."""
    return MerchantRepository(database)


def get_transaction_repository(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> TransactionRepository:
    """Get transaction repository instance."""
    return TransactionRepository(database)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    """Get user service instance."""
    return UserService(user_repository)


def get_merchant_service(
    merchant_repository: MerchantRepository = Depends(get_merchant_repository)
) -> MerchantService:
    """Get merchant service instance."""
    return MerchantService(merchant_repository)


def get_transaction_service(
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
    user_service: UserService = Depends(get_user_service),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> TransactionService:
    """Get transaction service instance."""
    return TransactionService(transaction_repository, user_service, merchant_service)


def get_report_repository(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> ReportRepository:
    """Get report repository instance."""
    return ReportRepository(database)


def get_report_service(
    report_repository: ReportRepository = Depends(get_report_repository)
) -> ReportService:
    """Get report service instance."""
    return ReportService(report_repository)





def get_idempotency_service(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> IdempotencyService:
    """Get idempotency service instance."""
    return IdempotencyService(database)
# RBAC Dependencies
def get_rbac_repository() -> RBACRepository:
    """Get RBAC repository instance."""
    from app.db.mongo import get_database
    database = get_database()
    return RBACRepository(database)

def get_rbac_service() -> RBACService:
    """Get RBAC service instance."""
    rbac_repository = get_rbac_repository()
    return RBACService(rbac_repository)

