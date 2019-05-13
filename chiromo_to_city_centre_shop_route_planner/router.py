from math import atan2, pi

from route_parser import Parser


DIST_FROM_START = "dist_from_start"
DIST_FROM_END = "dist_from_end"
INFINITY = 1E+20

TRANSPORT = {
    "foot": ''
}

class Router(object):
    def __init__(self, filename = '', transport='foot'):
        self.parser = Parser(filename)
        self.transport = transport

    def find_point_by_name(self, name):
        points = []
        if not name:
            return points
        for node in self.parser.nodes.values():
            if name.lower() in node["tags"].get('name', '').lower():
                points.append(node)

        for way  in self.parser.ways.values():
            if name.lower() in way["tags"].get('name', '').lower():
                points.append(way)

        return points

    def get_chosen_point_coords(self, index, points):
        if 0 < index <= len(points):
            point = points[index - 1]
            if point["type"] != 'way':
                return self.find_point_by_coords(
                    point=point,
                )
            node = self.find_closest_node_to_centre(point)
            if not point["tags"].get('highway', ''):
                return self.find_point_by_coords(
                    point=node,
                )
            return point["nodes"][0]

        return None

    def find_point_by_name_cli(self, name):
        if not name:
            name = input('What place would you like to find?\n: ')
        points = self.find_point_by_name(name)
        if not points:
            print('{} does not exist in the map'.format(name))
            if input('Would you like to try again? [y/N] ') in ('y', 'Y'):
                return self.find_point_by_name_cli('')
            return None
        elif len(points) == 1:
            return points[0]

        print('Which place would you like to select?')
        for i, point in enumerate(points):
            print('({}) {} [type="{}"]'.format(i + 1, point["tags"]["name"], point["type"]))

        index = int(input('> '))
        point = self.get_chosen_point_coords(index, points)
        if point:
            return point

        raise Exception('Invalid input: Number given is not within range')

    def way_to_lonLat(self, way):
        res = []
        for nd in way["nodes"]:
            res.append([nd["lon"], nd["lat"]])
            
        return res

    def find_closest_node_to_centre(self, way):
        centre = self.find_centre_of_way(way)
        max_dist = 1E+20
        point = None
        for node in way["nodes"]:
            dlat = centre["lat"] - node['lat']
            dlon = centre["lon"] - node['lon']
            dist = dlon * dlon + dlat * dlat

            if dist < max_dist:
                max_dist = dist
                point = node

        return point

    def find_centre_of_way(self, way):
        res = {"lon": 0, "lat": 0}
        num_nodes = len(way["nodes"])
        for node in way["nodes"]:
            res["lon"] += node["lon"]
            res["lat"] += node["lat"]

        res["lon"] /= num_nodes
        res["lat"] /= num_nodes

        return res

    def check_node_is_part_of_highway(self, node):
        for way in node["ways"]:
            if self.parser.ways[way]["tags"].get('highway', ''):
                return True

        return False
        

    def find_point_by_coords(self, point, is_highway = True):
        max_dist = 1E+20
        found_node = None
        for key, node in self.parser.nodes.items():
            dist = self.dist_between_nodes(point, node)
            if dist < max_dist:
                if is_highway and not self.check_node_is_part_of_highway(node):
                    continue

                max_dist = dist
                found_node = node

        return found_node

    def dist_between_nodes(self, node, node2):
        dlat = node2['lat'] - node['lat']
        dlon = node2['lon'] - node['lon']
        return dlon * dlon + dlat * dlat

    def find_route(self, start, end):
        closed_set = set()
        start[DIST_FROM_START] = 0
        start[DIST_FROM_END] = self.dist_between_nodes(start, end)
        open_set = [start]
        came_from = {}
        node_associated_way = {}
        count = 0
        while open_set and count < 10000:
            current = open_set[0]
            for i, node in enumerate(open_set):
                if self.total_distance(current) > self.total_distance(node):
                    current = node
            if current["id"] == end["id"]:
                route, route_ids = self.find_path(came_from, current)
                return route, self.get_directions(route_ids, node_associated_way)

            open_set.remove(current)
            closed_set.add(current["id"])

            for neighbour, way_id in self.get_neighbours(current):
                if neighbour["id"] not in closed_set:
                    if neighbour not in open_set:
                        neighbour[DIST_FROM_START] = INFINITY
                        neighbour[DIST_FROM_END] = self.dist_between_nodes(neighbour, end)
                        open_set.append(neighbour)

                    dist_from_start = current[DIST_FROM_START] + self.dist_between_nodes(current, neighbour)
                    if dist_from_start < neighbour[DIST_FROM_START]:
                        came_from[neighbour["id"]] = current["id"]
                        node_associated_way[neighbour["id"]] = way_id
                        neighbour[DIST_FROM_START] = dist_from_start

            count += 1

        return [], []

    def total_distance(self, node):
        return node[DIST_FROM_START] + node[DIST_FROM_END]

    def find_path(self, came_from, end):
        node_id = end["id"]
        route_ids = []
        route = []
        while node_id:
            node = self.parser.nodes[node_id]
            route.insert(0, self.node_to_lon_lat(node))
            route_ids.insert(0, node_id)
            node_id = came_from.get(node_id, '')

        return route, route_ids

    def get_directions(self, route_ids, node_associated_way):
        directions = []
        # print(route_ids)
        offset = 1
        for i, route_id in enumerate(route_ids[offset:-1]):
            next_id = route_ids[i + offset + 1]
            current_way = self.parser.ways[node_associated_way[route_id]]
            next_way = self.parser.ways[node_associated_way[next_id]]
            # print("Point")
            # print(route_id, next_id)
            # print(current_way, next_way)

        return directions

    def angle_between_points(self, node, point):
        d_lat = node['lat'] - point['lat']
        d_lon = node['lon'] - point['lon']
        return atan2(d_lat, d_lon) * (180 / pi)

    def compass_direction(self, angle):
        increment = 45
        current = increment / 2 
        if 360 - current < angle <= 360 or 0 <= angle < current:
            return 'N'
        if current <= angle < current + increment:
            return 'NE'
        current += increment
        if current <= angle < current + increment:
            return 'E'
        current += increment
        if current <= angle < current + increment:
            return 'SE'
        current += increment
        if current <= angle < current + increment:
            return 'S'
        current += increment
        if current <= angle < current + increment:
            return 'SW'
        current += increment
        if current <= angle < current + increment:
            return 'W'
        current += increment
        if current <= angle < current + increment:
            return 'NW'

        return 'Unknown'
    
    def node_to_lon_lat(self, node):
        return [node["lon"], node["lat"]]

    def node_to_lat_lon(self, node):
        return self.node_to_lon_lat(node)[::-1]

    def check_highway(self, highway):
        return highway not in ['footway', '']

    def get_neighbours(self, node):
        for way_id in node["ways"]:
            way = self.parser.ways[way_id]
            way_nodes = way["nodes"]
            oneway = way["tags"].get('oneway', '')
            highway = way["tags"].get('highway', '')
            junction = way["tags"].get('junction', '')
            for i, nd in enumerate(way_nodes):
                if nd["id"] == node["id"]:
                    if len(way_nodes) != i + 1 and (self.transport == 'foot' or self.check_highway(highway)): #oneway or both ways[oneway="yes"]
                        yield way_nodes[i + 1], way_id
                    if i != 0 and (self.transport == 'foot' or ((oneway in ['-1', 'no'] or not oneway) and  self.check_highway(highway) and not junction == 'roundabout')): #reverse direction if oneway opp. or both
                        yield way_nodes[i - 1], way_id
