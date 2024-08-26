# tasks.py
import os
import shutil
import glob
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from .models import (
    Road,
    RoadUpload,
    Building,
    BuildingUpload,
    RoadGeometry,
    BuildingGeometry,
    VectorLayer,
    FeatureCollection,
    RasterLayer,
    RasterLayerMetadata,
    VectorLayerStyle,
)
from api.utils.file_handlers import (
    road_handle_shapefile,
    road_handle_csv,
    road_handle_geojson,
    building_handle_csv,
    building_handle_geojson,
    building_handle_shapefile,
    handle_vector_layer,
)
import zipfile
from django.conf import settings
from core.raster.raster_tiler import generate_raster_tiles
from core.raster.generate_tiles import metadata_generator, sld2colormap
from api.serializers.core_serializers import RoadPostSerializer, BuildingPostSerializer
from core.script import house_numbering

dir = f"{settings.MEDIA_ROOT}/Files/"
if not os.path.exists(dir):
    os.makedirs(dir)


def vector_style(geometry_type):
    if geometry_type == "Point":
        return {"circle-color": "#FF0000", "circle-radius": 5}
    elif geometry_type == "LineString":
        return {"line-color": "#FF0000", "line-width": 5, "line-opacity": 1}
    elif geometry_type == "Polygon":
        return {
            "fill-color": "#FF0000",
            "fill-opacity": 1,
            "fill-outline-color": "#000000",
        }
    else:
        return {}


def update_layer_fields(layer, geometry_type, bound_dict, layer_type):
    layer.geometry_type = geometry_type
    layer.bbox = bound_dict
    layer.file_type = layer_type
    style = vector_style(geometry_type)
    VectorLayerStyle.objects.create(layer=layer, style_json=style)
    layer.save()


@shared_task
def process_road_file(
    file_id,
    user_id,
):
    layer = RoadUpload.objects.get(id=file_id)
    file = str(layer.file_upload.path)
    split_tup = os.path.splitext(file)
    file_extension = split_tup[1]
    road_file_id = layer.id
    uploaded_file = layer.file_upload
    try:
        if file_extension.lower() == ".zip":
            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(dir)
            shape_files = glob.glob(f"{dir}/**/*.shp", recursive=True)
            if shape_files:
                try:
                    shapefile = file
                    try:
                        geometry_type, bound_dict = road_handle_shapefile(
                            shapefile,
                            Road,
                            RoadGeometry,
                            user_id,
                        )
                        return update_layer_fields(
                            layer, geometry_type, bound_dict, "Shapefile"
                        )
                    except Exception as e:
                        return str(e)
                except FileNotFoundError:
                    raise FileNotFoundError(
                        data={"message": "Shapefile not found in the uploaded ZIP file"}
                    )
        elif file_extension.lower() == ".csv":
            try:
                geometry_type, bound_dict = road_handle_csv(
                    uploaded_file,
                    Road,
                    RoadGeometry,
                    user_id,
                )
                return update_layer_fields(layer, geometry_type, bound_dict, "CSV")
            except Exception as e:
                return str(e)

        elif file_extension.lower() == ".geojson":
            try:
                geometry_type, bound_dict = road_handle_geojson(
                    uploaded_file,
                    Road,
                    RoadGeometry,
                    user_id,
                )
                return update_layer_fields(layer, geometry_type, bound_dict, "Geojson")
            except Exception as e:
                return str(e)

        serializer_post = RoadPostSerializer(layer)
        serializer_post.data["bbox"] = layer.bbox
        serializer_post.data["geometry_type"] = layer.geometry_type

        """clearing the directory"""
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        return Response(
            data={
                "message": "RoadLayer created successfully",
                "data": serializer_post.data,
            },
            status=status.HTTP_201_CREATED,
        )
    except ObjectDoesNotExist:
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        Road.objects.get(id=road_file_id).delete()
        return Response(
            data={"message": "RoadLayer does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )


@shared_task
def process_building_file(file_id, user_id):
    layer = BuildingUpload.objects.get(id=file_id)
    file = str(layer.file_upload.path)
    split_tup = os.path.splitext(file)
    file_extension = split_tup[1]
    building_id = layer.id
    uploaded_file = layer.file_upload
    try:
        if file_extension.lower() == ".zip":
            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(dir)
            shape_files = glob.glob(f"{dir}/**/*.shp", recursive=True)
            if shape_files:
                try:
                    shapefile = file
                    try:
                        geometry_type = None
                        bound_dict = None
                        error_message = None

                        geometry_type,
                        bound_dict,
                        error_message = building_handle_shapefile(
                            shapefile,
                            Building,
                            BuildingGeometry,
                            user_id,
                        )
                        if error_message:
                            return None, "success", error_message, 200
                        # elif error_message is not None:
                        #     return None, "error", error_message, 400
                        else:
                            return update_layer_fields(
                                layer, geometry_type, bound_dict, "Shapefile"
                            )

                    except Exception as e:
                        return str(e)
                except FileNotFoundError:
                    raise FileNotFoundError(
                        data={"message": "Shapefile not found in the uploaded ZIP file"}
                    )
        elif file_extension.lower() == ".csv":
            try:
                geometry_type, bound_dict = building_handle_csv(
                    uploaded_file,
                    Building,
                    BuildingGeometry,
                    user_id,
                )
                return update_layer_fields(layer, geometry_type, bound_dict, "CSV")
            except Exception as e:
                return str(e)

        elif file_extension.lower() == ".geojson":
            try:
                geometry_type, bound_dict = building_handle_geojson(
                    uploaded_file,
                    Building,
                    BuildingGeometry,
                    user_id,
                )
                return update_layer_fields(layer, geometry_type, bound_dict, "Geojson")
            except Exception as e:
                return str(e)

        serializer_post = BuildingPostSerializer(layer)
        serializer_post.data["bbox"] = layer.bbox
        serializer_post.data["geometry_type"] = layer.geometry_type

        """clearing the directory"""
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        return Response(
            data={
                "message": "BuildingLayer created successfully",
                "data": serializer_post.data,
            },
            status=status.HTTP_201_CREATED,
        )
    except ObjectDoesNotExist:
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        Building.objects.get(id=building_id).delete()
        return Response(
            data={"message": "BuildingLayer does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )


@shared_task
def process_vector_layer(vector_layer_id, user_id):
    layer = VectorLayer.objects.get(id=vector_layer_id)
    file = str(layer.file_upload.path)
    split_tup = os.path.splitext(file)
    file_extension = split_tup[1]
    try:
        if file_extension.lower() == ".zip":
            with zipfile.ZipFile(file, "r") as zip_ref:
                zip_ref.extractall(dir)
            shape_files = glob.glob(f"{dir}/**/*.shp", recursive=True)
            if shape_files:
                try:
                    shapefile = file
                    try:
                        geometry_type, bound_dict = handle_vector_layer(
                            shapefile,
                            vector_layer_id,
                            user_id,
                            FeatureCollection,
                        )
                        return update_layer_fields(
                            layer, geometry_type, bound_dict, "Shapefile"
                        )
                    except Exception as e:
                        return str(e)
                except FileNotFoundError:
                    raise FileNotFoundError(
                        data={"message": "Shapefile not found in the uploaded ZIP file"}
                    )
        else:
            raise FileNotFoundError(data={"message": "Only .zip files are supported"})

        serializer_post = BuildingPostSerializer(layer)
        serializer_post.data["bbox"] = layer.bbox
        serializer_post.data["geometry_type"] = layer.geometry_type

        """clearing the directory"""
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        return Response(
            data={
                "message": "VectorLayer created successfully",
                "data": serializer_post.data,
            },
            status=status.HTTP_201_CREATED,
        )
    except ObjectDoesNotExist:
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        VectorLayer.objects.get(id=vector_layer_id).delete()
        return Response(
            data={"message": "VectorLayer does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )


@shared_task
def get_raster_tile(raster_id, file, output_folder, zoom):
    raster_instance = RasterLayer.objects.get(id=raster_id)
    with zipfile.ZipFile(file, "r") as zipf:
        for file_name in zipf.namelist():
            if file_name.endswith(".tif"):
                rasterfile_name = file_name
    raster_file = f"/vsizip/{file}/{rasterfile_name}"
    metas = metadata_generator(raster_file)
    if metas is not None:
        rastermeta = RasterLayerMetadata.objects.create(
            rasterlayer=raster_instance, file_name=rasterfile_name, **metas
        )
    if metas["extent"] is not None:
        raster_instance.bbox = metas["extent"]
        raster_instance.save()
    options = {"zoom": zoom} if zoom is not None else {}
    if raster_instance.sld_file:
        colormap = sld2colormap(raster_instance.sld_file.read())
    else:
        colormap = None
    legend, stats = generate_raster_tiles(
        raster_file, rasterfile_name, colormap, output_folder, **options
    )
    if legend and stats is not None:
        rastermeta.legend = legend
        rastermeta.stats = stats
        rastermeta.save()
    raster_instance.status = "completed"
    raster_instance.save()
    return (
        raster_id,
        "success",
        "Raster Tile generated Sucessfully",
        status.HTTP_200_OK,
    )


@shared_task(bind=True)
def generate_house_numbers_task(self, data_id=None):
    try:
        if data_id is None:
            all_data_ids = Building.objects.values_list("id", flat=True)
            for data_id in all_data_ids:
                house_numbering(data_id)
                self.update_state(
                    state="PROGRESS",
                    meta={"current": data_id, "total": len(all_data_ids)},
                )

            count_with_house_no = Building.objects.filter(
                house_no__isnull=False
            ).count()

            response_dt = {
                "stat": "success",
                "count": count_with_house_no,
            }

            return {
                "message": "House numbers generated for all data IDs",
                "data": response_dt,
                "code": 200,
            }
        else:
            house = Building.objects.get(id=data_id)
            # If a specific data_id is provided
            house_numbering(data_id)

            response_dt = {
                "stat": "success",
                "house_id": house.id,
                "house_no": house.house_no,
            }

            return {
                "message": f"House numbers generated for data_id {data_id}",
                "data": response_dt,
                "code": 200,
            }

    except Exception as e:
        return {
            "stat": "error",
            "message": str(e),
        }
