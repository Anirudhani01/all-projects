# main.py
# To run this application:
# 1. Make sure you have Python installed.
# 2. Install the required libraries:
#    pip install "fastapi[all]" uvicorn sqlalchemy sqlmodel pymysql "python-jose[cryptography]" bcrypt
# 3. Make sure you have a MySQL server running.
# 4. Create a database named 'pay_later_db'.
# 5. Update the DATABASE_URL with your MySQL credentials.
# 6. Run the application from your terminal:
#    uvicorn main2:app --reload

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import List, Optional
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
# for password hashing
import bcrypt
# for JWT token creation and validation
from jose import JWTError, jwt

# --- Rate limiting imports ---
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
import redis, json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


# --- 1. Security and Configuration ---


# logger.info("FastAPI Pay-Later application started.")
# logger.error("Database connection failed", exc_info=True)


# --- Login Log Setup ---
LOGIN_LOG_FILE = "paylater_app.log"

app_logger = logging.getLogger("paylater_app")
app_logger.setLevel(logging.INFO)

handler = RotatingFileHandler("paylater_app.log", maxBytes=2*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

if not app_logger.handlers:
    app_logger.addHandler(handler)


# --- 2. Database Setup ---
DATABASE_URL = "mysql+pymysql://anirudh:password123@localhost/paylater_db2"
# Replace 'user' and 'password' with your MySQL username and password.

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- 3. Database Models (with password field) ---

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field()
    credit_limit: float
    dues: float = Field(default=0.0)

class Merchant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    fee_percentage: float = Field(default=0.0)
    total_fees_collected: float = Field(default=0.0)

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    merchant_id: int = Field(foreign_key="merchant.id")
    amount: float
    fee_paid: float

# --- 4. Pydantic Models for API ---

class UserCreate(SQLModel):
    name: str
    email: str
    password: str
    credit_limit: float

# New model for JSON-based login
class UserLogin(SQLModel):
    email: str
    password: str

class MerchantCreate(SQLModel):
    name: str
    fee_percentage: float

class TransactionCreate(SQLModel):
    merchant_name: str
    amount: float

class MerchantUpdate(SQLModel):
    name: str
    new_fee_percentage: float

class Payback(SQLModel):
    amount: float

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None


# --- 5. Security Helper Functions (Using bcrypt) ---

# Custom Header for API Key (replaces "Bearer")
api_key_header = APIKeyHeader(name="X-Access-Token", auto_error=False)


def verify_password(plain_password, hashed_password):
    """Compares a plain password with a hashed one using bcrypt."""
    password_byte = plain_password.encode('utf-8')
    hashed_password_byte = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte, hashed_password_byte)

def get_password_hash(password):
    """Hashes a password using bcrypt."""
    password_byte = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_byte, salt)
    return hashed_password.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(api_key_header), session: Session = Depends(get_session)):
    """Dependency to get the current user from a token."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "X-Access-Token"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "X-Access-Token"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == token_data.email)).first()
    if user is None:
        raise credentials_exception
    return user


# --- 6. FastAPI Application ---
app = FastAPI(
    title="Pay-Later Service API with JWT Auth (JSON Login)",
    description="A secured backend service for a simple pay-later application.",
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- 1. Application-level rate limiting with SlowAPI ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})

# --- 2. Middleware-level global rate limiting ---
request_history = defaultdict(list)
class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        ip = request.client.host
        now = time.time()
        window = 60
        max_requests = 100
        request_history[ip] = [t for t in request_history[ip] if now - t < window]
        if len(request_history[ip]) >= max_requests:
            return JSONResponse(status_code=429, content={"detail": "Global rate limit exceeded."})
        request_history[ip].append(now)
        return await call_next(request)

app.add_middleware(GlobalRateLimitMiddleware)


# --- 7. API Endpoints (Public and Protected) ---

# Public endpoint to get a token (login), now using a JSON body
@app.post("/token(login)", response_model=Token, summary="Login to get access token")
@limiter.limit("5/minute")
def login_for_access_token(login_data: UserLogin,request: Request, session: Session = Depends(get_session)):
    """
    Takes a JSON body with email and password, returns an access token.
    """
    client_ip = request.client.host
    user = session.exec(select(User).where(User.email == login_data.email)).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        app_logger.warning(f"Failed login attempt for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "X-Access-Token"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    app_logger.info(f"SUCCESSFUL LOGIN | Email: {user.email} | IP: {client_ip}")
    return {"access_token": access_token, "token_type": f"{User.name}-access-token"}



@app.post("/users(sign-up)", response_model=User, summary="Onboard a new user (Signup)")
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Creates a new user with a name, email, password, and a credit limit.
    The password will be hashed using bcrypt before storing.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        credit_limit=user.credit_limit
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# --- Protected Endpoints ---

@app.post("/merchants", response_model=Merchant, summary="Onboard a new merchant")
def create_merchant(merchant: MerchantCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_merchant = Merchant.from_orm(merchant)
    session.add(db_merchant)
    session.commit()
    session.refresh(db_merchant)
    return db_merchant

@app.put("/merchants/fee", response_model=Merchant, summary="Update a merchant's fee")
def update_merchant_fee(merchant_update: MerchantUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    merchant = session.exec(select(Merchant).where(Merchant.name == merchant_update.name)).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    merchant.fee_percentage = merchant_update.new_fee_percentage
    session.add(merchant)
    session.commit()
    session.refresh(merchant)
    return merchant

@app.post("/transactions", summary="Process a new transaction")
@limiter.limit("5/minute")
def create_transaction(request: Request, transaction: TransactionCreate,
                       session: Session = Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    # --- Merchant caching ---
    merchant_key = f"merchant:{transaction.merchant_name}"
    merchant_data = r.get(merchant_key)

    if merchant_data:
        merchant_info = json.loads(merchant_data)
        merchant_id = merchant_info['id']
        fee_percentage = merchant_info['fee_percentage']
    else:
        merchant = session.exec(select(Merchant).where(Merchant.name == transaction.merchant_name)).first()
        if not merchant:
            raise HTTPException(status_code=404, detail=f"Merchant '{transaction.merchant_name}' not found")
        merchant_id = merchant.id
        fee_percentage = merchant.fee_percentage
        r.setex(merchant_key, 3600, json.dumps({"id": merchant_id, "fee_percentage": fee_percentage}))  # cache for 1h

    # --- User credit limit caching ---
    credit_key = f"user:{current_user.email}:credit_limit"
    credit_limit = r.get(credit_key)

    if credit_limit:
        credit_limit = float(credit_limit)
    else:
        credit_limit = current_user.credit_limit
        r.setex(credit_key, 3600, credit_limit)  # cache for 1h

    # Check credit limit
    if current_user.dues + transaction.amount > credit_limit:
        raise HTTPException(status_code=400, detail="Rejected! (reason: credit limit)")

    # Process transaction
    fee_amount = transaction.amount * (fee_percentage / 100)
    db_transaction = Transaction(user_id=current_user.id, merchant_id=merchant_id,
                                 amount=transaction.amount, fee_paid=fee_amount)

    current_user.dues += transaction.amount
    session.add(db_transaction)
    session.add(current_user)
    session.commit()

    app_logger.info(f"Transaction: User={current_user.email}, Merchant={transaction.merchant_name}, Amount={transaction.amount}")

    return {"message": "Success!"}

    
@app.post("/payback", summary="Record the current user's payback")
@limiter.limit("10/minute")
def payback_dues(request: Request,payback: Payback, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if payback.amount > current_user.dues:
        raise HTTPException(status_code=400, detail="Payback amount exceeds total dues.")

    current_user.dues -= payback.amount
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    app_logger.info(f"Payback: User={current_user.email}, Amount={payback.amount}, Remaining dues={current_user.dues}")

    return {f"Dues for {current_user.name} (dues: {current_user.dues})"}


# --- Reporting Endpoints (also protected) ---

@app.get("/report/fees/{merchant_name}", summary="Report fees collected from a merchant")
def report_merchant_fees(merchant_name: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    merchant = session.exec(select(Merchant).where(Merchant.name == merchant_name)).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return {f"Total fees from {merchant.name}": merchant.total_fees_collected}

@app.get("/report/me/dues", summary="Report current user's total dues")
def report_my_dues(current_user: User = Depends(get_current_user)):
    return {f"Dues for {current_user.name}": current_user.dues}

@app.get("/report/users-at-limit", summary="Report users who have reached their credit limit")
def report_users_at_credit_limit(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    cache_key = "report:users_at_limit"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    users_at_limit = session.exec(select(User).where(User.dues >= User.credit_limit)).all()
    result = {"users_at_credit_limit": [user.name for user in users_at_limit]} if users_at_limit else {"message": "No users are currently at their credit limit."}

    r.setex(cache_key, 60, json.dumps(result))  # cache for 60s
    return result


@app.get("/report/total-dues", summary="Report total dues from all users")
def report_total_dues(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    cache_key = "report:total_dues"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    users = session.exec(select(User).where(User.dues > 0)).all()
    total = sum(user.dues for user in users)
    user_dues = {user.name: user.dues for user in users}
    result = {"total_dues": total, "individual_dues": user_dues}

    r.setex(cache_key, 60, json.dumps(result))  # cache for 60s
    app_logger.info(f"Report accessed by {current_user.email} | Total dues: {total}")
    return result
