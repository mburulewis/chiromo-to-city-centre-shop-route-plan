import json
import click
import re
import webbrowser
from pathlib import Path
from string import Template

from router import Router
from geojson import GeoJSON

def get_float_tuple(p_text):
    text = input('{}\n: '.format(p_text))
    values = re.split('\s+', text)
    l = len(values)
    if l != 2:
        print('Required number of values is 2 not {}'.format(l))
        return get_float_tuple(p_text)
    coords = []
    for val in values:
        try:
            coords.append(float(val))
        except ValueError as e:
            print(e.args[0])
            return get_float_tuple(p_text)

    return tuple(coords)

@click.command()
@click.option('--start', '-s', default='chiromo', help='Name of starting point of the route')
@click.option('--end', '-e', default='', help='Name of ending point of the route')
@click.option('--coords', help='Coordinates of the starting point[format="lat lon"]', nargs=2, type=float)
@click.option('--coorde', help='Coordinates of the ending point[format="lat lon"]', nargs=2, type=float)
def main(start, end, coords, coorde):
    router = Router('./map.osm')
    print('Would you like to search by name or by coordinates?')
    print('(1) Name')
    print('(2) Coordinates')
    index = click.prompt('', type=int)
    start_point, end_point = None, None
    if index == 1:
        if not start:
            start = click.prompt('What is your starting point?')
        start_point = router.find_point_by_name_cli(start)
        if not start_point:
            return print('Starting point not set')
        if not end:
            end = click.prompt('What is your destination?')
        end_point = router.find_point_by_name_cli(end)
        if not end_point:
            return print('Destination not set')
    elif index == 2:
        if not coords:
            coords = get_float_tuple('What is your starting point? [format="lat lon"]')
        start_point = router.find_point_by_coords(dict(lat=coords[0], lon=coords[1]))
        if not coorde:
            coorde = get_float_tuple('What is your destination? [format="lat lon"]').split(' ')
        end_point = router.find_point_by_coords(dict(lat=coorde[1], lon=coorde[1]))
    else:
        print('Invalid input')
        return
    route, _ = router.find_route(start_point, end_point)
    if route:
        print("Route found")
        geo = GeoJSON()
        geo.add_line_string(route)
        geo.add_point(lon=route[0][0], lat=route[0][1], props={
            "title": "Start"
        })
        geo.add_point(lon=route[-1][0], lat=route[-1][1], props={
            "title": "End"
        })
        js_file = ''
        with open('./map.template.js',encoding='utf-8') as f:
            js_file = Template(f.read()).safe_substitute(geojson=geo.data)
            f.close()
        with open('./map_client/index.js', 'w', encoding='utf-8') as f:
            f.write(js_file)
            f.close()

        webbrowser.open_new_tab(Path('./map_client/index.html').resolve().as_uri())


if __name__ == '__main__':
    main()