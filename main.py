import json
from datetime import datetime

from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/')
async def posts(request):
    with open('data/post.json') as f:
        posts_data = json.load(f)

    with open('data/comments.json') as f:
        comments_data = json.load(f)
    result = []

    for item in posts_data['posts']:
        if item['deleted'] is False:
            if datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S') < datetime.now():
                item['comments_count'] = len([x for x in comments_data['comments'] if x['post_id'] == item['id']])
                del item['deleted']
                result.append(item)

    return web.json_response({
            'posts': sorted(result, key=lambda r: datetime.strptime(r['date'], '%Y-%m-%dT%H:%M:%S'), reverse=True),
            'posts_count': len(result)
    })


@routes.get('/post/{id:\d+}')
async def post(request):
    post_id = int(request.match_info['id'])

    with open('data/post.json') as f:
        posts_data = json.load(f)

    with open('data/comments.json') as f:
        comments_data = json.load(f)

    result = None

    for item in posts_data['posts']:
        if item['id'] == post_id and datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S') < datetime.now():
            result = item

    if not result or result['deleted']:
        raise web.HTTPNotFound()

    comments = [x for x in comments_data['comments'] if x['post_id'] == result['id']]

    result['comments'] = sorted(comments, key=lambda r: datetime.strptime(r['date'], '%Y-%m-%dT%H:%M:%S'), reverse=True)
    result['comments_count'] = len(comments)
    del result['deleted']

    return web.json_response(result)


app = web.Application()
app.add_routes(routes)
web.run_app(app)
