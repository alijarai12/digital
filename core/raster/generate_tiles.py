import tempfile, math
from osgeo import gdal, osr
from xml.dom import minidom

tileSize = 256
initialResolution = 2 * math.pi * 6378137 / tileSize
originShift = 2 * math.pi * 6378137 / 2.0


def Resolution(zoom):
    return initialResolution / (2**zoom)


def PixelsToMeters(px, py, zoom):
    res = Resolution(zoom)
    mx = px * res - originShift
    my = py * res - originShift
    return mx, my


def TileBounds(tx, ty, zoom):
    minx, miny = PixelsToMeters(tx * tileSize, ty * tileSize, zoom)
    maxx, maxy = PixelsToMeters((tx + 1) * tileSize, (ty + 1) * tileSize, zoom)
    return (minx, miny, maxx, maxy)


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


def geo_query(ds, ulx, uly, lrx, lry, querysize=0):
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


def reproject_dataset(from_dataset, from_srs, to_srs):
    if (from_srs.ExportToProj4() != to_srs.ExportToProj4()) or (
        from_dataset.GetGCPCount() != 0
    ):
        to_dataset = gdal.AutoCreateWarpedVRT(
            from_dataset, from_srs.ExportToWkt(), to_srs.ExportToWkt()
        )
        return to_dataset
    else:
        return from_dataset


def scale_query_to_tile(dsquery, dstile, tiledriver, tilefilename=""):
    """Scales down query dataset to the tile dataset"""

    querysize = dsquery.RasterXSize
    tilesize = dstile.RasterXSize
    tilebands = dstile.RasterCount
    resampling = "average"

    if resampling == "average":
        for i in range(1, tilebands + 1):
            # Black border around NODATA
            res = gdal.RegenerateOverview(
                dsquery.GetRasterBand(i), dstile.GetRasterBand(i), "average"
            )

    elif resampling == "near":
        gdal_resampling = gdal.GRA_NearestNeighbour

    elif resampling == "bilinear":
        gdal_resampling = gdal.GRA_Bilinear

    elif resampling == "cubic":
        gdal_resampling = gdal.GRA_Cubic

    # Other algorithms are implemented by gdal.ReprojectImage().
    dsquery.SetGeoTransform(
        (0.0, tilesize / float(querysize), 0.0, 0.0, 0.0, tilesize / float(querysize))
    )
    dstile.SetGeoTransform((0.0, 1.0, 0.0, 0.0, 0.0, 1.0))

    res = gdal.ReprojectImage(dsquery, dstile, None, None, gdal_resampling)


def create_base_tile(project, hour, z, x, y):
    gdal.AllRegister()
    tilesize = 256
    tile_driver = "PNG"
    querysize = 256
    b = TileBounds(x, y, z)
    ds = gdal.Open("media/" + project + "/" + hour + ".tif", gdal.GA_ReadOnly)
    input_srs_wkt = ds.GetProjection()
    if not input_srs_wkt and ds.GetGCPCount() != 0:
        input_srs_wkt = ds.GetGCPProjection()
    if input_srs_wkt:
        input_srs = osr.SpatialReference()
        input_srs.ImportFromWkt(input_srs_wkt)
    output_srs = osr.SpatialReference()
    output_srs.ImportFromEPSG(3857)
    ds = reproject_dataset(ds, input_srs, output_srs)
    dataBandsCount = nb_data_bands(ds)
    tilebands = dataBandsCount + 1
    mem_drv = gdal.GetDriverByName("MEM")
    out_drv = gdal.GetDriverByName(tile_driver)
    alphaband = ds.GetRasterBand(1).GetMaskBand()

    rb, wb = geo_query(ds, b[0], b[3], b[2], b[1])

    # Pixel size in the raster covering query geo extent
    nativesize = wb[0] + wb[2]

    # Tile bounds in raster coordinates for ReadRaster query
    rb, wb = geo_query(ds, b[0], b[3], b[2], b[1], querysize=querysize)

    rx, ry, rxsize, rysize = rb
    wx, wy, wxsize, wysize = wb

    # Tile dataset in memory
    tf = tempfile.NamedTemporaryFile()
    out_file = tf.name + ".png"
    tilefilename = out_file
    dstile = mem_drv.Create("", tilesize, tilesize, tilebands)

    data = alpha = None

    # Query is in 'nearest neighbour' but can be bigger in then the tilesize
    # We scale down the query to the tilesize by supplied algorithm.

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
            dsquery = mem_drv.Create("", querysize, querysize, tilebands)
            dsquery.WriteRaster(
                wx,
                wy,
                wxsize,
                wysize,
                data,
                band_list=list(range(1, dataBandsCount + 1)),
            )
            dsquery.WriteRaster(wx, wy, wxsize, wysize, alpha, band_list=[tilebands])

            scale_query_to_tile(dsquery, dstile, tile_driver, tilefilename=tilefilename)
            del dsquery

    del ds
    del data

    # Write a copy of tile to png/jpg
    out_drv.CreateCopy(tilefilename, dstile, strict=0)

    del dstile
    return tilefilename


def sld2colormap(s):
    """
    Convert a sld string to a colormap.
    """
    s = minidom.parseString(s)
    sldtype = s.getElementsByTagName("sld:ColorMap")[0].getAttribute("type")
    t = s.getElementsByTagName("sld:ColorMapEntry")
    colors = []
    values = []
    labels = []
    opacities = []
    if sldtype == "intervals" or sldtype == "ramp":
        values = ["0"]
    for m in t:
        colors.append(m.getAttribute("color") or "#000000")
        values.append(m.getAttribute("quantity") or "")
        labels.append(m.getAttribute("label") or "")
        opacities.append(m.getAttribute("opacity") or "1")
    colormap = {
        "valuecolors": colors,
        "values": values,
        "labels": labels,
        "opacities": opacities,
    }
    return colormap


def metadata_generator(raster):
    """
    Generate metadata for given files.
    """
    ds = gdal.Open(raster)
    width = ds.RasterXSize
    height = ds.RasterYSize
    bands = ds.RasterCount
    min, max, mean, stdiv = ds.GetRasterBand(1).GetStatistics(0, 1)
    pixelSize = ds.GetGeoTransform()[1]
    srid = osr.SpatialReference(wkt=ds.GetProjection()).GetAttrValue("AUTHORITY", 1)
    if srid:
        tf = tempfile.NamedTemporaryFile()
        out_file = f"{tf.name}.tif"
        srs = gdal.Warp(out_file, raster, dstSRS="EPSG:3857")
        ds = gdal.Open(out_file)
        geotransform = ds.GetGeoTransform()
        extent = [
            geotransform[0],
            geotransform[3],
            geotransform[0] + width * geotransform[1],
            geotransform[3] + height * geotransform[5],
        ]
    else:
        extent = None
    metadata = {
        "width": width,
        "height": height,
        "minx": min,
        "maxx": max,
        "pixel_size": pixelSize,
        "srid": srid,
        "extent": extent,
    }
    return metadata
