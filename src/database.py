import logging

import asyncpg

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


async def connect_db():
    try:
        conn = await asyncpg.connect(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        return conn
    except Exception as e:
        logging.log(level=logging.CRITICAL, msg=e)
        return None


async def save_position(user_id: int, lat: float, lon: float):
    conn = await connect_db()
    try:
        stmt = f"INSERT INTO public.user_geolocation (user_id, lat, lon) VALUES {user_id, lat, lon};"
        await conn.execute(stmt)
    except Exception as e:
        logging.log(level=logging.CRITICAL, msg=e)

    finally:
        await conn.close()


async def update_position(user_id: int, lat: float, lon: float):
    conn = await connect_db()
    try:
        stmt = f"UPDATE public.user_geolocation SET lat={lat}, lon={lon} WHERE user_id={user_id};"
        await conn.execute(stmt)

    finally:
        await conn.close()


async def get_all_users(offset: int):
    conn = await connect_db()
    try:
        query = f"SELECT * FROM public.user_geolocation LIMIT 20 OFFSET {offset}"
        return await conn.fetch(query)
    except Exception as e:
        pass
