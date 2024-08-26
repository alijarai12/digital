from pyparsing import (
    Forward,
    Keyword,
    Literal,
    Optional,
    Regex,
    Word,
    ZeroOrMore,
    alphanums,
    delimitedList,
    oneOf,
)
from functools import reduce
from PIL import Image
from core.raster.gdaltiles import generate_tiles
import tempfile
from osgeo import gdal
import numpy
import keyword
import operator
from core.utils import constants


class FormulaParser(object):
    """
    Deconstantsantsruct mathematical algebra expressions and convert those into
    callable funcitons.


    Deconstruct mathematical algebra expressions and convert those into
    callable funcitons.

    This formula parser was inspired by the fourFun pyparsing example and also
    benefited from additional substantial contributions by Paul McGuire.
    This module uses pyparsing for this purpose and the parser is adopted from
    the `fourFun example`__.

    Example usage::

        >>> parser = FormulaParser()
        >>> parser.set_formula('log(a * 3 + b)')
        >>> parser.evaluate({'a': 5, 'b': 23})
        ... 3.6375861597263857
        >>> parser.evaluate({'a': [5, 6, 7], 'b': [23, 24, 25]})
        ... array([ 3.63758616,  3.73766962,  3.8286414 ])

    __ http://pyparsing.wikispaces.com/file/view/fourFn.py
    """

    def __init__(self):
        """
        Setup the Backus Normal Form (BNF) parser logic.
        """
        # Set an empty formula attribute
        self.formula = None

        # Instantiate blank parser for BNF constsruction
        self.bnf = Forward()

        # Expression for parenthesis, which are suppressed in the atoms
        # after matching.
        lpar = Literal(constants.LPAR).suppress()
        rpar = Literal(constants.RPAR).suppress()

        # Expression for mathematical constantsants: Euler number and Pi
        e = Keyword(constants.EULER)
        pi = Keyword(constants.PI)
        null = Keyword(constants.NULL)
        _true = Keyword(constants.TRUE)
        _false = Keyword(constants.FALSE)

        # Prepare operator expressions
        addop = oneOf(constants.ADDOP)
        multop = oneOf(constants.MULTOP)
        powop = oneOf(constants.POWOP)
        unary = reduce(operator.add, (Optional(x) for x in constants.UNOP))

        # Expression for floating point numbers, allowing for scientific notation.
        number = Regex(constants.NUMBER)

        # Variables are alphanumeric strings that represent keys in the input
        # data dictionary.
        variable = delimitedList(
            Word(alphanums), delim=constants.VARIABLE_NAME_SEPARATOR, combine=True
        )

        # Functional calls
        function = Word(alphanums) + lpar + self.bnf + rpar

        # Atom core - a single element is either a math constantsant,
        # a function or a variable.
        atom_core = function | pi | e | null | _true | _false | number | variable

        # Atom subelement between parenthesis
        atom_subelement = lpar + self.bnf.suppress() + rpar

        # In atoms, pi and e need to be before the letters for it to be found
        atom = (
            unary + atom_core.setParseAction(self.push_first) | atom_subelement
        ).setParseAction(self.push_unary_operator)

        # By defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of
        # left-to-right that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()
        factor << atom + ZeroOrMore((powop + factor).setParseAction(self.push_first))

        term = factor + ZeroOrMore((multop + factor).setParseAction(self.push_first))
        self.bnf << term + ZeroOrMore((addop + term).setParseAction(self.push_first))

    def push_first(self, strg, loc, toks):
        self.expr_stack.append(toks[0])

    def push_unary_operator(self, strg, loc, toks):
        """
        Set custom flag for unary operators.
        """
        if toks and toks[0] in constants.UNARY_REPLACE_MAP:
            self.expr_stack.append(constants.UNARY_REPLACE_MAP[toks[0]])

    def evaluate_stack(self, stack):
        """
        Evaluate a stack element.
        """
        op = stack.pop()

        if op in constants.UNARY_OPERATOR_MAP:
            return constants.UNARY_OPERATOR_MAP[op](self.evaluate_stack(stack))

        elif op in constants.OPERATOR_MAP:
            op2 = self.evaluate_stack(stack)
            op1 = self.evaluate_stack(stack)
            # Handle null case
            if isinstance(op1, str) and op1 == constants.NULL:
                op2 = self.get_mask(op2, op)
                op1 = True
            elif isinstance(op2, str) and op2 == constants.NULL:
                op1 = self.get_mask(op1, op)
                op2 = True
            return constants.OPERATOR_MAP[op](op1, op2)

        elif op in constants.FUNCTION_MAP:
            return constants.FUNCTION_MAP[op](self.evaluate_stack(stack))

        elif op in constants.KEYWORD_MAP:
            return constants.KEYWORD_MAP[op]

        elif op in self.variable_map:
            return self.variable_map[op]

        else:
            try:
                return numpy.array(op, dtype=constants.ALGEBRA_PIXEL_TYPE_NUMPY)
            except ValueError:
                raise Exception(
                    'Found an undeclared variable "{0}" in formula.'.format(op)
                )

    @staticmethod
    def get_mask(data, operator):
        # Make sure the right operator is used
        if operator not in (constants.EQUAL, constants.NOT_EQUAL):
            raise Exception('NULL can only be used with "==" or "!=" operators.')
        # Get mask
        if numpy.ma.is_masked(data):
            return data.mask
        # If there is no mask, all values are not null
        return numpy.zeros(data.shape, dtype=numpy.bool)

    def set_formula(self, formula):
        """
        Store the input formula as the one to evaluate on.
        """
        # Remove any white space and line breaks from formula.
        self.formula = formula.replace(" ", "").replace("\n", "").replace("\r", "")

    def prepare_data(self):
        """
        Basic checks and conversion of input data.
        """
        for key, var in self.variable_map.items():
            # Keywords are not allowed as variables, variables can not start or
            # end with separator.
            if keyword.iskeyword(key) or key != key.strip(
                constantsants.VARIABLE_NAME_SEPARATOR
            ):
                raise Exception('Invalid variable name found: "{}".'.format(key))

            # Convert all data to numpy arrays
            if not isinstance(var, numpy.ndarray):
                self.variable_map[key] = numpy.array(var)

    def evaluate(self, data={}, formula=None):
        """
        Evaluate the input data using the current formula expression stack.

        The formula is stored as attribute and can be re-evaluated with several
        input data sets on an existing parser.
        """
        if formula:
            self.set_formula(formula)

        if not self.formula:
            raise Exception("Formula not specified.")

        # Store data for variables
        self.variable_map = data

        # Check and convert input data
        self.prepare_data()

        # Reset expression stack
        self.expr_stack = []

        # Populate the expression stack
        self.bnf.parseString(self.formula)

        # Evaluate stack on data
        return self.evaluate_stack(self.expr_stack)


def colormap_generator(ds, colors, values=None, unique=None):
    """
    Generates a colormap from a GDALRaster and colors array.
    """
    if values is None:
        if unique is None:
            minmax = ds.GetRasterBand(1).GetStatistics(True, True)
            rasterrange = minmax[1] - minmax[0]
            steps = rasterrange / len(colors)
            colormap = {}
            for c in colors:
                colormap[f"(x > {minmax[0]}) & (x <= {minmax[0]+steps})"] = c
                minmax[0] += steps
            return colormap
        else:
            data = ds.GetRasterBand(1).ReadAsArray()
            unique = numpy.unique(data)
            colormap = {}
            for i in range(len(colors)):
                colormap[unique[i + 1]] = colors[i]
            return colormap
    else:
        if len(values) == len(colors) + 1:
            colormap = {}
            for i in range(len(colors)):
                colormap[f"(x > {values[i]}) & (x <= {values[i+1]})"] = colors[i]
            return colormap
        elif len(values) == len(colors):
            colormap = {}
            for i in range(len(colors)):
                colormap[values[i]] = colors[i]
            return colormap
        else:
            return "Did not match any pattern"


def hex_to_rgba(value, alpha=255):
    """
    Converts a HEX color string to a RGBA 4-tuple.
    """
    value = value.lstrip("#")

    # Check length and input string property
    if len(value) not in [1, 2, 3, 6] or not value.isalnum():
        raise print("Invalid color, could not convert hex to rgb.")

    # Repeat values for shortened input
    value = (value * 6)[:6]

    # Convert to rgb
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha


def colormap_to_rgba(colormap):
    """
    Convert color ma to rgba colors.
    """
    if "continuous" in colormap:
        return {
            k: hex_to_rgba(v)
            if isinstance(v, (str, int)) and k in ["from", "to", "over"]
            else v
            for k, v in colormap.items()
        }
    else:
        return {
            k: hex_to_rgba(v) if isinstance(v, (str, int)) else v
            for k, v in colormap.items()
        }


def legend_generator(ds, colormap):
    """
    Generates a legend for a GDALRaster.
    """
    data = ds.GetRasterBand(1).GetStatistics(True, True)
    min = data[0]
    max = data[1]
    if "continuous" in colormap:
        legendEntry = {str(min): colormap["from"], str(max): colormap["to"]}
        legend = {"type": "continuous", "legendEntry": legendEntry}
        return legend
    elif "unique" in colormap:
        data = ds.GetRasterBand(1).ReadAsArray()
        unique = numpy.unique(data).tolist()
        legendEntry = {}
        unique = unique[1:]
        for i in range(len(unique)):
            legendEntry[str(unique[i])] = colormap["colors"][i]
        legend = {"type": "unique", "legendEntry": legendEntry}
        return legend
    elif "colors" in colormap:
        rasterrange = max - min
        steps = rasterrange / len(colormap["colors"])
        values = [min]
        for c in colormap["colors"]:
            values.append(min + steps)
            min += steps
        values = values[1:]
        legendEntry = {}
        for i in range(len(values)):
            legendEntry[str(values[i])] = colormap["colors"][i]
        legend = {"type": "discrete", "legendEntry": legendEntry}
        return legend
    elif "values" in colormap:
        if len(colormap["values"]) == len(colormap["valuecolors"]):
            legendEntry = {}
            for i in range(len(colormap["values"])):
                if colormap["opacities"][i] == "0":
                    pass
                else:
                    legendEntry[str(colormap["labels"][i])] = colormap["valuecolors"][i]
            legend = {"type": "unique", "legendEntry": legendEntry}
            return legend
        else:
            values = colormap["values"]
            values = values[1:]
            legendEntry = {}
            for i in range(len(values)):
                if colormap["opacities"][i] == "0":
                    pass
                else:
                    legendEntry[str(colormap["labels"][i])] = colormap["valuecolors"][i]
            legend = {"type": "discrete", "legendEntry": legendEntry}
            return legend
    else:
        legend = {}
        return legend


def rescale_to_channel_range(data, dfrom, dto, dover=None):
    """
    Rescales an array to the color interval provided. Assumes that the data is normalized.

    This is used as a helper function for continuous colormaps.
    """
    # If the interval is zero dimensional, return constantsantsant array.
    if dfrom == dto:
        return numpy.ones(data.shape) * dfrom

    if dover is None:
        # Invert data going from smaller to larger if origin color is bigger
        # than target color.
        if dto < dfrom:
            data = 1 - data
        return data * abs(dto - dfrom) + min(dto, dfrom)
    else:
        # Divide data in upper and lower half.
        lower_half = data < 0.5
        # Recursive calls to scaling upper and lower half separately.
        data[lower_half] = rescale_to_channel_range(data[lower_half] * 2, dfrom, dover)
        data[numpy.logical_not(lower_half)] = rescale_to_channel_range(
            (data[numpy.logical_not(lower_half)] - 0.5) * 2, dover, dto
        )

        return data


def band_data_to_image(band_data, colormap):
    """
    Creates an python image from pixel values of a GDALRaster.
    The input is a dictionary that maps pixel values to RGBA UInt8 colors.
    If an interpolation interval is given, the values are
    """
    # Get data as 1D array
    dat = band_data.ravel()
    stats = {}

    if "continuous" in colormap:
        dmin, dmax = colormap.get("range", (dat.min(), dat.max()))

        if dmax == dmin:
            norm = dat == dmin
        else:
            norm = (dat - dmin) / (dmax - dmin)

        color_from = colormap.get("from", [0, 0, 0])
        color_to = colormap.get("to", [1, 1, 1])
        color_over = colormap.get("over", [None, None, None])

        red = rescale_to_channel_range(
            norm.copy(), color_from[0], color_to[0], color_over[0]
        )
        green = rescale_to_channel_range(
            norm.copy(), color_from[1], color_to[1], color_over[1]
        )
        blue = rescale_to_channel_range(
            norm.copy(), color_from[2], color_to[2], color_over[2]
        )

        # Compute alpha channel from mask if available.
        if numpy.ma.is_masked(dat):
            alpha = 255 * numpy.logical_not(dat.mask) * (norm >= 0) * (norm <= 1)
        else:
            alpha = 255 * (norm > 0) * (norm < 1)

        rgba = numpy.array([red, green, blue, alpha], dtype="uint8").T
    else:
        # Create zeros array
        rgba = numpy.zeros((dat.shape[0], 4), dtype="uint8")

        # Replace matched rows with colors
        for key, color in colormap.items():
            orig_key = key
            try:
                # Try to use the key as number directly
                key = float(key)
                selector = dat == key
            except ValueError:
                # Otherwise use it as numpy expression directly
                parser = FormulaParser()
                selector = parser.evaluate({"x": dat}, key)

            # If masked, use mask to filter values additional to formula values
            if numpy.ma.is_masked(selector):
                selector.fill_value = False
                rgba[selector.filled() == 1] = color
                # Compress for getting statistics
                selector = selector.compressed()
            else:
                rgba[selector] = color

            # Track pixel statistics for this tile
            stats[str(orig_key)] = int(numpy.sum(selector))

    # Reshape array to image size
    rgba = rgba.reshape(band_data.shape[0], band_data.shape[1], 4)

    # Create image from array
    img = Image.fromarray(rgba)

    return img, stats


def generate_raster_tiles(raster_file, raster_name, colormap, output_folder, **options):
    ds = gdal.Open(raster_file)
    if ds.RasterCount > 1 or colormap is None:
        generate_tiles(raster_file, raster_name, output_folder, **options)
        return {}, {}
    else:
        legend = legend_generator(ds, colormap)
        if "unique" in colormap:
            colormap = colormap_generator(ds, colormap["colors"], unique=True)
        elif "colors" in colormap:
            colormap = colormap_generator(ds, colormap["colors"])
        elif "values" in colormap:
            colormap = colormap_generator(
                ds, colormap["valuecolors"], colormap["values"]
            )
        colormap = colormap_to_rgba(colormap)

        tf = tempfile.NamedTemporaryFile()
        output_file = f"{tf.name}.tif"

        band_data = ds.GetRasterBand(1).ReadAsArray()
        band_data = numpy.round(band_data, 8)
        band_data[numpy.isnan(band_data)] = 0
        band_data[~numpy.isfinite(band_data)] = 1

        img, stats = band_data_to_image(band_data, colormap)
        img.save(output_file)
        out = gdal.Open(output_file, 1)  # Open rater file in write mode
        out.SetGeoTransform(ds.GetGeoTransform())  # Set geographic transformation
        out.SetProjection(ds.GetProjection())  # Set projection
        out = None
        generate_tiles(output_file, raster_name, output_folder, **options)
        tf = None
        if legend is not None:
            try:
                legendEntry = legend.get("legendEntry")
                legend = {
                    "type": legend.get("type"),
                    "colors": list(legendEntry.values()),
                    "values": list(legendEntry.keys()),
                }
            except:
                legend = legend

        return legend, stats
