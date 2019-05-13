import json

class GeoJSON(object):
    def __init__(self):
        self.data = {        
            "type": "FeatureCollection",
            "features": []
        }

    def add_line_string(self, coords, props={}):
        self.data["features"].append({
            "type": "Feature",
            "properties": props,
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        })

        return self


    def add_point(self, lon, lat, props={}):
        self.data["features"].append({
            "type": "Feature",
            "properties": props,
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        })

    def save_file(self, filename='path.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.data, indent=True))
            f.close()