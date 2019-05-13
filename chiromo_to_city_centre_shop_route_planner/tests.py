import os
import json

def main():
    with open('shapefile.json', 'w', encoding='utf-8') as mf:
        mf.write(json.dumps({
            "shapefiles": list(filter(lambda f : f.endswith('.shp'), os.listdir('./map_client/shapefile/kenya-latest-free.shp')))
        }, indent=True))

if __name__ == '__main__':
    main()