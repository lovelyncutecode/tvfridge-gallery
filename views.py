from aiohttp import web
import jinja2
import aiohttp_jinja2
import os
from sqlalchemy import text
from dbmanager import *

async def filtered_query(request,checkb1,checkb2,customfilter=text('')):
    async with request.app['db'].acquire() as conn:
            items = [dict(row.items()) async for row in conn.execute(items_tbl.select().where(customfilter).order_by(items_tbl.c.clicks.desc()))]
            return aiohttp_jinja2.render_template('index.html',
                                              request,
                                              {'items':items,'checkb1':checkb1,'checkb2':checkb2})

async def get_all_items(request):
    res = await filtered_query(request,0,0)
    return res

async def filter_items(request):
    data = await request.post()
    if 'checkb1' in data and 'checkb2' in data:
        res = await filtered_query(request,1,1)
        return res
    elif 'checkb1' in data : 
        res = await filtered_query(request,1,0,text("items.type = 1"))
        return res
    elif 'checkb2' in data : 
        res = await filtered_query(request,0,1,text("items.type = 2"))
        return res
    else:
        res = await filtered_query(request,0,0)
        return res

@aiohttp_jinja2.template('index.html')
async def update_item(request):
    data = await request.post()
    id = data['id']
    
    async with request.app['db'].acquire() as conn:
        result = await conn.execute(
            items_tbl.update().where(items_tbl.c.id == id).values(clicks=items_tbl.c.clicks + 1)
        )

    if result.rowcount == 0:
        return web.json_response({'error': 'Item not found'}, status=404)
    redir=await filter_items(request)    
    return redir

async def post(request):
    data = await request.post()
    action = data['action']
    if action == 'click':
        res = await update_item(request)
        return res
    if action == 'filter':
        res = await filter_items(request)
        return res   

async def app_factory(args=()):
    app = web.Application()

    app.on_startup.append(attach_db)
    app.on_shutdown.append(shutdown_db)

    #uncomment to popuulate database
    #if '--make-table' in args:
    #    app.on_startup.append(setup_table)

    BASE_DIR = os.path.dirname(__file__)
    jinja_env = aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader(os.path.join(BASE_DIR, 'templates')),
    context_processors=[aiohttp_jinja2.request_processor], )

    routes = [
    ('GET', '/',        get_all_items,  'main'),
    ('POST', '/',        post,  'main'),
    ]
    for route in routes:
        app.router.add_route(route[0], route[1], route[2], name=route[3])

    return app