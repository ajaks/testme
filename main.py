import json
from datetime import datetime

from aiohttp import web

DATA_FORMAT = '%Y-%m-%dT%H:%M:%S'

routes = web.RouteTableDef()


def get_data():
    with open('data/post.json') as f:
        posts_data = json.load(f)

    with open('data/comments.json') as f:
        comments_data = json.load(f)

    return posts_data, comments_data


def clean_data(data):
    del data['date_object']
    return data


@routes.get('/')
async def posts(request):
    posts_data, comments_data = get_data()
    result = []

    for item in posts_data['posts']:
        if item['deleted'] is False:
            item['date_object'] = datetime.strptime(item['date'], DATA_FORMAT)
            if item['date_object'] < datetime.now():
                item['comments_count'] = len([x for x in comments_data['comments'] if x['post_id'] == item['id']])
                del item['deleted']
                result.append(item)

    result.sort(key=lambda r: r['date_object'], reverse=True)
    result = list(map(clean_data, result))
    return web.json_response({
            'posts': result,
            'posts_count': len(result)
    })


@routes.get('/post/{id:\d+}')
async def post(request):
    post_id = int(request.match_info['id'])
    posts_data, comments_data = get_data()

    result = None

    for item in posts_data['posts']:
        if item['id'] == post_id and datetime.strptime(item['date'], DATA_FORMAT) < datetime.now():
            result = item

    if not result or result['deleted']:
        raise web.HTTPNotFound()

    comments = [x for x in comments_data['comments'] if x['post_id'] == result['id']]

    result['comments'] = sorted(comments, key=lambda r: datetime.strptime(r['date'], DATA_FORMAT), reverse=True)
    result['comments_count'] = len(comments)
    del result['deleted']

    return web.json_response(result)


app = web.Application()
app.add_routes(routes)
web.run_app(app)
