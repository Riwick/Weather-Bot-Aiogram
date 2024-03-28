import asyncpg

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


async def connect_db():
    conn = await asyncpg.connect(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    return conn


async def save_position(user_id: int, lat: float, lon: float):
    conn = await connect_db()
    try:
        stmt = f"INSERT INTO public.user_geolocation (user_id, lat, lon) VALUES {user_id, lat, lon};"
        await conn.execute(stmt)

    finally:
        await conn.close()


async def get_position(user_id: int) -> asyncpg.Record:
    conn = await connect_db()
    query = f"SELECT * FROM public.user_geolocation WHERE user_id={user_id};"
    return await conn.fetch(query)


async def update_position(user_id: int, lat: float, lon: float):
    conn = await connect_db()
    try:
        stmt = f"UPDATE public.user_geolocation SET lat={lat}, lon={lon} WHERE user_id={user_id};"
        await conn.execute(stmt)

    finally:
        await conn.close()
