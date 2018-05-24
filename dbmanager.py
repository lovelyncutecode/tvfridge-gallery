from aiopg.sa import create_engine
import sqlalchemy as sa
from os.path import isfile
from envparse import env

metadata = sa.MetaData()
items_tbl = sa.Table(
    'items', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('type', sa.Integer, nullable=False),
    sa.Column('name', sa.String(255), unique=True, nullable=False),
    sa.Column('img', sa.String(255), unique=True),
    sa.Column('clicks', sa.Integer, default=0, nullable=False)
    )


async def create_table(engine):
    async with engine.acquire() as conn:
        await conn.execute('DROP TABLE IF EXISTS items')
        await conn.execute('''CREATE TABLE items (
            id SERIAL PRIMARY KEY,
            type INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL UNIQUE,
            img VARCHAR(255) UNIQUE,
            clicks INTEGER NOT NULL DEFAULT 0
        )''')


async def attach_db(app):
    if isfile('.env'):
        env.read_envfile('.env')
        app['db'] = await create_engine(
        ' '.join([
            'host='+env.str('host'),
            'port='+env.str('port'),
            'dbname='+env.str('dbname'),
            'user='+env.str('user'),
            'password='+env.str('password')
        ]))

async def shutdown_db(app):
    app['db'].close()
    await app['db'].wait_closed()
    app['db'] = None


async def populate_initial_values(engine):
    async with engine.acquire() as conn:
        await conn.execute(items_tbl.insert().values({'name': 'fancy fridge','img':'http://photogearfinder.com/wp-content/uploads/2018/03/standard-refrigerator-width-ft-inch-width-standard-depth-french-door-refrigerator-with-standard-fridge-width-mm.jpg','type':1, 'clicks': 0}))
        await conn.execute(items_tbl.insert().values({'name': 'budget-friendly fridge','img':'https://cdn.shopify.com/s/files/1/2023/9239/products/Outdoor_Beverage_Fridge_Main_large.jpg?v=1506216102','type':1,'clicks': 0}))
        await conn.execute(items_tbl.insert().values({'name': 'small tv','img':'https://wheeler-centre-heracles.s3.amazonaws.com/wheeler-centre/assets/66/1b3370a37411e4b253750b504f9d3d/6901b190a37411e4a4b403420a2508a0_content_small.jpg','type':2,'clicks': 0}))
        await conn.execute(items_tbl.insert().values({'name': 'enormous tv','img':'https://static-eu.insales.ru/images/products/1/5015/130790295/large_p71651_11675952_big.jpg','type':2,'clicks': 0}))

async def setup_table(app):
    await create_table(app['db'])
    await populate_initial_values(app['db'])        