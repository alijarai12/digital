import geopandas
import math
import os
import pyproj
import shapely
import shapely.wkt

from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F
from shapely.geometry import Point
from sqlalchemy import create_engine

from core.models import Building, Road
from api.utils.file_handlers import calculate_and_save_geometry


db_connection_url = f"postgresql://{os.environ.get('POSTGRES_USER', '')}:{os.environ.get('POSTGRES_PASSWORD', '')}@{os.environ.get('POSTGRES_HOST', 'localhost')}:{os.environ.get('POSTGRES_PORT', '5432')}/{os.environ.get('POSTGRES_DB', 'postgres')}"
con = create_engine(db_connection_url)
proj = pyproj.Transformer.from_crs(4326, 32645, always_xy=True)


def get_road_start_point(road):
    """
    Function to get start point of road with epsg:4326
    """
    start_point = None
    if road.feature.geom.geom_type == "MultiLineString":
        # first = road.geom[0].coords[0]
        # start_point = Point(first[0], first[1])
        start_point, end_point, road_length = calculate_and_save_geometry(road)
        start_point = Point(start_point)
    else:
        first = road.feature.geom.coords[0]
        start_point = Point(first[0], first[1])
    return start_point


def get_start_point(road_geom_proj):
    """
    Function to get start point of road with epsg:32645
    """
    start_point = None
    if road_geom_proj.geom_type == "MultiLineString":
        first = road_geom_proj[0].coords[0]
        start_point = Point(first[0], first[1])
    else:
        first = road_geom_proj.coords[0]
        start_point = Point(first[0], first[1])
    return start_point


def check_gate_proximity(gate_lat, gate_lon):
    gate_loc = Point(gate_lon, gate_lat, srid=4326)
    gate_loc_projected = gate_loc.transform(32645, clone=True)
    gate_loc_buffer = gate_loc_projected.buffer(2)
    metric_house_layer_id = Building.objects.filter(
        feature__geom__intersects=gate_loc_buffer
    ).values_list("id", flat=True)
    if len(metric_house_layer_id) > 0:
        return "fail"
    else:
        return "pass"


def get_direction(gate_location, road_geom_proj):
    """
    function get direction of house gate with respect to road
    """
    # first, last = road.geom.boundary
    # first = get_start_point(road_geom_proj)
    dist_gate = road_geom_proj.project(gate_location)
    ip = road_geom_proj.interpolate(dist_gate)
    near_dist_gate = dist_gate - 1 if (dist_gate - 1) > 0 else 0.0
    prev_ip = road_geom_proj.interpolate(near_dist_gate)
    # prev_ip= nearest_points(road_geom_proj, gate_location)[0] #similar to project and interpolate so yields same point most of the time.
    azimuthA = math.atan2(ip.x - gate_location.x, ip.y - gate_location.y)
    azimuthB = math.atan2(ip.x - prev_ip.x, ip.y - prev_ip.y)
    if (azimuthA > azimuthB) and ((azimuthA - azimuthB) < math.pi):
        return "Left"
    elif (azimuthB > azimuthA) and ((azimuthB - azimuthA) < math.pi):
        return "Right"
    elif (azimuthA > azimuthB) and ((azimuthA - azimuthB) > math.pi):
        return "Right"
    else:
        return "Left"


def RightDirRound(distance):
    """
    Function to round off the metric distance of the house which is at right direction with respect to road
    """
    if distance == 0:
        return distance
    else:
        answer = round(distance)
        if not answer % 2:
            return answer
        if abs(answer + 1 - distance) < abs(answer - 1 - distance):
            return answer + 1
        else:
            return answer - 1


def LeftDirRound(distance):
    """
    Function to round off the metric distance of the house which is at left direction with respect to road
    """
    if distance == 0:
        return distance
    else:
        answer = round(distance)
        if answer % 2:
            return answer
        if abs(answer + 1 - distance) > abs(answer - 1 - distance):
            return answer + 1
        else:
            return answer - 1


def getIntersectedRoad(road, start_point, exid):
    # def getIntersectedRoad(start_point, exid, metric_road_qs, road_gdf):
    """
    Function to get nearest connected road of subsidiary road
    """
    d = 5
    connected_road_id = None
    main_road = False
    minor_road = False
    initial_buffer_radius = 5
    max_attempts = 3
    expanded_buffer_increment = 5

    for attempt in range(max_attempts):
        buffer_radius = initial_buffer_radius + attempt * expanded_buffer_increment
        buffer = start_point.buffer(buffer_radius)

        road_intersect_sql = f"""
            SELECT r.id, r.road_category, r.road_id,
                ST_GeomFromWKB(ST_Transform(rg.geom, 32645)) as geom
            FROM core_road AS r
            JOIN core_roadgeometry AS rg ON r.feature_id = rg.id
            WHERE ST_Intersects(ST_Transform(rg.geom, 32645), ST_SetSRID(ST_GeomFromText('SRID=32645;{buffer}'), 32645))
            AND r.road_id != {exid}
            """

        road_intersect_gdf = geopandas.GeoDataFrame.from_postgis(
            road_intersect_sql, con
        )

        if not road_intersect_gdf.empty:
            break

    for index, row in road_intersect_gdf.iterrows():
        dist = start_point.distance(row["geom"])
        road_type = row["road_category"]
        if road_type == "major":
            if main_road == False:
                main_road = True
                d = dist
                connected_road_id = row["road_id"]
            elif dist < d:
                d = dist
                connected_road_id = row["road_id"]
        if road_type == "minor":
            if main_road == False and minor_road == False:
                d = dist
                connected_road_id = row["road_id"]
                minor_road = True
            elif dist < d:
                d = dist
                connected_road_id = row["road_id"]
        if road_type == "subsidiary":
            if main_road == False and minor_road == False:
                d = dist
                connected_road_id = row["road_id"]
            elif dist < d:
                d = dist
                connected_road_id = row["road_id"]
    return connected_road_id


def get_distance(road, metric_road_qs):
    """
    Function to get metric house number
    """
    road_type = road.road_category
    if road_type == "major" or road_type == "minor":
        return ""
    else:
        instance = road.feature.geom
        converted_geometry = instance.transform(32645, clone=True)

        if converted_geometry.geom_type == "MultiLineString":
            road_geom_proj = shapely.geometry.MultiLineString(
                shapely.wkt.loads(converted_geometry.wkt)
            )
        elif converted_geometry.geom_type == "LineString":
            road_geom_proj = shapely.geometry.LineString(
                shapely.wkt.loads(converted_geometry.wkt)
            )
        pt = road_geom_proj.centroid

        road_start_point = get_road_start_point(road)
        first_x2, first_y2 = proj.transform(
            road_start_point.coords[0][0], road_start_point.coords[0][1]
        )
        start_point = Point(first_x2, first_y2)
        exid = road.road_id
        aid = getIntersectedRoad(road, start_point, exid)
        connected_road_qs = metric_road_qs.filter(road_id=aid)
        for road1 in connected_road_qs:
            if road1.road_id == aid:
                instance = road1.feature.geom

                converted_geometry = instance.transform(32645, clone=True)

                if converted_geometry.geom_type == "MultiLineString":
                    road_geom_proj1 = shapely.geometry.MultiLineString(
                        shapely.wkt.loads(converted_geometry.wkt)
                    )
                elif converted_geometry.geom_type == "LineString":
                    road_geom_proj1 = shapely.geometry.LineString(
                        shapely.wkt.loads(converted_geometry.wkt)
                    )
                dist = road_geom_proj1.project(start_point)
                direction = get_direction(pt, road_geom_proj1)

                dist = (
                    LeftDirRound(dist) if direction == "Left" else RightDirRound(dist)
                )
                return get_distance(road1, metric_road_qs) + "/" + str(dist)
        print(
            f"error from get_distance: Not found connected road of road_id : {road.road_id}"
        )
        return "/none"


def get_road_ids(road, metric_road_qs, max_interation=5):
    """
    Regarding the exid and aid variables, these are used to find the nearest connected road of
    a subsidiary road (in getIntersectedRoad function) and to determine the distance of the house
      from the main road (in get_distance function). The exid variable represents the road ID of
      the current road being processed, and the aid variable represents the ID of the nearest
    connected road. may be
    """
    if max_interation <= 1:
        return "/none"
    association_type = road.road_category
    if association_type == "major" or association_type == "minor":
        return ""

    else:
        road_start_point = get_road_start_point(road)
        first_x2, first_y2 = proj.transform(
            road_start_point.coords[0][0], road_start_point.coords[0][1]
        )

        start_point = Point(first_x2, first_y2)
        exid = road.road_id

        aid = getIntersectedRoad(road, start_point, exid)
        connected_road_qs = metric_road_qs.filter(road_id=aid)
        for road1 in connected_road_qs:
            if road1.road_id == aid:
                ids = str(road1.road_id)
                result = (
                    get_road_ids(road1, metric_road_qs, max_interation - 1) + "/" + ids
                )
                return (
                    get_road_ids(road1, metric_road_qs, max_interation - 1) + "/" + ids
                )
        print(
            f"error from get_road_ids : Not found connected road of road_id: {road.road_id}"
        )
        return "/none"


def association_house_numbering(association, data_id, metric_house_qs):
    try:
        if data_id:
            filter_dict = {}

            house = Building.objects.get(id=data_id)
            filter_dict["building_id"] = house.main_building_id
            main_house = metric_house_qs.filter(**filter_dict)
            if main_house.exists():
                main_house = main_house[0]
            else:
                return

            main_house_num = main_house.house_no if main_house else None
            # main_house_road_ids = main_house.road_id if main_house else None
            if main_house_num and association == "associate":
                house.house_no = main_house_num
                # house.road_id = main_house_road_ids
                house.metric_address = main_house.metric_address
                house.road_id = main_house.road_id
                # road_inst = Road.objects.get(road_id=house.road_id)
                house.associate_road_name = main_house.associate_road_name
                house.road_width = main_house.road_width
                house.road_type = main_house.road_type
                house.road_lane = main_house.road_lane
                house.direction = main_house.direction
                house.tole_name = main_house.tole_name
                house.owner_name = main_house.owner_name
                house.save()
                print(
                    f"\t\tbuilding_id: {house.building_id} \thnum: {main_house_num} \tdata_id: {data_id} \thouse id: {house.id} \tmetric_address: {house.metric_address}\n"
                )

            elif main_house_num and association == "dissociate":
                ass_filter_dict = {}
                ass_filter_dict["association_type"] = association
                ass_filter_dict["building_id"] = house.main_building_id
                house_qs = metric_house_qs.filter(**ass_filter_dict)
                ass_num_list = []
                for qs in house_qs:
                    house_number = qs.house_no
                    if qs.house_no:
                        ass_num_list.append(house_number[-1])
                ass_num_list.sort()
                # work only for dissociate
                num = ord(ass_num_list[-1]) + 1 if ass_num_list else ord("A")
                # if main_house_num:
                house_number_final = str(main_house_num) + "/" + chr(num)
                house.house_no = house_number_final
                # house.road_ids = main_house_road_ids
                house.metric_address = main_house.metric_address
                house.road_id = main_house.road_id
                # road_inst = Road.objects.get(road_id=house.road_id)
                house.associate_road_name = main_house.associate_road_name
                house.road_width = main_house.road_width
                house.road_type = main_house.road_type
                house.road_lane = main_house.road_lane
                house.direction = main_house.direction
                house.tole_name = main_house.tole_name
                house.save()
                print(
                    f"\t\tbuilding_id: {house.building_id} \thnum: {house_number_final} \tdata_id: {data_id} \thouse id: {house.id} \tmetric_address: {house.metric_address} \n"
                )
        else:
            ass_filter_dict = {}
            ass_filter_dict["association_type"] = association
            house_qs = metric_house_qs.filter(**ass_filter_dict)
            main_building_ids = []
            for data in house_qs:
                building_id = data.main_building_id
                if not building_id in main_building_ids:
                    main_building_ids.append(building_id)
            for main_id in main_building_ids:
                filter_dict = {}
                key = "building_id"
                filter_dict[key] = main_id
                try:
                    main_house = metric_house_qs.get(**filter_dict)
                    main_house_num = main_house.house_no if main_house else None
                    # main_house_road_ids = main_house.road_ids if main_house else None
                    filter_dict = {}
                    filtered_qs = house_qs.filter(main_building_id=main_id)
                    if main_house_num and association == "associate":
                        for house in filtered_qs:
                            if not house.house_no:
                                house.house_no = main_house_num
                                # house.road_ids = main_house_road_ids
                                house.road_id = main_house.road_id
                                house.direction = main_house.direction
                                house.metric_address = main_house.metric_address
                                house.tole_name = main_house.tole_name
                                house.save()
                                print(
                                    f"\t\tbuilding_id: {house.id} \thnum: {house_number_final} \tdata_id: {data_id} \thouse id: {house.id} \tmetric_address: {house.metric_address} \n"
                                )
                    elif main_house_num and association == "dissociate":
                        num = ord("A")
                        for house in filtered_qs:
                            if not house.house_no:
                                house_number_final = (
                                    str(main_house_num) + "/" + chr(num)
                                )
                                house.house_no = house_number_final
                                # house.road_ids = main_house_road_ids
                                house.road_id = main_house.road_id
                                house.direction = main_house.direction
                                house.metric_address = main_house.metric_address
                                house.tole_name = main_house.tole_name
                                house.save()
                                print(
                                    f"\t\tbuilding_id: {house.id} \thnum: {house_number_final} \tdata_id: {data_id} \thouse id: {house.id} \tmetric_address: {house.metric_address} \n"
                                )
                                num = num + 1
                except:
                    error_building_id_list = []
                    error_qs = house_qs.filter(main_building_id=main_id)
                    error_building_id_list += [house.building_id for house in error_qs]
                    print(
                        f"main_building_id: {main_id} not found and building_ids={error_building_id_list}"
                    )
    except Exception as e:
        print("error in association_house_numbering: " + str(e))


def get_metric_address(road_ids, metric_road_qs):
    road_address = None
    if road_ids:
        road_ids = road_ids.split("/")
        road = metric_road_qs.filter(road_id=road_ids[0])
        if road.exists():
            road_address = road[0].road_name_en
    return road_address


def main_house_address_generator(house, road_inst, metric_road_qs):
    # polygon_wkt = house.feature.geom
    # polygon = GEOSGeometry(polygon_wkt)

    # centroid = polygon.centroid
    centroid = GEOSGeometry(house.centroid)
    ref_centroid = GEOSGeometry(house.ref_centroid)

    new_srid = 32645
    centroid_meters = centroid.transform(new_srid, clone=True)
    ref_centroid_meters = ref_centroid.transform(new_srid, clone=True)

    distance_m = Distance(F("centroid"), ref_centroid)
    distance_meters = centroid_meters.distance(ref_centroid_meters)

    if distance_meters > 10:
        raise Exception("ref_centroid is more than 10m away from centroid")

    ref_centroid_x, ref_centroid_y = ref_centroid

    try:
        gate_lat = ref_centroid_x
        gate_lon = ref_centroid_y

        x2, y2 = proj.transform(gate_lat, gate_lon)
        gate_location = Point(x2, y2)

        instance = road_inst.feature.geom
        converted_geometry = instance.transform(32645, clone=True)

        if converted_geometry.geom_type == "MultiLineString":
            road_geom_proj = shapely.geometry.MultiLineString(
                shapely.wkt.loads(converted_geometry.wkt)
            )

        elif converted_geometry.geom_type == "LineString":
            road_geom_proj = shapely.geometry.LineString(
                shapely.wkt.loads(converted_geometry.wkt)
            )

        """house to nearest road distance"""
        house_road_dist = road_geom_proj.project(gate_location)

        """get road ids"""
        road_ids = (
            str(get_road_ids(road_inst, metric_road_qs, max_interation=5))
            + "/"
            + str(road_inst.road_id)
        )
        # removing initial slash
        road_ids = road_ids[1:] if road_ids else None
        road_ids_list = road_ids.split("/")
        if road_ids_list[0] == "none":
            print(f"Geometry error for data_id={house.id}")
            return
        """get direction of road with respect to road"""
        direction = get_direction(gate_location, road_geom_proj)

        relevant_houses = Building.objects.filter(association_type="main")
        existing_house_nums = set(relevant_houses.values_list("house_no", flat=True))

        # Determine the increment based on direction
        increment = 1 if direction == "Left" else 2

        if house_road_dist == 0.0:
            house_num = increment
        else:
            house_num = (
                LeftDirRound(house_road_dist)
                if direction == "Left"
                else RightDirRound(house_road_dist)
            )

        # Ensure unique house_num
        while house_num in existing_house_nums:
            house_num += increment

        """get final house number"""
        house_num_final = (
            str(get_distance(road_inst, metric_road_qs)) + "/" + str(house_num)
        )
        if road_inst.road_category == "subsidiary":
            associate_road_name = get_metric_address(road_ids, metric_road_qs)
            house.associate_road_name = associate_road_name
        else:
            house.associate_road_name = road_inst.road_name_en
        house_num_final = house_num_final[1:] if house_num_final else None
        metric_address = get_metric_address(road_ids, metric_road_qs)
        house.road_ids = road_ids
        house.metric_address = metric_address
        house.house_no = house_num_final
        house.direction = direction
        house.save()
        print(
            f"\t\tbuilding_id: {house.id} \thnum: {house_num_final} \tdata_id: {house.building_id} \thouse id: {house.id} \tmetric_address: {house.metric_address} \n"
        )
    except Exception as e:
        print(
            "error in main house address generator: " + str(e),
            "                     data_id: " + str(house.id),
        )


def house_numbering(data_id):
    try:
        """metric road layer information"""
        metric_road_qs = Road.objects.all()
        """metric house layer informaton"""
        metric_house_qs = Building.objects.all()
        if data_id:
            house = Building.objects.get(id=data_id)
            house_association_type = house.association_type
            try:
                if house_association_type == "main":
                    house_road_id = house.road_id
                    if house_road_id:
                        for road in metric_road_qs:
                            road_id = road.road_id
                            if house_road_id == road_id:
                                road_inst = Road.objects.get(road_id=house_road_id)
                                house.associate_road_name = road_inst.road_name_en
                                main_house_address_generator(
                                    house, road_inst, metric_road_qs
                                )
                                break

                elif house_association_type == "associate":
                    pass
                    association_house_numbering("associate", data_id, metric_house_qs)
                elif house_association_type == "dissociate":
                    association_house_numbering("dissociate", data_id, metric_house_qs)
                else:
                    print(
                        "error: invalid house association type. Only main, associate, or dissociate are valid."
                    )
            except Exception as e:
                print(str(e), "error in specific house_numbering")
        else:
            for house in metric_house_qs:
                house_road_id = house.road_id
                house_association_type = house.association_type
                road_found = False
                try:
                    """House numbering for main building"""
                    if house_association_type == "main":
                        latitude = house.ref_centroid.y
                        longitude = house.ref_centroid.x
                        if not latitude or not longitude or not house.road_id:
                            print(
                                f"data_id:{house.id} building_id:{house.building_id}  error:latitude or longitude or road_id is missing"
                            )

                        for road in metric_road_qs:
                            road_id = road.road_id
                            if house_road_id == road_id:
                                road_found = True
                                road_inst = Road.objects.get(road_id=house_road_id)
                                main_house_address_generator(
                                    house, road_inst, metric_road_qs
                                )
                                break
                        if road_found == False:
                            print(
                                f"Road not found for building id {house.building_id} or data_id {house.id}"
                            )
                    elif (
                        house_association_type == "associate"
                        or house_association_type == "dissociate"
                    ):
                        pass
                except Exception as e:
                    print(str(e), "error in house_numbering")

            association_house_numbering("associate", data_id, metric_house_qs)
            association_house_numbering("dissociate", data_id, metric_house_qs)

    except Exception as e:
        print("error in house_numbering main: ", str(e))
