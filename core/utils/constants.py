PALIKA_FILE_FORMAT_CHOICES = [
    ("palika", "Palika"),
    ("ward", "Ward"),
]
NUMBERING_STATUS_CHOICES = [
    ("completed", "Completed"),
    ("ongoing", "Ongoing"),
    ("not_started", "Not Started"),
]
FILE_FORMAT_CHOICES = [
    ("shapefile", "Shapefile"),
    ("csv", "CSV"),
    ("geojson", "Geojson"),
]
PAVEMENT_TYPE_CHOICES = [
    ("other", "Other", "अन्य"),
    ("black_topped", "Black Topped", "कालो पत्रे"),
    ("gravel", "Gravel", "रोडा"),
    ("concrete", "Concrete", "कंक्रीट"),
    ("earthen", "Earthen", "माटो"),
]
ROAD_CATEGORY_CHOICES = [
    ("major", "Major", "प्रमुख"),
    ("minor", "Minor", "सानातिना"),
    ("subsidiary", "Subsidiary", "सहायक"),
]
ROAD_CLASS_CHOICES = [
    ("other_urban_road", "Other urban road", "अन्य सहरी सडक"),
    ("national_highway", "National highway", "राष्ट्रिय राजमार्ग"),
    ("feeder_road", "Feeder road", "फिडर रोड"),
    ("district_road", "District road", "जिल्ला सडक"),
]

ASSOCIATION_TYPE_CHOICES = [
    ("main", "Main", "मुख्य"),
    ("associate", "Associate", "सहायक"),
    ("dissociate", "Dissociate", "अलग"),
]

ROOF_TYPE_CHOICES = [
    ("other", "Other", "अन्य"),
    ("rcc", "RCC", "आर.सि.सि"),
    ("tile", "Tile", "टाइल"),
    ("cgi_sheet", "CGI sheet", "जी.आइ. पाता"),
    ("straw", "Straw", "स्ट्राओ"),
]

STRUCTURE_CHOICES = [
    ("other", "Other", "अन्य"),
    ("framed", "Framed", "फ्रेम गरिएको"),
    ("load_bearing", "Load bearing", "लोड सहन सक्ने"),
    ("timber", "Timber", "काठ"),
    ("earthen_masonry", "Earthen masonry", "माटोको डकर्मी "),
]

REGISTRATION_TYPE_CHOICES = [
    (
        "registered_and_completed",
        "Registered and completed",
        "दर्ता गरिएको र निर्माण सम्पन्न",
    ),
    ("archived_with_condition", "Archived with condition", "सर्त सहित अभिलेख राखिएको"),
    (
        "registered_and_under_construction",
        "Registered and under construction",
        "दर्ता गरिएको र निर्माण हुदै गरेको",
    ),
    ("not_registered", "Not registered", "दर्ता भएको छैन"),
    ("not_aware", "Not aware", "थाहा छैन"),
    ("archived", "Archived", "अभिलेख राखिएको"),
]

USE_CHOICES = [
    ("other", "Other", "अन्य"),
    ("residential", "Residential", "आवासीय"),
    ("commercial", "Commercial", "व्यापारिक"),
    ("multi_use", "Multi use", "बहु-प्रयोग"),
    ("institutional", "Institutional", "संस्थागत"),
    ("unused", "Unused", "प्रयोग नगरिएको"),
]

SPECIFIC_USE_CHOICES = [
    ("other", "Other", "अन्य"),
    ("hospitality", "Hospitality", "आतिथ्य सत्कार"),
    ("smes", "SMES", "एस्.एम्.ई.एस्"),
    ("retails", "Retails", "खुद्रा"),
    ("construction_and_engineering", "Construction and Engineering", "सी.एन.इ."),
    ("agriculture", "Agriculture", "कृषि"),
    ("pharmacy", "Pharmacy", "फार्मेसी"),
    ("entertainment", "Entertainment", "मनोरञ्जन"),
    ("financial", "Financial", "वित्तीय"),
    ("healthcare", "Healthcare", "स्वास्थ्य"),
    ("education", "Education", "शिक्षा"),
    ("industry_and_manufacturing", "Industry and Manufacturing", "उद्योग"),
    ("media", "Media", "मीडिया"),
    ("religious", "Religious", "धार्मिक"),
    ("mall", "Mall", "मल"),
    ("residential", "Residential", "आवासीय"),
]

OWNER_STATUS_CHOICES = [
    ("governmental", "Governmental", "सरकारी"),
    ("non_governmental", "Non governmental", "गैर-सरकारी"),
]

TEMPRORARY_STATUS_CHOICES = [
    ("permanent", "Permanent", "स्थायी"),
    ("temporary", "Temporary", "अस्थायी"),
]

ROAD_LANE_CHOICES = [
    ("alley", "Alley", "गल्ली"),
    ("single_lane", "Single lane", "एकल लेन"),
    ("double_lane", "Double lane", "दोहोरो लेन"),
    ("four_lane", "Four lane", "चार लेन"),
]

DIRECTION_CHOICES = [
    ("left", "Left"),
    ("right", "Right"),
]

VECTOR_LAYER_CATEGORY_CHOICES = [
    ("base_line_data", "Base Line Data"),
    ("resource_data", "Resources Data"),
    ("tourism_data", "Tourism Data"),
    ("utilities_data", "Utilities Data"),
    ("open_space", "Open Space"),
    ("orthophoto", "Orthophoto"),
    ("raster_data", "Raster Data"),
    ("risk_and_hazard_data", "Risk and Hazard Data"),
]

DATA_GROUP_CHOICES = [
    ("art_history_and_culture", "Art, History and Culture"),
    ("basemaps", "Basemaps"),
    ("blue_infrastructures", "Blue Infrastructures"),
    ("boundary", "Boundary"),
    ("disaster", "Diaster"),
    ("economy", "Economy"),
    ("education", "Education"),
    ("economy", "Economy"),
    ("education", "Education"),
    ("geography", "Geography"),
    ("government_bodies", "Government Bodies"),
    ("health", "Health"),
    ("organizations", "Organizations"),
    ("infrastructure", "Infrastructure"),
    ("industries_and_factories", "Industries and Factories"),
    ("power_and_energy", "Power and Energy"),
    ("public_utilities", "Public Utilities"),
    ("raster", "Raster"),
    ("recreational_infrastructure", "Recreational Infrastructure"),
    ("risk_and_hazard", "Risk and Hazard"),
    ("risk_infrastructure", "Risk Infrastructure"),
    ("telecommunication", "Telecommunication"),
    ("tourism_destination", "Tourism Destination"),
    ("tourism_facilities", "Tourism Facilities"),
    ("transport", "Transport"),
    ("water_infrastructure", "Water Infrastructure"),
    ("agriculture_and_livestock", "Agriculture and Livestock"),
]

DATA_SOURCE_CHOICES = [
    ("spatial", "Spatial"),
    ("non_spatial", "Non Spatial"),
]

STATUS_CHOICES = [
    (("in_process"), ("In Process")),
    (("completed"), ("Completed")),
    (("error"), ("Error")),
]

BuildingFieldChoicesType = (
    ("owner_status", "owner_status"),
    ("temporary_type", "temporary_type"),
    ("association_type", "association_type"),
    ("roof_type", "roof_type"),
    ("building_structure", "building_structure"),
    ("reg_type", "reg_type"),
    ("building_use", "building_use"),
    ("building_sp_use", "building_sp_use"),
    ("road_type", "road_type"),
    ("road_lane", "road_lane"),
)

RoadfieldChoicesType = (
    ("road_type", "road_type"),
    ("road_category", "road_category"),
    ("road_class", "road_class"),
    ("road_lane", "road_lane"),
)


"""
Define all mappings between operators and string representations.
"""
import numpy

ALGEBRA_PIXEL_TYPE_GDAL = 7
ALGEBRA_PIXEL_TYPE_NUMPY = "float64"

LPAR = "("
RPAR = ")"

NUMBER = r"[+-]?\d+(\.\d*)?([Ee][+-]?\d+)?"

VARIABLE_NAME_SEPARATOR = "_"
BAND_INDEX_SEPARATOR = ":"

# Keywords
EULER = "E"
PI = "PI"
TRUE = "TRUE"
FALSE = "FALSE"
NULL = "NULL"
INFINITE = "INF"

KEYWORD_MAP = {
    EULER: numpy.e,
    PI: numpy.pi,
    TRUE: True,
    FALSE: False,
    NULL: NULL,
    INFINITE: numpy.inf,
}

# Operator strings
ADD = "+"
SUBTRACT = "-"
MULTIPLY = "*"
DIVIDE = "/"
POWER = "^"
EQUAL = "=="
NOT_EQUAL = "!="
GREATER = ">"
GREATER_EQUAL = ">="
LESS = "<"
LESS_EQUAL = "<="
LOGICAL_OR = "|"
LOGICAL_AND = "&"
LOGICAL_NOT = "!"
FILL = "~"
UNARY_AND = "unary +"
UNARY_LESS = "unary -"
UNARY_NOT = "unary !"
UNARY_FILL = "unary ~"

# Operator groups
ADDOP = (
    ADD,
    SUBTRACT,
)
POWOP = (POWER,)
UNOP = (ADD, SUBTRACT, LOGICAL_NOT, FILL)
# The order the operators in this group matters due to "<=" being caught by "<".
MULTOP = (
    MULTIPLY,
    DIVIDE,
    EQUAL,
    NOT_EQUAL,
    GREATER_EQUAL,
    LESS_EQUAL,
    GREATER,
    LESS,
    LOGICAL_AND,
    LOGICAL_OR,
)

# Map operator symbols to arithmetic operations in numpy
OPERATOR_MAP = {
    ADD: numpy.add,
    SUBTRACT: numpy.subtract,
    MULTIPLY: numpy.multiply,
    DIVIDE: numpy.divide,
    POWER: numpy.power,
    EQUAL: numpy.equal,
    NOT_EQUAL: numpy.not_equal,
    GREATER: numpy.greater,
    GREATER_EQUAL: numpy.greater_equal,
    LESS: numpy.less,
    LESS_EQUAL: numpy.less_equal,
    LOGICAL_OR: numpy.logical_or,
    LOGICAL_AND: numpy.logical_and,
}

UNARY_OPERATOR_MAP = {
    UNARY_AND: numpy.array,
    UNARY_LESS: numpy.negative,
    UNARY_NOT: numpy.logical_not,
    UNARY_FILL: numpy.ma.filled,
}

UNARY_REPLACE_MAP = {
    ADD: UNARY_AND,
    SUBTRACT: UNARY_LESS,
    LOGICAL_NOT: UNARY_NOT,
    FILL: UNARY_FILL,
}

# Map function names to numpy functions
FUNCTION_MAP = {
    "sin": numpy.sin,
    "cos": numpy.cos,
    "tan": numpy.tan,
    "log": numpy.log,
    "exp": numpy.exp,
    "abs": numpy.abs,
    "int": numpy.int,
    "round": numpy.round,
    "sign": numpy.sign,
    "min": numpy.min,
    "max": numpy.max,
    "mean": numpy.mean,
    "median": numpy.median,
    "std": numpy.std,
    "sum": numpy.sum,
}
