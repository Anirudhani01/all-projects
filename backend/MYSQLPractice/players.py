# Debug endpoint to list all playerIDs in the table
@app.get("/debug/playerIDs/")
def list_player_ids():
    _cursor.execute("SELECT playerID FROM players_table")
    ids = [row[0] for row in _cursor.fetchall()]
    return {"playerIDs": ids}
from mysql.connector import connect
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query
from typing import List
from typing import Optional

from pydantic import BaseModel

# Pydantic model for a Player
class Player(BaseModel):
    playerID: str
    birthYear: int | None = None
    birthMonth: int | None = None
    birthDay: int | None = None
    birthCountry: str | None = None
    birthState: str | None = None
    birthCity: str | None = None
    deathYear: int | None = None
    deathMonth: int | None = None
    deathDay: int | None = None
    deathCountry: str | None = None
    deathState: str | None = None
    deathCity: str | None = None
    nameFirst: str | None = None
    nameLast: str | None = None
    nameGiven: str | None = None
    weight: int | None = None
    height: int | None = None
    bats: str | None = None
    throws: str | None = None
    debut: str | None = None
    finalGame: str | None = None
    retroID: str | None = None
    bbrefID: str | None = None

# Pydantic model for paginated response
class PaginatedPlayers(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[Player]

# Pydantic model for cursor-based response
class CursorPlayers(BaseModel):
    next_cursor: str | None
    limit: int
    data: list[Player]

# Pydantic model for page-based response
class PagePlayers(BaseModel):
    page: int
    page_size: int
    total_pages: int
    total_records: int
    data: list[Player]



from fastapi import HTTPException

app = FastAPI()

# Establish DB connection at startup
_connection = connect(
    host='localhost',
    user='anirudh',
    password='password123',
    database='players_data'
)
_cursor = _connection.cursor()

# Step 2: Load and clean data
_data = pd.read_csv('/home/anirudh/MYSQLPractice/People.csv')
_data = _data.replace({np.nan: None})
act_data = [tuple(row) for row in _data.itertuples(index=False, name=None)]

# Step 3: Insert Data (optional, comment out after one-time run)
def insert_data_into_database():
    _create_query = """
    CREATE TABLE IF NOT EXISTS players_table (
        playerID VARCHAR(100), 
        birthYear INT, 
        birthMonth INT,
        birthDay INT,
        birthCountry VARCHAR(100),
        birthState VARCHAR(100),
        birthCity VARCHAR(100),
        deathYear INT,
        deathMonth INT,
        deathDay INT,
        deathCountry VARCHAR(100),
        deathState VARCHAR(100),
        deathCity VARCHAR(100), 
        nameFirst VARCHAR(100), 
        nameLast VARCHAR(100), 
        nameGiven VARCHAR(100), 
        weight INT,
        height INT,
        bats VARCHAR(100), 
        throws VARCHAR(100), 
        debut DATE,
        finalGame DATE,
        retroID VARCHAR(100), 
        bbrefID VARCHAR(100)
    );
    """
    _cursor.execute(_create_query)

    _insert_query = """
    INSERT INTO players_table (
        playerID, birthYear, birthMonth, birthDay, birthCountry, birthState, birthCity,
        deathYear, deathMonth, deathDay, deathCountry, deathState, deathCity,
        nameFirst, nameLast, nameGiven, weight, height, bats, throws,
        debut, finalGame, retroID, bbrefID
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for rec in act_data:
        _cursor.execute(_insert_query, rec)

    _connection.commit()
    print("✅ Data inserted successfully.")

# Uncomment the next line only for the first run
# insert_data_into_database()


# POST endpoint to add a new player
@app.post("/add/player/", response_model=Player)
def add_player(player: Player):
    # Check if player already exists
    _cursor.execute("SELECT 1 FROM players_table WHERE playerID = %s", (player.playerID,))
    if _cursor.fetchone():
        raise HTTPException(status_code=400, detail="Player with this playerID already exists.")

    _insert_query = """
        INSERT INTO players_table (
            playerID, birthYear, birthMonth, birthDay, birthCountry, birthState, birthCity,
            deathYear, deathMonth, deathDay, deathCountry, deathState, deathCity,
            nameFirst, nameLast, nameGiven, weight, height, bats, throws,
            debut, finalGame, retroID, bbrefID
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    _cursor.execute(_insert_query, (
        player.playerID, player.birthYear, player.birthMonth, player.birthDay, player.birthCountry, player.birthState, player.birthCity,
        player.deathYear, player.deathMonth, player.deathDay, player.deathCountry, player.deathState, player.deathCity,
        player.nameFirst, player.nameLast, player.nameGiven, player.weight, player.height, player.bats, player.throws,
        player.debut, player.finalGame, player.retroID, player.bbrefID
    ))
    _connection.commit()
    return player

# FastAPI route to get player info
@app.get("/get/playerID/{playerID}/", response_model=list[Player])
def read_data_from_database(playerID: str):
    print(f"Searching for playerID: {playerID}")
    _query = "SELECT * FROM players_table WHERE playerID = %s;"
    _cursor.execute(_query, (playerID,))
    result = _cursor.fetchall()
    # Convert DB rows to Player dicts
    columns = [desc[0] for desc in _cursor.description]
    players = [Player(**dict(zip(columns, row))) for row in result]
    return players


# 📄 Get all players with pagination

# pagination tech - using limit and offset
@app.get("/get/players/", response_model=PaginatedPlayers)
def get_players(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    _query = "SELECT * FROM players_table LIMIT %s OFFSET %s;"
    _cursor.execute(_query, (limit, offset))
    rows = _cursor.fetchall()

    # Optional: total count for frontend pagination
    _cursor.execute("SELECT COUNT(*) FROM players_table")
    total_count = _cursor.fetchone()[0]

    columns = [desc[0] for desc in _cursor.description]
    players = [Player(**dict(zip(columns, row))) for row in rows]

    return PaginatedPlayers(
        total=total_count,
        limit=limit,
        offset=offset,
        data=players
    )

# pagination tech - Cursor-Based Pagination
@app.get("/players/", response_model=CursorPlayers)
def get_players(
    cursor: Optional[str] = Query(None, description="Start after this playerID"),
    limit: int = Query(10, ge=1)
):
    if cursor:
        _query = """
            SELECT * FROM players_table
            WHERE playerID > %s
            ORDER BY playerID ASC
            LIMIT %s;
        """
        _cursor.execute(_query, (cursor, limit))
    else:
        _query = """
            SELECT * FROM players_table
            ORDER BY playerID ASC
            LIMIT %s;
        """
        _cursor.execute(_query, (limit,))
    
    rows = _cursor.fetchall()
    columns = [desc[0] for desc in _cursor.description]
    players = [Player(**dict(zip(columns, row))) for row in rows]

    # Get next cursor (last playerID in this batch)
    next_cursor = players[-1].playerID if players else None

    return CursorPlayers(
        next_cursor=next_cursor,
        limit=limit,
        data=players
    )
    
    
@app.get("/get/players1/", response_model=PagePlayers)
def get_players(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page (max 100)")
):
    offset = (page - 1) * page_size

    # Fetch paginated records
    _query = "SELECT * FROM players_table LIMIT %s OFFSET %s"
    _cursor.execute(_query, (page_size, offset))
    rows = _cursor.fetchall()

    # Get total number of rows
    _cursor.execute("SELECT COUNT(*) FROM players_table")
    total_records = _cursor.fetchone()[0]
    total_pages = (total_records + page_size - 1) // page_size  # Ceiling division

    columns = [desc[0] for desc in _cursor.description]
    players = [Player(**dict(zip(columns, row))) for row in rows]

    return PagePlayers(
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_records=total_records,
        data=players
    )
    

#Pagination - Infinite Scroll with Limit & Offset
@app.get("/get/players2/", response_model=PaginatedPlayers)
def get_players(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    _query = "SELECT * FROM players_table LIMIT %s OFFSET %s;"
    _cursor.execute(_query, (limit, offset))
    rows = _cursor.fetchall()

    # Total record count (optional)
    _cursor.execute("SELECT COUNT(*) FROM players_table")
    total = _cursor.fetchone()[0]

    columns = [desc[0] for desc in _cursor.description]
    players = [Player(**dict(zip(columns, row))) for row in rows]

    return PaginatedPlayers(
        data=players,
        limit=limit,
        offset=offset,
        total=total
    )

if __name__=='__main__':
    app.run()