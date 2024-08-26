from __future__ import print_function, division

import math
import os
import tempfile
import shutil
import sys
from uuid import uuid4
from xml.etree import ElementTree

try:
    from billiard import Pipe, Pool, Process, Manager
except ImportError:
    from multiprocessing import Pipe, Pool, Process, Manager

from osgeo import gdal, osr

try:
    from PIL import Image
    import numpy
    import osgeo.gdal_array as gdalarray
except Exception:
    pass
import tempfile
import warnings


class AttrDict(object):
    """
    Helper class to provide attribute like access (read and write) to
    dictionaries. Used to provide a convenient way to access both results and
    nested dsl dicts.
    """

    def __init__(self, d={}):
        # assign the inner dict manually to prevent __setattr__ from firing
        super(AttrDict, self).__setattr__("_d_", d)

    def __contains__(self, key):
        return key in self._d_

    def __nonzero__(self):
        return bool(self._d_)

    __bool__ = __nonzero__

    def __dir__(self):
        # introspection for auto-complete in IPython etc
        return list(self._d_.keys())

    def __eq__(self, other):
        if isinstance(other, AttrDict):
            return other._d_ == self._d_
        # make sure we still equal to a dict with the same data
        return other == self._d_

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        r = repr(self._d_)
        if len(r) > 60:
            r = r[:60] + "...}"
        return r

    def __getstate__(self):
        return (self._d_,)

    def __setstate__(self, state):
        super(AttrDict, self).__setattr__("_d_", state[0])

    def __getattr__(self, attr_name):
        try:
            return self.__getitem__(attr_name)
        except KeyError:
            raise AttributeError(
                "%r object has no attribute %r" % (self.__class__.__name__, attr_name)
            )

    def __delattr__(self, attr_name):
        try:
            del self._d_[attr_name]
        except KeyError:
            raise AttributeError(
                "%r object has no attribute %r" % (self.__class__.__name__, attr_name)
            )

    def __getitem__(self, key):
        return self._d_[key]

    def __setitem__(self, key, value):
        self._d_[key] = value

    def __delitem__(self, key):
        del self._d_[key]

    def __setattr__(self, name, value):
        if name in self._d_ or not hasattr(self.__class__, name):
            self._d_[name] = value
        else:
            # there is an attribute on the class (could be property, ..) - don't add it as field
            super(AttrDict, self).__setattr__(name, value)

    def __iter__(self):
        return iter(self._d_)

    def to_dict(self):
        return self._d_


def recursive_attrdict(obj):
    """
    .. deprecated:: version

    Walks a simple data structure, converting dictionary to AttrDict.
    Supports lists, tuples, and dictionaries.
    """
    warnings.warn("deprecated", DeprecationWarning)
    AttrDict(obj)


MAXZOOMLEVEL = 32

DEFAULT_GDAL2TILES_OPTIONS = {
    "verbose": False,
    "title": "",
    "profile": "mercator",
    "url": "",
    "resampling": "near",
    "s_srs": None,
    "zoom": None,
    "tile_size": 256,
    "resume": False,
    "srcnodata": None,
    "tmscompatible": False,
    "quiet": False,
    "kml": False,
    "webviewer": "all",
    "copyright": "",
    "googlekey": "INSERT_YOUR_KEY_HERE",
    "bingkey": "INSERT_YOUR_KEY_HERE",
    "nb_processes": 1,
}


gdal.UseExceptions()


class GlobalMercator(object):
    def __init__(self, tileSize=256):
        "Initialize the TMS Global Mercator pyramid"
        self.tileSize = tileSize
        self.initialResolution = 2 * math.pi * 6378137 / self.tileSize
        # 156543.03392804062 for tileSize 256 pixels
        self.originShift = 2 * math.pi * 6378137 / 2.0
        # 20037508.342789244

    def LatLonToMeters(self, lat, lon):
        "Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:3857"

        mx = lon * self.originShift / 180.0
        my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)

        my = my * self.originShift / 180.0
        return mx, my

    def MetersToLatLon(self, mx, my):
        "Converts XY point from Spherical Mercator EPSG:3857 to lat/lon in WGS84 Datum"

        lon = (mx / self.originShift) * 180.0
        lat = (my / self.originShift) * 180.0

        lat = (
            180
            / math.pi
            * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
        )
        return lat, lon

    def PixelsToMeters(self, px, py, zoom):
        "Converts pixel coordinates in given zoom level of pyramid to EPSG:3857"

        res = self.Resolution(zoom)
        mx = px * res - self.originShift
        my = py * res - self.originShift
        return mx, my

    def MetersToPixels(self, mx, my, zoom):
        "Converts EPSG:3857 to pyramid pixel coordinates in given zoom level"

        res = self.Resolution(zoom)
        px = (mx + self.originShift) / res
        py = (my + self.originShift) / res
        return px, py

    def PixelsToTile(self, px, py):
        "Returns a tile covering region in given pixel coordinates"

        tx = int(math.ceil(px / float(self.tileSize)) - 1)
        ty = int(math.ceil(py / float(self.tileSize)) - 1)
        return tx, ty

    def PixelsToRaster(self, px, py, zoom):
        "Move the origin of pixel coordinates to top-left corner"

        mapSize = self.tileSize << zoom
        return px, mapSize - py

    def MetersToTile(self, mx, my, zoom):
        "Returns tile for given mercator coordinates"

        px, py = self.MetersToPixels(mx, my, zoom)
        return self.PixelsToTile(px, py)

    def TileBounds(self, tx, ty, zoom):
        "Returns bounds of the given tile in EPSG:3857 coordinates"

        minx, miny = self.PixelsToMeters(tx * self.tileSize, ty * self.tileSize, zoom)
        maxx, maxy = self.PixelsToMeters(
            (tx + 1) * self.tileSize, (ty + 1) * self.tileSize, zoom
        )
        return (minx, miny, maxx, maxy)

    def TileLatLonBounds(self, tx, ty, zoom):
        "Returns bounds of the given tile in latitude/longitude using WGS84 datum"

        bounds = self.TileBounds(tx, ty, zoom)
        minLat, minLon = self.MetersToLatLon(bounds[0], bounds[1])
        maxLat, maxLon = self.MetersToLatLon(bounds[2], bounds[3])

        return (minLat, minLon, maxLat, maxLon)

    def Resolution(self, zoom):
        "Resolution (meters/pixel) for given zoom level (measured at Equator)"

        # return (2 * math.pi * 6378137) / (self.tileSize * 2**zoom)
        return self.initialResolution / (2**zoom)

    def ZoomForPixelSize(self, pixelSize):
        "Maximal scaledown zoom of the pyramid closest to the pixelSize."

        for i in range(MAXZOOMLEVEL):
            if pixelSize > self.Resolution(i):
                if i != -1:
                    return i - 1
                else:
                    return 0  # We don't want to scale up

    def GoogleTile(self, tx, ty, zoom):
        "Converts TMS tile coordinates to Google Tile coordinates"

        # coordinate origin is moved from bottom-left to top-left corner of the extent
        return tx, (2**zoom - 1) - ty

    def QuadTree(self, tx, ty, zoom):
        "Converts TMS tile coordinates to Microsoft QuadTree"

        quadKey = ""
        ty = (2**zoom - 1) - ty
        for i in range(zoom, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (tx & mask) != 0:
                digit += 1
            if (ty & mask) != 0:
                digit += 2
            quadKey += str(digit)

        return quadKey


class GlobalGeodetic(object):
    def __init__(self, tmscompatible, tileSize=256):
        self.tileSize = tileSize
        if tmscompatible is True:
            self.resFact = 180.0 / self.tileSize
        else:
            self.resFact = 360.0 / self.tileSize

    def LonLatToPixels(self, lon, lat, zoom):
        "Converts lon/lat to pixel coordinates in given zoom of the EPSG:4326 pyramid"

        res = self.resFact / 2**zoom
        px = (180 + lon) / res
        py = (90 + lat) / res
        return px, py

    def PixelsToTile(self, px, py):
        "Returns coordinates of the tile covering region in pixel coordinates"

        tx = int(math.ceil(px / float(self.tileSize)) - 1)
        ty = int(math.ceil(py / float(self.tileSize)) - 1)
        return tx, ty

    def LonLatToTile(self, lon, lat, zoom):
        "Returns the tile for zoom which covers given lon/lat coordinates"

        px, py = self.LonLatToPixels(lon, lat, zoom)
        return self.PixelsToTile(px, py)

    def Resolution(self, zoom):
        "Resolution (arc/pixel) for given zoom level (measured at Equator)"

        return self.resFact / 2**zoom

    def ZoomForPixelSize(self, pixelSize):
        "Maximal scaledown zoom of the pyramid closest to the pixelSize."

        for i in range(MAXZOOMLEVEL):
            if pixelSize > self.Resolution(i):
                if i != 0:
                    return i - 1
                else:
                    return 0  # We don't want to scale up

    def TileBounds(self, tx, ty, zoom):
        "Returns bounds of the given tile"
        res = self.resFact / 2**zoom
        return (
            tx * self.tileSize * res - 180,
            ty * self.tileSize * res - 90,
            (tx + 1) * self.tileSize * res - 180,
            (ty + 1) * self.tileSize * res - 90,
        )

    def TileLatLonBounds(self, tx, ty, zoom):
        "Returns bounds of the given tile in the SWNE form"
        b = self.TileBounds(tx, ty, zoom)
        return (b[1], b[0], b[3], b[2])


class Zoomify(object):
    """
    Tiles compatible with the Zoomify viewer
    ----------------------------------------
    """

    def __init__(self, width, height, tilesize=256, tileformat="jpg"):
        """Initialization of the Zoomify tile tree"""

        self.tilesize = tilesize
        self.tileformat = tileformat
        imagesize = (width, height)
        tiles = (math.ceil(width / tilesize), math.ceil(height / tilesize))

        # Size (in tiles) for each tier of pyramid.
        self.tierSizeInTiles = []
        self.tierSizeInTiles.append(tiles)

        # Image size in pixels for each pyramid tierself
        self.tierImageSize = []
        self.tierImageSize.append(imagesize)

        while imagesize[0] > tilesize or imagesize[1] > tilesize:
            imagesize = (math.floor(imagesize[0] / 2), math.floor(imagesize[1] / 2))
            tiles = (
                math.ceil(imagesize[0] / tilesize),
                math.ceil(imagesize[1] / tilesize),
            )
            self.tierSizeInTiles.append(tiles)
            self.tierImageSize.append(imagesize)

        self.tierSizeInTiles.reverse()
        self.tierImageSize.reverse()

        # Depth of the Zoomify pyramid, number of tiers (zoom levels)
        self.numberOfTiers = len(self.tierSizeInTiles)

        # Number of tiles up to the given tier of pyramid.
        self.tileCountUpToTier = []
        self.tileCountUpToTier[0] = 0
        for i in range(1, self.numberOfTiers + 1):
            self.tileCountUpToTier.append(
                self.tierSizeInTiles[i - 1][0] * self.tierSizeInTiles[i - 1][1]
                + self.tileCountUpToTier[i - 1]
            )

    def tilefilename(self, x, y, z):
        """Returns filename for tile with given coordinates"""

        tileIndex = x + y * self.tierSizeInTiles[z][0] + self.tileCountUpToTier[z]
        return os.path.join(
            "TileGroup%.0f" % math.floor(tileIndex / self.tilesize),
            "%s-%s-%s.%s" % (z, x, y, self.tileformat),
        )


class GDALError(Exception):
    pass


def exit_with_error(message, details=""):
    # Message printing and exit code kept from the way it worked using the OptionParser (in case
    # someone parses the error output)
    sys.stderr.write("Usage: gdal2tiles.py [options] input_file [output]\n\n")
    sys.stderr.write("gdal2tiles.py: error: %s\n" % message)
    if details:
        sys.stderr.write("\n\n%s\n" % details)

    sys.exit(2)


def scale_query_to_tile(dsquery, dstile, tiledriver, options, tilefilename=""):
    """Scales down query dataset to the tile dataset"""

    querysize = dsquery.RasterXSize
    tilesize = dstile.RasterXSize
    tilebands = dstile.RasterCount

    if options.resampling == "average":
        # Function: gdal.RegenerateOverview()
        for i in range(1, tilebands + 1):
            # Black border around NODATA
            res = gdal.RegenerateOverview(
                dsquery.GetRasterBand(i), dstile.GetRasterBand(i), "average"
            )
            if res != 0:
                exit_with_error(
                    "RegenerateOverview() failed on %s, error %d" % (tilefilename, res)
                )

    elif options.resampling == "antialias":
        # Scaling by PIL (Python Imaging Library) - improved Lanczos
        array = numpy.zeros((querysize, querysize, tilebands), numpy.uint8)
        for i in range(tilebands):
            array[:, :, i] = gdalarray.BandReadAsArray(
                dsquery.GetRasterBand(i + 1), 0, 0, querysize, querysize
            )
        im = Image.fromarray(array, "RGBA")  # Always four bands
        im1 = im.resize((tilesize, tilesize), Image.ANTIALIAS)
        if os.path.exists(tilefilename):
            im0 = Image.open(tilefilename)
            im1 = Image.composite(im1, im0, im1)
        im1.save(tilefilename, tiledriver)

    else:
        if options.resampling == "near":
            gdal_resampling = gdal.GRA_NearestNeighbour

        elif options.resampling == "bilinear":
            gdal_resampling = gdal.GRA_Bilinear

        elif options.resampling == "cubic":
            gdal_resampling = gdal.GRA_Cubic

        elif options.resampling == "cubicspline":
            gdal_resampling = gdal.GRA_CubicSpline

        elif options.resampling == "lanczos":
            gdal_resampling = gdal.GRA_Lanczos

        # Other algorithms are implemented by gdal.ReprojectImage().
        dsquery.SetGeoTransform(
            (
                0.0,
                tilesize / float(querysize),
                0.0,
                0.0,
                0.0,
                tilesize / float(querysize),
            )
        )
        dstile.SetGeoTransform((0.0, 1.0, 0.0, 0.0, 0.0, 1.0))

        res = gdal.ReprojectImage(dsquery, dstile, None, None, gdal_resampling)
        if res != 0:
            exit_with_error(
                "ReprojectImage() failed on %s, error %d" % (tilefilename, res)
            )


def setup_no_data_values(input_dataset, options):
    """
    Extract the NODATA values from the dataset or use the passed arguments as override if any
    """
    in_nodata = []
    if options.srcnodata:
        nds = list(map(float, options.srcnodata.split(",")))
        if len(nds) < input_dataset.RasterCount:
            in_nodata = (nds * input_dataset.RasterCount)[: input_dataset.RasterCount]
        else:
            in_nodata = nds
    else:
        for i in range(1, input_dataset.RasterCount + 1):
            raster_no_data = input_dataset.GetRasterBand(i).GetNoDataValue()
            if raster_no_data is not None:
                in_nodata.append(raster_no_data)

    if options.verbose:
        print("NODATA: %s" % in_nodata)

    return in_nodata


def setup_input_srs(input_dataset, options):
    """
    Determines and returns the Input Spatial Reference System (SRS) as an osr object and as a
    WKT representation

    Uses in priority the one passed in the command line arguments. If None, tries to extract them
    from the input dataset
    """

    input_srs = None
    input_srs_wkt = None

    if options.s_srs:
        input_srs = osr.SpatialReference()
        input_srs.SetFromUserInput(options.s_srs)
        input_srs_wkt = input_srs.ExportToWkt()
    else:
        input_srs_wkt = input_dataset.GetProjection()
        if not input_srs_wkt and input_dataset.GetGCPCount() != 0:
            input_srs_wkt = input_dataset.GetGCPProjection()
        if input_srs_wkt:
            input_srs = osr.SpatialReference()
            input_srs.ImportFromWkt(input_srs_wkt)

    return input_srs, input_srs_wkt


def setup_output_srs(input_srs, options):
    """
    Setup the desired SRS (based on options)
    """
    output_srs = osr.SpatialReference()

    if options.profile == "mercator":
        output_srs.ImportFromEPSG(3857)
    elif options.profile == "geodetic":
        output_srs.ImportFromEPSG(4326)
    else:
        output_srs = input_srs

    return output_srs


def has_georeference(dataset):
    return (
        dataset.GetGeoTransform() != (0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        or dataset.GetGCPCount() != 0
    )


def reproject_dataset(from_dataset, from_srs, to_srs, options=None):
    """
    Returns the input dataset in the expected "destination" SRS.
    If the dataset is already in the correct SRS, returns it unmodified
    """
    if not from_srs or not to_srs:
        raise GDALError("from and to SRS must be defined to reproject the dataset")

    if (from_srs.ExportToProj4() != to_srs.ExportToProj4()) or (
        from_dataset.GetGCPCount() != 0
    ):
        to_dataset = gdal.AutoCreateWarpedVRT(
            from_dataset, from_srs.ExportToWkt(), to_srs.ExportToWkt()
        )

        if options and options.verbose:
            print(
                "Warping of the raster by AutoCreateWarpedVRT (result saved into 'tiles.vrt')"
            )
            to_dataset.GetDriver().CreateCopy("tiles.vrt", to_dataset)

        return to_dataset
    else:
        return from_dataset


def add_gdal_warp_options_to_string(vrt_string, warp_options):
    if not warp_options:
        return vrt_string

    vrt_root = ElementTree.fromstring(vrt_string)
    options = vrt_root.find("GDALWarpOptions")

    if options is None:
        return vrt_string

    for key, value in warp_options.items():
        tb = ElementTree.TreeBuilder()
        tb.start("Option", {"name": key})
        tb.data(value)
        tb.end("Option")
        elem = tb.close()
        options.insert(0, elem)

    return ElementTree.tostring(vrt_root).decode()


def update_no_data_values(warped_vrt_dataset, nodata_values, options=None):
    """
    Takes an array of NODATA values and forces them on the WarpedVRT file dataset passed
    """
    # TODO: gbataille - Seems that I forgot tests there
    if nodata_values != []:
        temp_file = gettempfilename("-gdal2tiles.vrt")
        warped_vrt_dataset.GetDriver().CreateCopy(temp_file, warped_vrt_dataset)
        with open(temp_file, "r") as f:
            vrt_string = f.read()

        vrt_string = add_gdal_warp_options_to_string(
            vrt_string, {"INIT_DEST": "NO_DATA", "UNIFIED_SRC_NODATA": "YES"}
        )

        # save the corrected VRT
        with open(temp_file, "w") as f:
            f.write(vrt_string)

        corrected_dataset = gdal.Open(temp_file)
        os.unlink(temp_file)

        # set NODATA_VALUE metadata
        corrected_dataset.SetMetadataItem(
            "NODATA_VALUES", " ".join([str(i) for i in nodata_values])
        )

        if options and options.verbose:
            print("Modified warping result saved into 'tiles1.vrt'")
            # TODO: gbataille - test replacing that with a gdal write of the dataset (more
            # accurately what's used, even if should be the same
            with open("tiles1.vrt", "w") as f:
                f.write(vrt_string)

        return corrected_dataset


def add_alpha_band_to_string_vrt(vrt_string):
    # TODO: gbataille - Old code speak of this being equivalent to gdalwarp -dstalpha
    # To be checked

    vrt_root = ElementTree.fromstring(vrt_string)

    index = 0
    nb_bands = 0
    for subelem in list(vrt_root):
        if subelem.tag == "VRTRasterBand":
            nb_bands += 1
            color_node = subelem.find("./ColorInterp")
            if color_node is not None and color_node.text == "Alpha":
                raise Exception("Alpha band already present")
        else:
            if nb_bands:
                # This means that we are one element after the Band definitions
                break

        index += 1

    tb = ElementTree.TreeBuilder()
    tb.start(
        "VRTRasterBand",
        {
            "dataType": "Byte",
            "band": str(nb_bands + 1),
            "subClass": "VRTWarpedRasterBand",
        },
    )
    tb.start("ColorInterp", {})
    tb.data("Alpha")
    tb.end("ColorInterp")
    tb.end("VRTRasterBand")
    elem = tb.close()

    vrt_root.insert(index, elem)

    warp_options = vrt_root.find(".//GDALWarpOptions")
    tb = ElementTree.TreeBuilder()
    tb.start("DstAlphaBand", {})
    tb.data(str(nb_bands + 1))
    tb.end("DstAlphaBand")
    elem = tb.close()
    warp_options.append(elem)

    # TODO: gbataille - this is a GDALWarpOptions. Why put it in a specific place?
    tb = ElementTree.TreeBuilder()
    tb.start("Option", {"name": "INIT_DEST"})
    tb.data("0")
    tb.end("Option")
    elem = tb.close()
    warp_options.append(elem)

    return ElementTree.tostring(vrt_root).decode()


def update_alpha_value_for_non_alpha_inputs(warped_vrt_dataset, options=None):
    """
    Handles dataset with 1 or 3 bands, i.e. without alpha channel, in the case the nodata value has
    not been forced by options
    """
    if warped_vrt_dataset.RasterCount in [1, 3]:
        tempfilename = gettempfilename("-gdal2tiles.vrt")
        warped_vrt_dataset.GetDriver().CreateCopy(tempfilename, warped_vrt_dataset)
        with open(tempfilename) as f:
            orig_data = f.read()
        alpha_data = add_alpha_band_to_string_vrt(orig_data)
        with open(tempfilename, "w") as f:
            f.write(alpha_data)

        warped_vrt_dataset = gdal.Open(tempfilename)
        os.unlink(tempfilename)

        if options and options.verbose:
            print("Modified -dstalpha warping result saved into 'tiles1.vrt'")
            # TODO: gbataille - test replacing that with a gdal write of the dataset (more
            # accurately what's used, even if should be the same
            with open("tiles1.vrt", "w") as f:
                f.write(alpha_data)

    return warped_vrt_dataset


def nb_data_bands(dataset):
    """
    Return the number of data (non-alpha) bands of a gdal dataset
    """
    alphaband = dataset.GetRasterBand(1).GetMaskBand()
    if (
        (alphaband.GetMaskFlags() & gdal.GMF_ALPHA)
        or dataset.RasterCount == 4
        or dataset.RasterCount == 2
    ):
        return dataset.RasterCount - 1
    else:
        return dataset.RasterCount


def gettempfilename(suffix):
    """Returns a temporary filename"""
    if "_" in os.environ:
        # tempfile.mktemp() crashes on some Wine versions (the one of Ubuntu 12.04 particularly)
        if os.environ["_"].find("wine") >= 0:
            tmpdir = "."
            if "TMP" in os.environ:
                tmpdir = os.environ["TMP"]
            import time
            import random

            random.seed(time.time())
            random_part = "file%d" % random.randint(0, 1000000000)
            return os.path.join(tmpdir, random_part + suffix)

    return tempfile.mktemp(suffix)


def create_base_tile(tile_job_info, tile_detail, queue=None):
    gdal.AllRegister()

    dataBandsCount = tile_job_info.nb_data_bands
    output = tile_job_info.output_file_path
    tileext = tile_job_info.tile_extension
    tilesize = tile_job_info.tile_size
    options = tile_job_info.options

    tilebands = dataBandsCount + 1
    ds = gdal.Open(tile_job_info.src_file, gdal.GA_ReadOnly)
    mem_drv = gdal.GetDriverByName("MEM")
    out_drv = gdal.GetDriverByName(tile_job_info.tile_driver)
    alphaband = ds.GetRasterBand(1).GetMaskBand()

    tx = tile_detail.tx
    ty = tile_detail.ty
    tz = tile_detail.tz
    rx = tile_detail.rx
    ry = tile_detail.ry
    rxsize = tile_detail.rxsize
    rysize = tile_detail.rysize
    wx = tile_detail.wx
    wy = tile_detail.wy
    wxsize = tile_detail.wxsize
    wysize = tile_detail.wysize
    querysize = tile_detail.querysize

    # Tile dataset in memory
    tilefilename = os.path.join(output, str(tz), str(tx), "%s.%s" % (ty, tileext))
    os.makedirs(os.path.dirname(tilefilename), exist_ok=True)
    dstile = mem_drv.Create("", tilesize, tilesize, tilebands)

    data = alpha = None

    if rxsize != 0 and rysize != 0 and wxsize != 0 and wysize != 0:
        data = ds.ReadRaster(
            rx,
            ry,
            rxsize,
            rysize,
            wxsize,
            wysize,
            band_list=list(range(1, dataBandsCount + 1)),
        )
        alpha = alphaband.ReadRaster(rx, ry, rxsize, rysize, wxsize, wysize)

    # The tile in memory is a transparent file by default. Write pixel values into it if
    # any
    if data:
        if tilesize == querysize:
            # Use the ReadRaster result directly in tiles ('nearest neighbour' query)
            dstile.WriteRaster(
                wx,
                wy,
                wxsize,
                wysize,
                data,
                band_list=list(range(1, dataBandsCount + 1)),
            )
            dstile.WriteRaster(wx, wy, wxsize, wysize, alpha, band_list=[tilebands])
        else:
            # Big ReadRaster query in memory scaled to the tilesize - all but 'near'
            # algo
            dsquery = mem_drv.Create("", querysize, querysize, tilebands)
            # TODO: fill the null value in case a tile without alpha is produced (now
            # only png tiles are supported)
            dsquery.WriteRaster(
                wx,
                wy,
                wxsize,
                wysize,
                data,
                band_list=list(range(1, dataBandsCount + 1)),
            )
            dsquery.WriteRaster(wx, wy, wxsize, wysize, alpha, band_list=[tilebands])

            scale_query_to_tile(
                dsquery,
                dstile,
                tile_job_info.tile_driver,
                options,
                tilefilename=tilefilename,
            )
            del dsquery

    # Force freeing the memory to make sure the C++ destructor is called and the memory as well as
    # the file locks are released
    del ds
    del data

    if options.resampling != "antialias":
        # Write a copy of tile to png/jpg
        out_drv.CreateCopy(tilefilename, dstile, strict=0)

    del dstile

    if queue:
        queue.put("tile %s %s %s" % (tx, ty, tz))


def create_overview_tiles(tile_job_info, output_folder, options):
    """Generation of the overview tiles (higher in the pyramid) based on existing tiles"""
    mem_driver = gdal.GetDriverByName("MEM")
    tile_driver = tile_job_info.tile_driver
    out_driver = gdal.GetDriverByName(tile_driver)

    tilebands = tile_job_info.nb_data_bands + 1

    # Usage of existing tiles: from 4 underlying tiles generate one as overview.

    tcount = 0
    for tz in range(tile_job_info.tmaxz - 1, tile_job_info.tminz - 1, -1):
        tminx, tminy, tmaxx, tmaxy = tile_job_info.tminmax[tz]
        tcount += (1 + abs(tmaxx - tminx)) * (1 + abs(tmaxy - tminy))

    ti = 0

    if tcount == 0:
        return

    if not options.quiet:
        print("Generating Overview Tiles:")

    progress_bar = ProgressBar(tcount)
    progress_bar.start()

    for tz in range(tile_job_info.tmaxz - 1, tile_job_info.tminz - 1, -1):
        tminx, tminy, tmaxx, tmaxy = tile_job_info.tminmax[tz]
        for ty in range(tmaxy, tminy - 1, -1):
            for tx in range(tminx, tmaxx + 1):
                ti += 1
                tilefilename = os.path.join(
                    output_folder,
                    str(tz),
                    str(tx),
                    "%s.%s" % (ty, tile_job_info.tile_extension),
                )
                os.makedirs(os.path.dirname(tilefilename), exist_ok=True)

                if options.verbose:
                    print(ti, "/", tcount, tilefilename)

                if options.resume and os.path.exists(tilefilename):
                    if options.verbose:
                        print("Tile generation skipped because of --resume")
                    else:
                        progress_bar.log_progress()
                    continue

                dsquery = mem_driver.Create(
                    "",
                    2 * tile_job_info.tile_size,
                    2 * tile_job_info.tile_size,
                    tilebands,
                )
                # TODO: fill the null value
                dstile = mem_driver.Create(
                    "", tile_job_info.tile_size, tile_job_info.tile_size, tilebands
                )

                children = []
                # Read the tiles and write them to query window
                for y in range(2 * ty, 2 * ty + 2):
                    for x in range(2 * tx, 2 * tx + 2):
                        minx, miny, maxx, maxy = tile_job_info.tminmax[tz + 1]
                        if x >= minx and x <= maxx and y >= miny and y <= maxy:
                            dsquerytile = gdal.Open(
                                os.path.join(
                                    output_folder,
                                    str(tz + 1),
                                    str(x),
                                    "%s.%s" % (y, tile_job_info.tile_extension),
                                ),
                                gdal.GA_ReadOnly,
                            )
                            tf_p = None
                            if (ty == 0 and y == 1) or (
                                ty != 0 and (y % (2 * ty)) != 0
                            ):
                                tileposy = 0
                            else:
                                tileposy = tile_job_info.tile_size
                            if tx:
                                tileposx = x % (2 * tx) * tile_job_info.tile_size
                            elif tx == 0 and x == 1:
                                tileposx = tile_job_info.tile_size
                            else:
                                tileposx = 0
                            dsquery.WriteRaster(
                                tileposx,
                                tileposy,
                                tile_job_info.tile_size,
                                tile_job_info.tile_size,
                                dsquerytile.ReadRaster(
                                    0,
                                    0,
                                    tile_job_info.tile_size,
                                    tile_job_info.tile_size,
                                ),
                                band_list=list(range(1, tilebands + 1)),
                            )
                            children.append([x, y, tz + 1])

                scale_query_to_tile(
                    dsquery, dstile, tile_driver, options, tilefilename=tilefilename
                )
                # Write a copy of tile to png/jpg
                if options.resampling != "antialias":
                    # Write a copy of tile to png/jpg
                    out_driver.CreateCopy(tilefilename, dstile, strict=0)

                if not options.verbose and not options.quiet:
                    progress_bar.log_progress()


def process_options(input_file, output_folder, options={}):
    _options = DEFAULT_GDAL2TILES_OPTIONS.copy()
    _options.update(options)
    options = AttrDict(_options)
    options = options_post_processing(options, input_file, output_folder)
    return options


def options_post_processing(options, input_file, output_folder):
    if not options.title:
        options.title = os.path.basename(input_file)

    if options.url and not options.url.endswith("/"):
        options.url += "/"
    if options.url:
        out_path = output_folder
        if out_path.endswith("/"):
            out_path = out_path[:-1]
        options.url += os.path.basename(out_path) + "/"

    if isinstance(options.zoom, (list, tuple)) and len(options.zoom) < 2:
        raise ValueError("Invalid zoom value")

    # Supported options
    if options.resampling == "average":
        try:
            if gdal.RegenerateOverview:
                pass
        except Exception:
            exit_with_error(
                "'average' resampling algorithm is not available.",
                "Please use -r 'near' argument or upgrade to newer version of GDAL.",
            )

    elif options.resampling == "antialias":
        try:
            if numpy:  # pylint:disable=W0125
                pass
        except Exception:
            exit_with_error(
                "'antialias' resampling algorithm is not available.",
                "Install PIL (Python Imaging Library) and numpy.",
            )

    try:
        os.path.basename(input_file).encode("ascii")
    except UnicodeEncodeError:
        full_ascii = False
    else:
        full_ascii = True

    # LC_CTYPE check
    if not full_ascii and "UTF-8" not in os.environ.get("LC_CTYPE", ""):
        if not options.quiet:
            print(
                "\nWARNING: "
                "You are running gdal2tiles.py with a LC_CTYPE environment variable that is "
                "not UTF-8 compatible, and your input file contains non-ascii characters. "
                "The generated sample googlemaps, openlayers or "
                "leaflet files might contain some invalid characters as a result\n"
            )

    return options


class TileDetail(object):
    tx = 0
    ty = 0
    tz = 0
    rx = 0
    ry = 0
    rxsize = 0
    rysize = 0
    wx = 0
    wy = 0
    wxsize = 0
    wysize = 0
    querysize = 0
    filename = ""

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])

    def __unicode__(self):
        return "TileDetail %s\n%s\n%s\n" % (self.tx, self.ty, self.tz)

    def __str__(self):
        return "TileDetail %s\n%s\n%s\n" % (self.tx, self.ty, self.tz)

    def __repr__(self):
        return "TileDetail %s\n%s\n%s\n" % (self.tx, self.ty, self.tz)


class TileJobInfo(object):
    """
    Plain object to hold tile job configuration for a dataset
    """

    src_file = ""
    filename = ""
    nb_data_bands = 0
    output_file_path = ""
    tile_extension = ""
    tile_size = 0
    tile_driver = None
    kml = False
    tminmax = []
    tminz = 0
    tmaxz = 0
    in_srs_wkt = 0
    out_geo_trans = []
    ominy = 0
    is_epsg_4326 = False
    options = None

    def __init__(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])

    def __unicode__(self):
        return "TileJobInfo %s\n" % (self.src_file)

    def __str__(self):
        return "TileJobInfo %s\n" % (self.src_file)

    def __repr__(self):
        return "TileJobInfo %s\n" % (self.src_file)


class Gdal2TilesError(Exception):
    pass


class GDAL2Tiles(object):
    def __init__(self, input_file, filename, output_folder, options):
        """Constructor function - initialization"""
        self.out_drv = None
        self.mem_drv = None
        self.warped_input_dataset = None
        self.out_srs = None
        self.nativezoom = None
        self.tminmax = None
        self.tsize = None
        self.mercator = None
        self.geodetic = None
        self.alphaband = None
        self.dataBandsCount = None
        self.out_gt = None
        self.tileswne = None
        self.swne = None
        self.ominx = None
        self.omaxx = None
        self.omaxy = None
        self.ominy = None

        self.input_file = None
        self.filename = None
        self.output_folder = None

        # Tile format
        self.tilesize = options.tile_size
        self.tiledriver = "PNG"
        self.tileext = "png"
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_vrt_filename = os.path.join(self.tmp_dir, str(uuid4()) + ".vrt")

        self.scaledquery = True
        self.querysize = 4 * self.tilesize
        self.overviewquery = False

        self.input_file = input_file
        self.filename = filename
        self.output_folder = output_folder
        self.options = options

        if self.options.resampling == "near":
            self.querysize = self.tilesize

        elif self.options.resampling == "bilinear":
            self.querysize = self.tilesize * 2

        # User specified zoom levels
        self.tminz = None
        self.tmaxz = None
        if isinstance(self.options.zoom, (list, tuple)):
            self.tminz = self.options.zoom[0]
            self.tmaxz = self.options.zoom[1]
        elif isinstance(self.options.zoom, int):
            self.tminz = self.options.zoom
            self.tmaxz = self.tminz
        elif self.options.zoom:
            minmax = self.options.zoom.split("-", 1)
            minmax.extend([""])
            zoom_min, zoom_max = minmax[:2]
            self.tminz = int(zoom_min)
            if zoom_max:
                self.tmaxz = int(zoom_max)
            else:
                self.tmaxz = int(zoom_min)

        # KML generation
        self.kml = self.options.kml

    # -------------------------------------------------------------------------
    def open_input(self):
        """Initialization of the input raster, reprojection if necessary"""
        gdal.AllRegister()

        self.out_drv = gdal.GetDriverByName(self.tiledriver)
        self.mem_drv = gdal.GetDriverByName("MEM")

        if not self.out_drv:
            raise Exception(
                "The '%s' driver was not found, is it available in this GDAL build?",
                self.tiledriver,
            )
        if not self.mem_drv:
            raise Exception(
                "The 'MEM' driver was not found, is it available in this GDAL build?"
            )

        # Open the input file

        if self.input_file:
            input_dataset = gdal.Open(self.input_file, gdal.GA_ReadOnly)
        else:
            raise Exception("No input file was specified")

        if not input_dataset:
            # Note: GDAL prints the ERROR message too
            exit_with_error(
                "It is not possible to open the input file '%s'." % self.input_file
            )

        # Read metadata from the input file
        if input_dataset.RasterCount == 0:
            exit_with_error("Input file '%s' has no raster band" % self.input_file)

        if input_dataset.GetRasterBand(1).GetRasterColorTable():
            exit_with_error(
                "Please convert this file to RGB/RGBA and run gdal2tiles on the result.",
                "From paletted file you can create RGBA file (temp.vrt) by:\n"
                "gdal_translate -of vrt -expand rgba %s temp.vrt\n"
                "then run:\n"
                "gdal2tiles temp.vrt" % self.input_file,
            )

        in_nodata = setup_no_data_values(input_dataset, self.options)
        in_srs, self.in_srs_wkt = setup_input_srs(input_dataset, self.options)
        self.out_srs = setup_output_srs(in_srs, self.options)

        # If input and output reference systems are different, we reproject the input dataset into
        # the output reference system for easier manipulation

        self.warped_input_dataset = None

        if self.options.profile in ("mercator", "geodetic"):
            if not in_srs:
                exit_with_error(
                    "Input file has unknown SRS.",
                    "Use --s_srs ESPG:xyz (or similar) to provide source reference system.",
                )

            if not has_georeference(input_dataset):
                exit_with_error(
                    "There is no georeference - neither affine transformation (worldfile) "
                    "nor GCPs. You can generate only 'raster' profile tiles.",
                    "Either gdal2tiles with parameter -p 'raster' or use another GIS "
                    "software for georeference e.g. gdal_transform -gcp / -a_ullr / -a_srs",
                )

            if (in_srs.ExportToProj4() != self.out_srs.ExportToProj4()) or (
                input_dataset.GetGCPCount() != 0
            ):
                self.warped_input_dataset = reproject_dataset(
                    input_dataset, in_srs, self.out_srs
                )

                if in_nodata:
                    self.warped_input_dataset = update_no_data_values(
                        self.warped_input_dataset, in_nodata, options=self.options
                    )
                else:
                    self.warped_input_dataset = update_alpha_value_for_non_alpha_inputs(
                        self.warped_input_dataset, options=self.options
                    )

            if self.warped_input_dataset and self.options.verbose:
                print(
                    "Projected file:",
                    "tiles.vrt",
                    "( %sP x %sL - %s bands)"
                    % (
                        self.warped_input_dataset.RasterXSize,
                        self.warped_input_dataset.RasterYSize,
                        self.warped_input_dataset.RasterCount,
                    ),
                )

        if not self.warped_input_dataset:
            self.warped_input_dataset = input_dataset

        self.warped_input_dataset.GetDriver().CreateCopy(
            self.tmp_vrt_filename, self.warped_input_dataset
        )

        # Get alpha band (either directly or from NODATA value)
        self.alphaband = self.warped_input_dataset.GetRasterBand(1).GetMaskBand()
        self.dataBandsCount = nb_data_bands(self.warped_input_dataset)

        # KML test
        self.isepsg4326 = False
        srs4326 = osr.SpatialReference()
        srs4326.ImportFromEPSG(4326)
        if self.out_srs and srs4326.ExportToProj4() == self.out_srs.ExportToProj4():
            self.kml = True
            self.isepsg4326 = True
            if self.options.verbose:
                print("KML autotest OK!")

        # Read the georeference
        self.out_gt = self.warped_input_dataset.GetGeoTransform()

        # Test the size of the pixel
        # Report error in case rotation/skew is in geotransform (possible only in 'raster' profile)
        if (self.out_gt[2], self.out_gt[4]) != (0, 0):
            exit_with_error(
                "Georeference of the raster contains rotation or skew. "
                "Such raster is not supported. Please use gdalwarp first."
            )

        # Here we expect: pixel is square, no rotation on the raster
        # Output Bounds - coordinates in the output SRS
        self.ominx = self.out_gt[0]
        self.omaxx = (
            self.out_gt[0] + self.warped_input_dataset.RasterXSize * self.out_gt[1]
        )
        self.omaxy = self.out_gt[3]
        self.ominy = (
            self.out_gt[3] - self.warped_input_dataset.RasterYSize * self.out_gt[1]
        )
        # Note: maybe round(x, 14) to avoid the gdal_translate behaviour, when 0 becomes -1e-15

        if self.options.verbose:
            print(
                "Bounds (output srs):",
                round(self.ominx, 13),
                self.ominy,
                self.omaxx,
                self.omaxy,
            )

        # Calculating ranges for tiles in different zoom levels
        if self.options.profile == "mercator":
            self.mercator = GlobalMercator(tileSize=self.tilesize)

            # Function which generates SWNE in LatLong for given tile
            self.tileswne = self.mercator.TileLatLonBounds

            # Generate table with min max tile coordinates for all zoomlevels
            self.tminmax = list(range(0, 32))
            for tz in range(0, 32):
                tminx, tminy = self.mercator.MetersToTile(self.ominx, self.ominy, tz)
                tmaxx, tmaxy = self.mercator.MetersToTile(self.omaxx, self.omaxy, tz)
                # crop tiles extending world limits (+-180,+-90)
                tminx, tminy = max(0, tminx), max(0, tminy)
                tmaxx, tmaxy = min(2**tz - 1, tmaxx), min(2**tz - 1, tmaxy)
                self.tminmax[tz] = (tminx, tminy, tmaxx, tmaxy)

            # TODO: Maps crossing 180E (Alaska?)

            # Get the minimal zoom level (map covers area equivalent to one tile)
            if self.tminz is None:
                self.tminz = self.mercator.ZoomForPixelSize(
                    self.out_gt[1]
                    * max(
                        self.warped_input_dataset.RasterXSize,
                        self.warped_input_dataset.RasterYSize,
                    )
                    / float(self.tilesize)
                )

            # Get the maximal zoom level
            # (closest possible zoom level up on the resolution of raster)
            if self.tmaxz is None:
                self.tmaxz = self.mercator.ZoomForPixelSize(self.out_gt[1])

            if self.options.verbose:
                print(
                    "Bounds (latlong):",
                    self.mercator.MetersToLatLon(self.ominx, self.ominy),
                    self.mercator.MetersToLatLon(self.omaxx, self.omaxy),
                )
                print("MinZoomLevel:", self.tminz)

        if self.options.profile == "geodetic":
            self.geodetic = GlobalGeodetic(
                self.options.tmscompatible, tileSize=self.tilesize
            )

            # Function which generates SWNE in LatLong for given tile
            self.tileswne = self.geodetic.TileLatLonBounds

            # Generate table with min max tile coordinates for all zoomlevels
            self.tminmax = list(range(0, 32))
            for tz in range(0, 32):
                tminx, tminy = self.geodetic.LonLatToTile(self.ominx, self.ominy, tz)
                tmaxx, tmaxy = self.geodetic.LonLatToTile(self.omaxx, self.omaxy, tz)
                # crop tiles extending world limits (+-180,+-90)
                tminx, tminy = max(0, tminx), max(0, tminy)
                tmaxx, tmaxy = min(2 ** (tz + 1) - 1, tmaxx), min(2**tz - 1, tmaxy)
                self.tminmax[tz] = (tminx, tminy, tmaxx, tmaxy)

            # TODO: Maps crossing 180E (Alaska?)

            # Get the maximal zoom level
            # (closest possible zoom level up on the resolution of raster)
            if self.tminz is None:
                self.tminz = self.geodetic.ZoomForPixelSize(
                    self.out_gt[1]
                    * max(
                        self.warped_input_dataset.RasterXSize,
                        self.warped_input_dataset.RasterYSize,
                    )
                    / float(self.tilesize)
                )

            # Get the maximal zoom level
            # (closest possible zoom level up on the resolution of raster)
            if self.tmaxz is None:
                self.tmaxz = self.geodetic.ZoomForPixelSize(self.out_gt[1])

            if self.options.verbose:
                print(
                    "Bounds (latlong):", self.ominx, self.ominy, self.omaxx, self.omaxy
                )

        if self.options.profile == "raster":

            def log2(x):
                return math.log10(x) / math.log10(2)

            self.nativezoom = int(
                max(
                    math.ceil(
                        log2(
                            self.warped_input_dataset.RasterXSize / float(self.tilesize)
                        )
                    ),
                    math.ceil(
                        log2(
                            self.warped_input_dataset.RasterYSize / float(self.tilesize)
                        )
                    ),
                )
            )

            if self.options.verbose:
                print("Native zoom of the raster:", self.nativezoom)

            # Get the minimal zoom level (whole raster in one tile)
            if self.tminz is None:
                self.tminz = 0

            # Get the maximal zoom level (native resolution of the raster)
            if self.tmaxz is None:
                self.tmaxz = self.nativezoom

            # Generate table with min max tile coordinates for all zoomlevels
            self.tminmax = list(range(0, self.tmaxz + 1))
            self.tsize = list(range(0, self.tmaxz + 1))
            for tz in range(0, self.tmaxz + 1):
                tsize = 2.0 ** (self.nativezoom - tz) * self.tilesize
                tminx, tminy = 0, 0
                tmaxx = (
                    int(math.ceil(self.warped_input_dataset.RasterXSize / tsize)) - 1
                )
                tmaxy = (
                    int(math.ceil(self.warped_input_dataset.RasterYSize / tsize)) - 1
                )
                self.tsize[tz] = math.ceil(tsize)
                self.tminmax[tz] = (tminx, tminy, tmaxx, tmaxy)

            # Function which generates SWNE in LatLong for given tile
            if self.kml and self.in_srs_wkt:
                ct = osr.CoordinateTransformation(in_srs, srs4326)

                def rastertileswne(x, y, z):
                    pixelsizex = (
                        2 ** (self.tmaxz - z) * self.out_gt[1]
                    )  # X-pixel size in level
                    west = self.out_gt[0] + x * self.tilesize * pixelsizex
                    east = west + self.tilesize * pixelsizex
                    south = self.ominy + y * self.tilesize * pixelsizex
                    north = south + self.tilesize * pixelsizex
                    if not self.isepsg4326:
                        # Transformation to EPSG:4326 (WGS84 datum)
                        west, south = ct.TransformPoint(west, south)[:2]
                        east, north = ct.TransformPoint(east, north)[:2]
                    return south, west, north, east

                self.tileswne = rastertileswne
            else:
                self.tileswne = lambda x, y, z: (0, 0, 0, 0)  # noqa

    def generate_metadata(self):
        """
        Generation of main metadata files and HTML viewers (metadata related to particular
        tiles are generated during the tile processing).
        """

        if self.options.profile == "mercator":
            south, west = self.mercator.MetersToLatLon(self.ominx, self.ominy)
            north, east = self.mercator.MetersToLatLon(self.omaxx, self.omaxy)
            south, west = max(-85.05112878, south), max(-180.0, west)
            north, east = min(85.05112878, north), min(180.0, east)
            self.swne = (south, west, north, east)

        elif self.options.profile == "geodetic":
            west, south = self.ominx, self.ominy
            east, north = self.omaxx, self.omaxy
            south, west = max(-90.0, south), max(-180.0, west)
            north, east = min(90.0, north), min(180.0, east)
            self.swne = (south, west, north, east)

        elif self.options.profile == "raster":
            west, south = self.ominx, self.ominy
            east, north = self.omaxx, self.omaxy

            self.swne = (south, west, north, east)

    def generate_base_tiles(self):
        """
        Generation of the base tiles (the lowest in the pyramid) directly from the input raster
        """

        # Set the bounds
        tminx, tminy, tmaxx, tmaxy = self.tminmax[self.tmaxz]

        ds = self.warped_input_dataset
        tilebands = self.dataBandsCount + 1
        querysize = self.querysize

        tcount = (1 + abs(tmaxx - tminx)) * (1 + abs(tmaxy - tminy))
        ti = 0

        tile_details = []

        tz = self.tmaxz
        for ty in range(tmaxy, tminy - 1, -1):
            for tx in range(tminx, tmaxx + 1):
                ti += 1
                tilefilename = os.path.join(
                    self.output_folder, str(tz), str(tx), "%s.%s" % (ty, self.tileext)
                )
                if self.options.verbose:
                    print(ti, "/", tcount, tilefilename)

                if self.options.resume and os.path.exists(tilefilename):
                    if self.options.verbose:
                        print("Tile generation skipped because of --resume")
                    continue

                if self.options.profile == "mercator":
                    # Tile bounds in EPSG:3857
                    b = self.mercator.TileBounds(tx, ty, tz)
                elif self.options.profile == "geodetic":
                    b = self.geodetic.TileBounds(tx, ty, tz)

                # Don't scale up by nearest neighbour, better change the querysize
                # to the native resolution (and return smaller query tile) for scaling

                if self.options.profile in ("mercator", "geodetic"):
                    rb, wb = self.geo_query(ds, b[0], b[3], b[2], b[1])

                    # Pixel size in the raster covering query geo extent
                    nativesize = wb[0] + wb[2]
                    if self.options.verbose:
                        print("\tNative Extent (querysize", nativesize, "): ", rb, wb)

                    # Tile bounds in raster coordinates for ReadRaster query
                    rb, wb = self.geo_query(
                        ds, b[0], b[3], b[2], b[1], querysize=querysize
                    )

                    rx, ry, rxsize, rysize = rb
                    wx, wy, wxsize, wysize = wb

                else:  # 'raster' profile:
                    tsize = int(
                        self.tsize[tz]
                    )  # tilesize in raster coordinates for actual zoom
                    xsize = (
                        self.warped_input_dataset.RasterXSize
                    )  # size of the raster in pixels
                    ysize = self.warped_input_dataset.RasterYSize
                    if tz >= self.nativezoom:
                        querysize = self.tilesize

                    rx = (tx) * tsize
                    rxsize = 0
                    if tx == tmaxx:
                        rxsize = xsize % tsize
                    if rxsize == 0:
                        rxsize = tsize

                    rysize = 0
                    if ty == tmaxy:
                        rysize = ysize % tsize
                    if rysize == 0:
                        rysize = tsize
                    ry = ysize - (ty * tsize) - rysize

                    wx, wy = 0, 0
                    wxsize = int(rxsize / float(tsize) * self.tilesize)
                    wysize = int(rysize / float(tsize) * self.tilesize)
                    if wysize != self.tilesize:
                        wy = self.tilesize - wysize

                # Read the source raster if anything is going inside the tile as per the computed
                # geo_query
                tile_details.append(
                    TileDetail(
                        tx=tx,
                        ty=ty,
                        tz=tz,
                        rx=rx,
                        ry=ry,
                        rxsize=rxsize,
                        rysize=rysize,
                        wx=wx,
                        wy=wy,
                        wxsize=wxsize,
                        wysize=wysize,
                        querysize=querysize,
                        filename=self.filename,
                    )
                )

        conf = TileJobInfo(
            src_file=self.tmp_vrt_filename,
            filename=self.filename,
            nb_data_bands=self.dataBandsCount,
            output_file_path=self.output_folder,
            tile_extension=self.tileext,
            tile_driver=self.tiledriver,
            tile_size=self.tilesize,
            tminmax=self.tminmax,
            tminz=self.tminz,
            tmaxz=self.tmaxz,
            in_srs_wkt=self.in_srs_wkt,
            out_geo_trans=self.out_gt,
            ominy=self.ominy,
            is_epsg_4326=self.isepsg4326,
            options=self.options,
        )

        return conf, tile_details

    def geo_query(self, ds, ulx, uly, lrx, lry, querysize=0):
        """
        For given dataset and query in cartographic coordinates returns parameters for ReadRaster()
        in raster coordinates and x/y shifts (for border tiles). If the querysize is not given, the
        extent is returned in the native resolution of dataset ds.

        raises Gdal2TilesError if the dataset does not contain anything inside this geo_query
        """
        geotran = ds.GetGeoTransform()
        rx = int((ulx - geotran[0]) / geotran[1] + 0.001)
        ry = int((uly - geotran[3]) / geotran[5] + 0.001)
        rxsize = int((lrx - ulx) / geotran[1] + 0.5)
        rysize = int((lry - uly) / geotran[5] + 0.5)

        if not querysize:
            wxsize, wysize = rxsize, rysize
        else:
            wxsize, wysize = querysize, querysize

        # Coordinates should not go out of the bounds of the raster
        wx = 0
        if rx < 0:
            rxshift = abs(rx)
            wx = int(wxsize * (float(rxshift) / rxsize))
            wxsize = wxsize - wx
            rxsize = rxsize - int(rxsize * (float(rxshift) / rxsize))
            rx = 0
        if rx + rxsize > ds.RasterXSize:
            wxsize = int(wxsize * (float(ds.RasterXSize - rx) / rxsize))
            rxsize = ds.RasterXSize - rx

        wy = 0
        if ry < 0:
            ryshift = abs(ry)
            wy = int(wysize * (float(ryshift) / rysize))
            wysize = wysize - wy
            rysize = rysize - int(rysize * (float(ryshift) / rysize))
            ry = 0
        if ry + rysize > ds.RasterYSize:
            wysize = int(wysize * (float(ds.RasterYSize - ry) / rysize))
            rysize = ds.RasterYSize - ry

        return (rx, ry, rxsize, rysize), (wx, wy, wxsize, wysize)


def worker_tile_details(input_file, filename, output_folder, options, send_pipe=None):
    gdal2tiles = GDAL2Tiles(input_file, filename, output_folder, options)
    gdal2tiles.open_input()
    gdal2tiles.generate_metadata()
    tile_job_info, tile_details = gdal2tiles.generate_base_tiles()
    return_data = (tile_job_info, tile_details)
    if send_pipe:
        send_pipe.send(return_data)

    return return_data


def progress_printer_thread(queue, nb_jobs):
    pb = ProgressBar(nb_jobs)
    pb.start()
    for _ in range(nb_jobs):
        queue.get()
        pb.log_progress()
        queue.task_done()


class ProgressBar(object):
    def __init__(self, total_items):
        self.total_items = total_items
        self.nb_items_done = 0
        self.current_progress = 0
        self.STEP = 2.5

    def start(self):
        sys.stdout.write("0")

    def log_progress(self, nb_items=1):
        self.nb_items_done += nb_items
        progress = float(self.nb_items_done) / self.total_items * 100
        if progress >= self.current_progress + self.STEP:
            done = False
            while not done:
                if self.current_progress + self.STEP <= progress:
                    self.current_progress += self.STEP
                    if self.current_progress % 10 == 0:
                        sys.stdout.write(str(int(self.current_progress)))
                        if self.current_progress == 100:
                            sys.stdout.write("\n")
                    else:
                        sys.stdout.write(".")
                else:
                    done = True
        sys.stdout.flush()


def get_tile_swne(tile_job_info, options):
    if options.profile == "mercator":
        mercator = GlobalMercator(tileSize=options.tile_size)
        tile_swne = mercator.TileLatLonBounds
    elif options.profile == "geodetic":
        geodetic = GlobalGeodetic(options.tmscompatible, tileSize=options.tile_size)
        tile_swne = geodetic.TileLatLonBounds
    elif options.profile == "raster":
        srs4326 = osr.SpatialReference()
        srs4326.ImportFromEPSG(4326)
        if tile_job_info.kml and tile_job_info.in_srs_wkt:
            in_srs = osr.SpatialReference()
            in_srs.ImportFromWkt(tile_job_info.in_srs_wkt)
            ct = osr.CoordinateTransformation(in_srs, srs4326)

            def rastertileswne(x, y, z):
                pixelsizex = (
                    2 ** (tile_job_info.tmaxz - z) * tile_job_info.out_geo_trans[1]
                )
                west = (
                    tile_job_info.out_geo_trans[0]
                    + x * tile_job_info.tile_size * pixelsizex
                )
                east = west + tile_job_info.tile_size * pixelsizex
                south = tile_job_info.ominy + y * tile_job_info.tile_size * pixelsizex
                north = south + tile_job_info.tile_size * pixelsizex
                if not tile_job_info.is_epsg_4326:
                    # Transformation to EPSG:4326 (WGS84 datum)
                    west, south = ct.TransformPoint(west, south)[:2]
                    east, north = ct.TransformPoint(east, north)[:2]
                return south, west, north, east

            tile_swne = rastertileswne
        else:
            tile_swne = lambda x, y, z: (0, 0, 0, 0)  # noqa
    else:
        tile_swne = lambda x, y, z: (0, 0, 0, 0)  # noqa

    return tile_swne


def single_threaded_tiling(input_file, filename, output_folder, **options):
    """Generate tiles using single process.

    Keep a single threaded version that stays clear of multiprocessing,
    for platforms that would not support it
    """
    options = process_options(input_file, output_folder, options)

    if options.verbose:
        print("Begin tiles details calc")
    conf, tile_details = worker_tile_details(
        input_file, filename, output_folder, options
    )

    if options.verbose:
        print("Tiles details calc complete.")

    if not options.verbose and not options.quiet:
        progress_bar = ProgressBar(len(tile_details))
        progress_bar.start()

    for tile_detail in tile_details:
        create_base_tile(conf, tile_detail)

        if not options.verbose and not options.quiet:
            progress_bar.log_progress()

    create_overview_tiles(conf, output_folder, options)

    shutil.rmtree(os.path.dirname(conf.src_file))


def multi_threaded_tiling(input_file, filename, output_folder, **options):
    """Generate tiles with multi processing."""
    options = process_options(input_file, output_folder, options)

    nb_processes = options.nb_processes or 1
    (conf_receiver, conf_sender) = Pipe(False)

    if options.verbose:
        print("Begin tiles details calc")
    p = Process(
        target=worker_tile_details,
        args=[input_file, filename, output_folder, options],
        kwargs={"send_pipe": conf_sender},
    )
    p.start()
    conf, tile_details = conf_receiver.recv()
    p.join()
    manager = Manager()
    queue = manager.Queue()
    pool = Pool(processes=nb_processes)
    for tile_detail in tile_details:
        pool.apply_async(create_base_tile, (conf, tile_detail), {"queue": queue})

    if not options.verbose and not options.quiet:
        p = Process(target=progress_printer_thread, args=[queue, len(tile_details)])
        p.start()

    pool.close()
    pool.join()  # Jobs finished
    if not options.verbose and not options.quiet:
        p.join()  # Traces done

    create_overview_tiles(conf, output_folder, options)

    shutil.rmtree(os.path.dirname(conf.src_file))


def generate_tiles(input_file, filename, output_folder, **options):
    """Generate tiles from input file."""
    if options:
        nb_processes = options.get("nb_processes") or 1
    else:
        nb_processes = 1

    if nb_processes == 1:
        single_threaded_tiling(input_file, filename, output_folder, **options)
    else:
        multi_threaded_tiling(input_file, filename, output_folder, **options)
