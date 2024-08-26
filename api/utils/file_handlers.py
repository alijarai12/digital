import geopandas as gpd
import pandas as pd
from django.contrib.gis.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.prototypes.io import wkt_w
from django.db import models
from math import atan2, degrees
from shapely.geometry import Point, LineString, MultiLineString

from core.models import PalikaGeometry, PalikaGeometryFile, PalikaWardGeometry, Road
from core.utils import pluscode
from user.models import User


def handle_road_file(gdf, user_id, road_geometry_model, road_model):
    if any(col.lower() == "id" for col in gdf.columns):
        gdf.drop(
            columns=[col for col in gdf.columns if col.lower() == "id"], inplace=True
        )
    geometry_type = gdf["geometry"].iloc[0].geom_type
    total_bounds = gdf.total_bounds
    bound_dict = {"total_bounds": total_bounds.tolist()}
    user_instance = User.objects.get(id=user_id)

    required_fields = [
        "road_id",
        "road_name",
        # "road_lane",
        "width",
        "road_cat",
        "road_class",
        "road_type",
    ]
    for index, row in gdf.iterrows():
        try:
            attr_data = row.drop(["geometry"]).to_dict()

            attr_data = {
                key: None if pd.isna(value) else value
                for key, value in attr_data.items()
            }

            if "updated_date" in attr_data:
                attr_data["updated_date"] = str(attr_data["updated_date"])

            attr_data_keys = attr_data.keys()

            print("the attribute keys", attr_data_keys)

            missing_keys = [key for key in required_fields if key not in attr_data_keys]
            print("the missing keys", missing_keys)

            if missing_keys:
                raise KeyError(
                    f"The following required keys are missing in 'attr_data': {', '.join(missing_keys)}"
                )
            attr_data = row.drop(["geometry"]).to_dict()
            road_id = attr_data.pop("road_id")
            road_name_en = attr_data.pop("road_name")
            # road_lane = attr_data.pop("road_lane")
            road_width = attr_data.pop("width")
            road_category = attr_data.pop("road_cat")
            road_class = attr_data.pop("road_class")
            road_type = attr_data.pop("road_type")
            geom = GEOSGeometry(str(row["geometry"]))
            wkt = wkt_w(dim=2).write(geom).decode()
            geom = GEOSGeometry(wkt, srid=4326)

            # Handle LineString and MultiLineString geometries
            if geom.geom_type == "LineString":
                line_string = LineString(geom.coords)
                start_point = line_string.coords[0]
                end_point = line_string.coords[-1]
                start_point = GEOSGeometry(Point(start_point).wkt)
                end_point = GEOSGeometry(Point(end_point).wkt)
                geometry = geom.transform(32645, clone=True)
                road_length = geometry.length

            elif geom.geom_type == "MultiLineString":
                multi_line_string = MultiLineString(
                    [LineString(line.coords) for line in geom]
                )
                start_point = multi_line_string.geoms[0].coords[0]
                end_point = multi_line_string.geoms[-1].coords[-1]
                start_point = GEOSGeometry(Point(start_point).wkt)
                end_point = GEOSGeometry(Point(end_point).wkt)
                geometry = geom.transform(32645, clone=True)
                road_length = sum(line.length for line in geometry)

            angle_degrees = degrees(
                atan2(end_point[1] - start_point[1], end_point[0] - start_point[0])
            )
            # Determine the direction based on the angle
            direction = ""
            if 45 <= angle_degrees < 135:
                direction = "north to south"
            elif 135 <= angle_degrees < 225:
                direction = "west to east"
            elif 225 <= angle_degrees < 315:
                direction = "south to north"
            else:
                direction = "east to west"

            wards = PalikaWardGeometry.objects.filter(
                Q(geom__crosses=geom) | Q(geom__contains=geom)
            ).values_list("ward_no", flat=True)
            ward_no = list(wards)
            feature_instance = road_geometry_model.objects.create(geom=geom)
            road_model.objects.create(
                attr_data=attr_data,
                road_id=road_id,
                feature=feature_instance,
                road_name_en=road_name_en,
                # road_lane=road_lane,
                road_class=road_class,
                road_width=road_width,
                road_category=road_category,
                road_type=road_type,
                road_length=road_length,
                direction=direction,
                ward_no=ward_no,
                start_point=start_point,
                end_point=end_point,
                created_by=user_instance,
            )
        except KeyError as key_error:
            print("error:", str(key_error))
            return str(key_error)

        except Exception as e:
            print("error:", str(e))
            return str(e)
    return geometry_type, bound_dict


def road_handle_shapefile(shape, road_model, road_geometry_model, user_id):
    """
    Handle the processing of a shapefile.

    This function reads the shapefile, extracts the geometry type, total bounds, and attribute data from each feature,
    and creates corresponding feature collection instances in the database.

    """
    gdf = gpd.read_file(shape)
    crs = "epsg:4326"
    gdf.crs = crs
    return handle_road_file(gdf, user_id, road_geometry_model, road_model)


def road_handle_geojson(
    shape,
    road_model,
    road_geometry_model,
    user_id,
):
    """
    Handle the processing of a GeoJSON file.

    This function reads the GeoJSON file, extracts the CRS information, total bounds, and attribute data from each feature,
    and creates corresponding feature collection instances in the database.

    """
    gdf = gpd.read_file(shape)
    crs = "epsg:4326"
    gdf.crs = crs
    return handle_road_file(gdf, user_id, road_geometry_model, road_model)


def road_handle_csv(
    shape,
    road_model,
    road_geometry_model,
    user_id,
):
    """
    Handle the processing of a CSV file.

    This function reads the CSV file, creates a GeoDataFrame by converting latitude and longitude columns to geometry,
    extracts the geometry type, total bounds, and attribute data from each row,
    and creates corresponding feature collection instances in the database.

    """
    df = pd.read_csv(shape, keep_default_na=False)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"])
    )
    crs = "epsg:4326"
    gdf = gpd.GeoDataFrame(df, crs=crs)
    gdf.fillna("")
    return handle_road_file(gdf, user_id, road_geometry_model, road_model)


def get_char_fields_max_lengths(model_class):
    char_fields_max_length = {}
    for field in model_class._meta.fields:
        if isinstance(field, models.CharField):
            char_fields_max_length[field.name] = field.max_length
    return char_fields_max_length


def handle_building_file(gdf, user_id, building_geometry_model, building_model):
    if any(col.lower() == "id" for col in gdf.columns):
        gdf.drop(
            columns=[col for col in gdf.columns if col.lower() == "id"], inplace=True
        )
    geometry_type = gdf["geometry"].iloc[0].geom_type
    total_bounds = gdf.total_bounds
    bound_dict = {"total_bounds": total_bounds.tolist()}
    user_instance = User.objects.get(id=user_id)

    required_fields = [
        # "updated_date",
        "house_no",
        "build_id",
        "main_b_id",
        "road_id",
        "structure",
        "ownr_stat",
        "temp_type",
        "reg_type",
        "b_use_cat",
        "owner_name",
        "roof_type",
        "tole_name",
        "floor",
        "b_use_spc",
        "road_type",
        "road_lane",
        "road_wd",
        "road_name",
        "assoc_type",
    ]

    for index, row in gdf.iterrows():
        try:
            attr_data = row.drop(["geometry"]).to_dict()

            attr_data = {
                key: None if pd.isna(value) else value
                for key, value in attr_data.items()
            }

            if "updated_date" in attr_data:
                attr_data["updated_date"] = str(attr_data["updated_date"])

            if "updated_by" in attr_data:
                del attr_data["updated_by"]

            attr_data_keys = attr_data.keys()

            missing_keys = [key for key in required_fields if key not in attr_data_keys]

            if missing_keys:
                # raise KeyError(
                #     f"The following required keys are missing in 'attr_data': {', '.join(missing_keys)}"
                # )
                geometry_type = None
                bound_dict = None
                error_message = f"The following required keys are missing in 'attr_data': {', '.join(missing_keys)}"
                return geometry_type, bound_dict, error_message

            char_fields_max_length = get_char_fields_max_lengths(building_model)

            skipped_fields_info = {}
            for char_field, max_length in char_fields_max_length.items():
                if (
                    char_field in attr_data
                    and len(str(attr_data[char_field])) > max_length
                ):
                    attr_data[char_field] = None

                    # Store skipped field information
                    skipped_fields_info.setdefault(char_field, {"ids": [], "count": 0})
                    skipped_fields_info[char_field]["ids"].append(index)
                    skipped_fields_info[char_field]["count"] += 1

            house_no = attr_data.pop("house_no")
            building_id = attr_data.pop("build_id")
            main_building_id = attr_data.pop("main_b_id")
            road_id = attr_data.pop("road_id")
            if road_id:
                road_inst = Road.objects.get(road_id=road_id)
                associate_road_name = road_inst.road_name_en
            building_structure = attr_data.pop("structure")
            owner_status = attr_data.pop("ownr_stat")
            temporary_type = attr_data.pop("temp_type")
            reg_type = attr_data.pop("reg_type")
            building_use = attr_data.pop("b_use_cat")
            owner_name = attr_data.pop("owner_name")
            roof_type = attr_data.pop("roof_type")
            tole_name = attr_data.pop("tole_name")
            floor = attr_data.pop("floor")
            building_sp_use_raw = attr_data.pop("b_use_spc")
            if pd.notna(building_sp_use_raw):
                building_sp_use = [
                    use.strip() for use in building_sp_use_raw.split(",")
                ]
            else:
                building_sp_use = []
            road_type = attr_data.pop("road_type")
            road_lane = attr_data.pop("road_lane")
            road_width = attr_data.pop("road_wd")
            association_type = attr_data.pop("assoc_type")
            geom = GEOSGeometry(str(row["geometry"]))
            wkt = wkt_w(dim=2).write(geom).decode()
            geom = GEOSGeometry(wkt)
            centroid = geom.centroid
            centroid_lat = centroid.y
            centroid_lon = centroid.x
            ref_centroid = geom.centroid
            plus_code = pluscode.encode(centroid_lat, centroid_lon)
            ward_geometry = PalikaWardGeometry.objects.get(geom__contains=centroid)
            ward_no = ward_geometry.ward_no

            feature_instance = building_geometry_model.objects.create(
                geom=geom, created_by=user_instance
            )
            building_model.objects.create(
                feature=feature_instance,
                house_no=house_no,
                building_id=building_id,
                main_building_id=main_building_id,
                tole_name=tole_name,
                floor=floor,
                centroid=centroid,
                ref_centroid=ref_centroid,
                plus_code=plus_code,
                building_structure=building_structure,
                owner_status=owner_status,
                temporary_type=temporary_type,
                reg_type=reg_type,
                building_use=building_use,
                owner_name=owner_name,
                roof_type=roof_type,
                building_sp_use=building_sp_use,
                road_type=road_type,
                road_lane=road_lane,
                road_width=road_width,
                associate_road_name=associate_road_name,
                association_type=association_type,
                attr_data=attr_data,
                created_by=user_instance,
                road_id=road_id,
                ward_no=ward_no,
            )
        # except KeyError as key_error:
        #     print("error:", str(key_error))
        #     return str(key_error)

        except Exception as e:
            continue

    error_message = ""
    for char_field, info in skipped_fields_info.items():
        error_message += (
            f"Skipped {char_field} for IDs: {info['ids']} (Count: {info['count']})\n"
        )

    return geometry_type, bound_dict, error_message


def building_handle_shapefile(
    shape,
    building_model,
    building_geometry_model,
    user_id,
):
    """
    Handle the processing of a shapefile.

    This function reads the shapefile, extracts the geometry type, total bounds, and attribute data from each feature,
    and creates corresponding feature collection instances in the database..

    """
    gdf = gpd.read_file(shape)
    crs = "epsg:4326"
    gdf.crs = crs
    return handle_building_file(gdf, user_id, building_geometry_model, building_model)


def building_handle_geojson(
    shape,
    building_model,
    building_geometry_model,
    user_id,
):
    """
    Handle the processing of a GeoJSON file.

    This function reads the GeoJSON file, extracts the CRS information, total bounds, and attribute data from each feature,
    and creates corresponding feature collection instances in the database.

    """
    gdf = gpd.read_file(shape)
    crs = "epsg:4326"
    gdf.crs = crs
    return handle_building_file(gdf, user_id, building_geometry_model, building_model)


def building_handle_csv(
    shape,
    building_model,
    building_geometry_model,
    user_id,
):
    """
    Handle the processing of a CSV file.

    This function reads the CSV file, creates a GeoDataFrame by converting latitude and longitude columns to geometry,
    extracts the geometry type, total bounds, and attribute data from each row,
    and creates corresponding feature collection instances in the database.

    """
    df = pd.read_csv(shape, keep_default_na=False)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"])
    )
    crs = "epsg:4326"
    gdf.crs = crs
    gdf.fillna("")
    return handle_building_file(gdf, user_id, building_geometry_model, building_model)


def handlepalikageometryfile(id):
    instance = PalikaGeometryFile.objects.get(id=id)
    file = str(instance.file_upload.path)
    file_type = instance.file_type
    gdf = gpd.read_file(file)
    if file_type == "palika":
        for index, row in gdf.iterrows():
            geom = GEOSGeometry(str(row["geometry"]))
            bbox = list(row["geometry"].bounds)
            area_gdf = gpd.GeoDataFrame(geometry=[row["geometry"]], crs=gdf.crs)
            area_gdf.to_crs(epsg=3857, inplace=True)
            area = area_gdf.area.iloc[0] / 1000000
            PalikaGeometry.objects.create(geom=geom, bbox=bbox, area=area)
    elif file_type == "ward":
        for index, row in gdf.iterrows():
            attr_data = row.drop(["geometry"]).to_dict()
            geom = GEOSGeometry(str(row["geometry"]))
            bbox = list(row["geometry"].bounds)
            area_gdf = gpd.GeoDataFrame(geometry=[row["geometry"]], crs=gdf.crs)
            area_gdf.to_crs(epsg=3857, inplace=True)
            area = area_gdf.area.iloc[0] / 1000000
            PalikaWardGeometry.objects.create(
                geom=geom, ward_no=attr_data["new_ward_n"], bbox=bbox, area=area
            )
    return "success"


def handle_vector_layer(shape, vector_layer_id, user_id, feature_collection_model):
    """
    Handle the processing of a vector layer in shapefile.

    This function reads the shapefile, extracts the geometry type, total bounds, and attribute data from each feature,
    and creates corresponding feature collection instances in the database.

    """
    try:
        gdf = gpd.read_file(shape)
        if any(col.lower() == "id" for col in gdf.columns):
            gdf.drop(
                columns=[col for col in gdf.columns if col.lower() == "id"],
                inplace=True,
            )
        geometry_type = gdf["geometry"].iloc[0].geom_type
        total_bounds = gdf.total_bounds
        bound_dict = {"total_bounds": total_bounds.tolist()}
        user_instance = User.objects.get(id=user_id)
        for index, row in gdf.iterrows():
            dropped_geometry = row.drop(["geometry"])
            geom = GEOSGeometry(str(row["geometry"]))
            wkt = wkt_w(dim=2).write(geom).decode()
            geom = GEOSGeometry(wkt)
            attr_data = dropped_geometry.to_dict()
            feature_collection_model.objects.create(
                vector_layer_id=vector_layer_id,
                attr_data=attr_data,
                geom=geom,
                created_by=user_instance,
            )
        return geometry_type, bound_dict
    except Exception as e:
        return e


def calculate_and_save_geometry(instance):
    """
    Calculate start point, end point, and road length for a given geometry.

    Parameters:
    - instance: An instance containing a 'feature' attribute with a valid geometry (LineString or MultiLineString).

    Returns:
    A tuple containing:
    - start_point: The starting point of the geometry.
    - end_point: The ending point of the geometry.
    - road_length: The length of the geometry after transforming it to SRID 32645.

    Explanation:
    The function handles LineString and MultiLineString geometries differently based on the number of coordinates in the first LineString of a MultiLineString:
    - If len(line_string[0]) > 2, it indicates a MultiLineString geometry.
      The start_point is set as the first coordinate of the first LineString, and the end_point is set as the last coordinate of the last LineString.
    - If len(line_string[0]) <= 2, it suggests LineString geometry.
      The start_point is set as the first coordinate of the first LineString, and the end_point is set as the last coordinate of the last LineString.
    """

    geom = instance.feature.geom
    line_string = geom.coords

    if len(line_string[0]) > 2:
        start_point = line_string[0][0]
        end_point = line_string[-1][-1]

    else:
        start_point = line_string[0]
        end_point = line_string[-1]

    geometry = geom.transform(32645, clone=True)
    road_length = geometry.length

    return start_point, end_point, road_length
