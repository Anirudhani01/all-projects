from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional, List
from pydantic import BaseModel
from mysql.connector import connect
from datetime import date
import hashlib

app = FastAPI()

# Database connection
_connection = connect(
    host='localhost',
    user='anirudh',
    password='password123',
    database='players_data'
)

# Input model (used for insert)
class PlayerIn(BaseModel):
    playerID: str
    birthYear: Optional[int] = None
    birthMonth: Optional[int] = None
    birthDay: Optional[int] = None
    birthCountry: Optional[str] = None
    birthState: Optional[str] = None
    birthCity: Optional[str] = None
    deathYear: Optional[int] = None
    deathMonth: Optional[int] = None
    deathDay: Optional[int] = None
    deathCountry: Optional[str] = None
    deathState: Optional[str] = None
    deathCity: Optional[str] = None
    nameFirst: Optional[str] = None
    nameLast: Optional[str] = None
    nameGiven: Optional[str] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    bats: Optional[str] = None
    throws: Optional[str] = None
    debut: Optional[date] = None
    finalGame: Optional[date] = None
    retroID: Optional[str] = None
    bbrefID: Optional[str] = None

# Output model (full player)
class PlayerOut(PlayerIn):
    playerHash: str

# Summary model (used for /player/hash/{hash})
class PlayerSummary(BaseModel):
    nameFirst: Optional[str]
    nameLast: Optional[str]
    birthYear: Optional[int]
    birthCountry: Optional[str]
    weight: Optional[int]
    height: Optional[int]

# Hash generator
def generate_player_hash(data: dict) -> str:
    base = f"{data.get('nameFirst', '')}{data.get('nameLast', '')}{data.get('birthYear', '')}"
    return hashlib.sha256(base.encode()).hexdigest()[:32]

# POST: Add player
@app.post("/player/", response_model=PlayerOut)
def add_player(player: PlayerIn):
    try:
        player_data = player.dict()
        player_data["playerHash"] = generate_player_hash(player_data)

        cursor = _connection.cursor()
        query = """
        INSERT INTO players_table (
            playerID, birthYear, birthMonth, birthDay, birthCountry, birthState, birthCity,
            deathYear, deathMonth, deathDay, deathCountry, deathState, deathCity,
            nameFirst, nameLast, nameGiven, weight, height, bats, throws,
            debut, finalGame, retroID, bbrefID, playerHash
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = tuple(player_data.values())
        cursor.execute(query, values)
        _connection.commit()
        cursor.close()
        return PlayerOut(**player_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insert failed: {str(e)}")

# POST: Redirect from ID to hash endpoint
@app.post("/player/link/{playerID}")
def redirect_to_player_hash(playerID: str):
    try:
        cursor = _connection.cursor()
        cursor.execute("SELECT playerHash FROM players_table WHERE playerID = %s", (playerID,))
        result = cursor.fetchone()
        cursor.close()

        if not result:
            raise HTTPException(status_code=404, detail="Player ID not found.")

        player_hash = result[0]
        return RedirectResponse(url=f"/player/hash/{player_hash}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# GET: Player by hash (summary only)
@app.get("/player/hash/{playerHash}", response_model=PlayerSummary)
def get_player_by_hash(playerHash: str):
    try:
        cursor = _connection.cursor()
        cursor.execute("""
            SELECT nameFirst, nameLast, birthYear, birthCountry, weight, height
            FROM players_table
            WHERE playerHash = %s
        """, (playerHash,))
        row = cursor.fetchone()
        cursor.close()

        if not row:
            raise HTTPException(status_code=404, detail="Player not found by hash.")

        return PlayerSummary(
            nameFirst=row[0],
            nameLast=row[1],
            birthYear=row[2],
            birthCountry=row[3],
            weight=row[4],
            height=row[5]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Admin: Generate missing hashes for existing records
@app.post("/admin/generate-player-hashes")
def generate_hashes_for_existing():
    try:
        cursor = _connection.cursor()
        cursor.execute("SELECT playerID, nameFirst, nameLast, birthYear FROM players_table WHERE playerHash IS NULL")
        players = cursor.fetchall()

        updated = 0
        for playerID, first, last, year in players:
            first = first or ""
            last = last or ""
            year = str(year) if year else ""
            raw = f"{first}{last}{year}"
            hash_val = hashlib.sha256(raw.encode()).hexdigest()[:32]
            cursor.execute("UPDATE players_table SET playerHash = %s WHERE playerID = %s", (hash_val, playerID))
            updated += 1

        _connection.commit()
        cursor.close()
        return {"message": f"Hashes generated for {updated} players."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")