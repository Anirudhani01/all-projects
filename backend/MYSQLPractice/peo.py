# players_api_secure.py
# This version uses POST for player lookup to avoid exposing playerID or hash in the URL.
# Only public fields and playerID_hash are returned in the response.

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import text
from db import engine
import hashlib

app = FastAPI()

# --- Pydantic Models ---

# Base model with all common fields
class PlayerBase(BaseModel):
    birthYear: Optional[float] = None
    birthMonth: Optional[float] = None
    birthDay: Optional[float] = None
    birthCountry: Optional[str] = None
    birthState: Optional[str] = None
    birthCity: Optional[str] = None
    deathYear: Optional[float] = None
    deathMonth: Optional[float] = None
    deathDay: Optional[float] = None
    deathCountry: Optional[str] = None
    deathState: Optional[str] = None
    deathCity: Optional[str] = None
    nameFirst: Optional[str] = None
    nameLast: Optional[str] = None
    nameGiven: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    bats: Optional[str] = None
    throws: Optional[str] = None
    debut: Optional[str] = None
    finalGame: Optional[str] = None
    retroID: Optional[str] = None
    bbrefID: Optional[str] = None

# Output model for API responses (expose only the hash, not the real playerID)
class PlayerOut(PlayerBase):
    playerHash: str

# Request model for secure lookup
class PlayerLookupRequest(BaseModel):
    playerID: str

# Input model for creating a player (client provides playerID)
class PlayerIn(PlayerBase):
    playerID: str

# Request model for paginated player listing
class PlayerListRequest(BaseModel):
    skip: int = 0
    limit: int = 10

# --- Endpoint: Secure player lookup using POST ---
@app.post("/players/lookup", response_model=PlayerOut)
def lookup_player(request: PlayerLookupRequest):
    player_id = request.playerID
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT playerHash, birthYear, birthMonth, birthDay, birthCountry, birthState, birthCity, "
                 "deathYear, deathMonth, deathDay, deathCountry, deathState, deathCity, "
                 "nameFirst, nameLast, nameGiven, weight, height, bats, throws, debut, finalGame, retroID, bbrefID "
                 "FROM players_table WHERE playerID = :player_id"),
            {"player_id": player_id}
        )
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Player not found")
        return PlayerOut(
            playerHash=row[0],
            birthYear=row[1], birthMonth=row[2], birthDay=row[3], birthCountry=row[4], birthState=row[5], birthCity=row[6],
            deathYear=row[7], deathMonth=row[8], deathDay=row[9], deathCountry=row[10], deathState=row[11], deathCity=row[12],
            nameFirst=row[13], nameLast=row[14], nameGiven=row[15], weight=row[16], height=row[17], bats=row[18], throws=row[19],
            debut=str(row[20]) if row[20] is not None else None, finalGame=str(row[21]) if row[21] is not None else None, retroID=row[22], bbrefID=row[23]
        )

# --- Endpoint: Create a new player ---
@app.post("/players/", response_model=PlayerOut)
def create_player(player: PlayerIn):
    # Hash the playerID
    player_hash = hashlib.sha256(player.playerID.encode('utf-8')).hexdigest()
    # Prepare the insert statement (all fields)
    insert_stmt = text('''
        INSERT INTO players_table (
            playerID, birthYear, birthMonth, birthDay, birthCountry, birthState, birthCity,
            deathYear, deathMonth, deathDay, deathCountry, deathState, deathCity,
            nameFirst, nameLast, nameGiven, weight, height, bats, throws, debut, finalGame,
            retroID, bbrefID, playerHash
        ) VALUES (
            :playerID, :birthYear, :birthMonth, :birthDay, :birthCountry, :birthState, :birthCity,
            :deathYear, :deathMonth, :deathDay, :deathCountry, :deathState, :deathCity,
            :nameFirst, :nameLast, :nameGiven, :weight, :height, :bats, :throws, :debut, :finalGame,
            :retroID, :bbrefID, :playerHash
        )
    ''')
    params = player.dict()
    params['playerHash'] = player_hash
    with engine.begin() as conn:
        conn.execute(insert_stmt, params)
    # Return only the hash and public fields
    return PlayerOut(**player.dict(), playerHash=player_hash)

# --- Endpoint: Get a paginated list of players (output: PlayerOut) ---
@app.post("/players", response_model=List[PlayerOut])
def get_players(request: PlayerListRequest):
    skip = request.skip
    limit = request.limit
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT playerHash, birthYear, birthMonth, birthDay, birthCountry, birthState, birthCity, "
                 "deathYear, deathMonth, deathDay, deathCountry, deathState, deathCity, "
                 "nameFirst, nameLast, nameGiven, weight, height, bats, throws, debut, finalGame, retroID, bbrefID "
                 "FROM players_table LIMIT :limit OFFSET :skip"),
            {"limit": limit, "skip": skip}
        )
        players = [PlayerOut(
            playerHash=row[0],
            birthYear=row[1], birthMonth=row[2], birthDay=row[3], birthCountry=row[4], birthState=row[5], birthCity=row[6],
            deathYear=row[7], deathMonth=row[8], deathDay=row[9], deathCountry=row[10], deathState=row[11], deathCity=row[12],
            nameFirst=row[13], nameLast=row[14], nameGiven=row[15], weight=row[16], height=row[17], bats=row[18], throws=row[19],
            debut=str(row[20]) if row[20] is not None else None, finalGame=str(row[21]) if row[21] is not None else None, retroID=row[22], bbrefID=row[23]
        ) for row in result]
    return players

# How to use this API:
# 1. Start the server with: uvicorn players_api_secure:app --reload
# 2. POST /players/lookup with {"playerID": "aardsda01"} to look up a player securely
# 3. GET /players to see a paginated list of players (hash only)