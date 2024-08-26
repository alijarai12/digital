from dmaps.models import GeometryFile, MunicipalityGeometry, ProvinceGeometry
from django.contrib.gis.geos import GEOSGeometry
from user.models import User
from django.contrib.gis.geos.prototypes.io import wkt_w
import geopandas as gpd
from django.contrib.gis.db.models import Q
import pandas as pd
from shapely.geometry import Point, LineString, MultiLineString
import fiona
import geopandas as gpd
from core.utils import pluscode


def handlegeometryfile(id):
    instance = GeometryFile.objects.get(id=id)
    file = str(instance.file_upload.path)
    file_type = instance.file_type
    gdf = gpd.read_file(file)
    if file_type == "municipality":
        for index, row in gdf.iterrows():
            attr_data = row.drop(["geometry"]).to_dict()
            name = attr_data.pop("name")
            geom = GEOSGeometry(str(row["geometry"]))
            bbox = list(row["geometry"].bounds)
            area_gdf = gpd.GeoDataFrame(geometry=[row["geometry"]], crs=gdf.crs)
            area_gdf.to_crs(epsg=3857, inplace=True)
            area = area_gdf.area.iloc[0] / 1000000
            MunicipalityGeometry.objects.create(
                name=name, geom=geom, bbox=bbox, area=area, attr_data=attr_data
            )
    elif file_type == "province":
        for index, row in gdf.iterrows():
            attr_data = row.drop(["geometry"]).to_dict()
            name = attr_data.pop("Name")
            geom = GEOSGeometry(str(row["geometry"]))
            bbox = list(row["geometry"].bounds)
            area_gdf = gpd.GeoDataFrame(geometry=[row["geometry"]], crs=gdf.crs)
            area_gdf.to_crs(epsg=3857, inplace=True)
            area = area_gdf.area.iloc[0] / 1000000
            ProvinceGeometry.objects.create(
                name=name, geom=geom, bbox=bbox, area=area, attr_data=attr_data
            )
    return "success"
