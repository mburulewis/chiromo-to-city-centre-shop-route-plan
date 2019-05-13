from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from router import Router
from geojson import GeoJSON

router = Router('./map.osm')
app = Flask(__name__, static_folder='map_client', static_url_path='')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)
points = []


def get_route_color():
    colors = ['#ff0', '#f0f', '#0ff', '#00f', '#0f0', '#f00', '#000']
    for c in colors:
        yield c
    yield from get_route_color()

color = get_route_color()

@app.route("/")
def map():
    return app.send_static_file('index.html')

@socketio.on('find')
def check_point(data):
    return {
        "points": router.find_point_by_name(data['place'])
    }

@socketio.on('coords')
def get_point_coords(data):
    return {
        "node": router.get_chosen_point_coords(data['index'] + 1, data['points'])
    }

@socketio.on('route')
def create_route(data):
    path = data.get('points', [])
    geo = GeoJSON()
    for i, _ in enumerate(path[:-1]):
        if path[i+1] is None:
            path[i+1] = path[i]
        elif path[i] is not None:            
            route, _ = router.find_route(path[i], path[i+1])
            if route:
                start, end = route[0], route[-1]
                geo.add_point(lon=start[0], lat=start[1], props={
                    'title': path[i]['tags'].get('name', path[i]['id'])
                })
                geo.add_point(lon=end[0], lat=end[1], props={
                    'title': path[i+1]['tags'].get('name', path[i+1]['id'])
                })
                geo.add_line_string(route, {
                    "style": {
                        "color": next(color)
                    }
                })
            
    return geo.data



if __name__ == '__main__':
    socketio.run(app, debug=True)