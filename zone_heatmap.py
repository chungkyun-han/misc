import os.path as opath
import pandas as pd
import csv
import json
import folium
import webbrowser


ifpath = 'zones_with_coordinates.csv' # including header!!
th_scale = [0, 100, 150, 200, 400]

#
geo_json_fpath = 'zones.json'
geo_json = {"type": "FeatureCollection", "features": []}

min_lon, max_lon = 1e400, -1e400
min_lat, max_lat = 1e400, -1e400

with open(ifpath, 'rb') as r_csvfile:
    reader = csv.reader(r_csvfile)
    header = reader.next()
    hid = dict((cn, i) for i, cn in enumerate(header))
    for row in reader:
        zone_id = int(row[hid['zone_id']])
        zone_name = row[hid['zone_name']]
        _poly = row[hid['polygon_coordinates']][len('POLYGON(('):-len('))')].split(',')
        poly = []
        for _coord in _poly:
            lon, lat = map(eval, _coord.split())
            if lon < min_lon: min_lon = lon
            if max_lon < lon : max_lon = lon
            if lat < min_lat: min_lat = lat
            if max_lat < lat : max_lat = lat
            poly += [(lon, lat)]
        if not opath.exists(geo_json_fpath):
            feature = {"type":"Feature",
                           "id": zone_id,
                           "geometry":
                               {"type": "Polygon",
                                "coordinates": [poly]
                                }
                          }
            geo_json["features"].append(feature)
    #
    if not opath.exists(geo_json_fpath):
        with open(geo_json_fpath, 'w') as f:
            json.dump(geo_json, f)
#
df = pd.read_csv(ifpath)

lonC, latC = (min_lon + max_lon) / 2.0, (min_lat + max_lat) / 2.0
map_osm = folium.Map(location=[latC, lonC], zoom_start=11)
map_osm.geo_json(geo_path=geo_json_fpath, data=df,
                columns=['zone_id', 'value'],
                threshold_scale=th_scale,
                key_on='feature.id',
                fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2,
                legend_name='Value')
#
fpath = 'viz.html'
map_osm.save(fpath)
html_url = 'file://%s' % opath.join(opath.dirname(opath.realpath(__file__)), fpath)
webbrowser.open_new(html_url)