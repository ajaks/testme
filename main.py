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
                result.append(item)

    return web.json_response({
            'posts': sorted(result, key=lambda r: r['date'], reverse=True),
            'posts_count': len(result)
    })


app = web.Application()
app.add_routes(routes)
web.run_app(app)
