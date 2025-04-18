from enum import Enum


class Term(str, Enum):
    """Savings Plansの契約期間"""

    ONE_YEAR = "1 year"
    THREE_YEAR = "3 year"


class PaymentOption(str, Enum):
    """Savings Plansの支払いオプション"""

    ALL_UPFRONT = "All Upfront"
    PARTIAL_UPFRONT = "Partial Upfront"
    NO_UPFRONT = "No Upfront"


class Region(str, Enum):
    """Savings Plansのリージョン"""

    US_EAST_N_VIRGINIA = "US East (N. Virginia)"
    US_WEST_OREGON = "US West (Oregon)"
    EU_IRELAND = "EU (Ireland)"
    ASIA_PACIFIC_TOKYO = "Asia Pacific (Tokyo)"
    EU_FRANKFURT = "EU (Frankfurt)"
    US_EAST_OHIO = "US East (Ohio)"
    ASIA_PACIFIC_SYDNEY = "Asia Pacific (Sydney)"
    ASIA_PACIFIC_SINGAPORE = "Asia Pacific (Singapore)"
    AWS_GOVCLOUD_US = "AWS GovCloud (US)"
    ASIA_PACIFIC_MUMBAI = "Asia Pacific (Mumbai)"
    CANADA_CENTRAL = "Canada (Central)"
    ASIA_PACIFIC_SEOUL = "Asia Pacific (Seoul)"
    US_WEST_N_CALIFORNIA = "US West (N. California)"
    EU_LONDON = "EU (London)"
    SOUTH_AMERICA_SAO_PAULO = "South America (Sao Paulo)"
    EU_STOCKHOLM = "EU (Stockholm)"
    EU_PARIS = "EU (Paris)"
    AWS_GOVCLOUD_US_EAST = "AWS GovCloud (US-East)"
    EU_SPAIN = "EU (Spain)"
    EU_MILAN = "EU (Milan)"
    ASIA_PACIFIC_OSAKA = "Asia Pacific (Osaka)"
    AFRICA_CAPE_TOWN = "Africa (Cape Town)"
    ASIA_PACIFIC_HYDERABAD = "Asia Pacific (Hyderabad)"
    ASIA_PACIFIC_HONG_KONG = "Asia Pacific (Hong Kong)"
    ASIA_PACIFIC_JAKARTA = "Asia Pacific (Jakarta)"
    EU_ZURICH = "EU (Zurich)"
    ISRAEL_TEL_AVIV = "Israel (Tel Aviv)"
    ASIA_PACIFIC_MALAYSIA = "Asia Pacific (Malaysia)"
    MIDDLE_EAST_BAHRAIN = "Middle East (Bahrain)"
    MIDDLE_EAST_UAE = "Middle East (UAE)"
    ASIA_PACIFIC_THAILAND = "Asia Pacific (Thailand)"
    MEXICO_CENTRAL = "Mexico (Central)"
    ASIA_PACIFIC_MELBOURNE = "Asia Pacific (Melbourne)"
    CANADA_WEST_CALGARY = "Canada West (Calgary)"
    US_EAST_DALLAS = "US East (Dallas)"
    US_WEST_LOS_ANGELES = "US West (Los Angeles)"
    US_EAST_NEW_YORK_CITY = "US East (New York City)"
    US_EAST_ATLANTA = "US East (Atlanta)"
    US_EAST_CHICAGO = "US East (Chicago)"
    US_WEST_PHOENIX = "US West (Phoenix)"
    US_EAST_MIAMI = "US East (Miami)"
    US_EAST_HOUSTON = "US East (Houston)"
    US_EAST_PHILADELPHIA = "US East (Philadelphia)"
    US_WEST_DENVER = "US West (Denver)"
    ARGENTINA_BUENOS_AIRES = "Argentina (Buenos Aires)"
    US_EAST_BOSTON = "US East (Boston)"
    CHILE_SANTIAGO = "Chile (Santiago)"
    PERU_LIMA = "Peru (Lima)"
    AUSTRALIA_PERTH = "Australia (Perth)"
    MEXICO_QUERETARO = "Mexico (Queretaro)"
    US_WEST_HONOLULU = "US West (Honolulu)"
    NIGERIA_LAGOS = "Nigeria (Lagos)"
    PHILIPPINES_MANILA = "Philippines (Manila)"
    POLAND_WARSAW = "Poland (Warsaw)"
    TAIWAN_TAIPEI = "Taiwan (Taipei)"
    THAILAND_BANGKOK = "Thailand (Bangkok)"
    INDIA_KOLKATA = "India (Kolkata)"
    US_EAST_KANSAS_CITY_2 = "US East (Kansas City 2)"
    NEW_ZEALAND_AUCKLAND = "New Zealand (Auckland)"
    US_EAST_VERIZON_CHARLOTTE = "US East (Verizon) - Charlotte"
    US_EAST_VERIZON_NASHVILLE = "US East (Verizon) - Nashville"
    US_EAST_VERIZON_WASHINGTON_DC = "US East (Verizon) - Washington DC"
    DENMARK_COPENHAGEN = "Denmark (Copenhagen)"
    FINLAND_HELSINKI = "Finland (Helsinki)"
    GERMANY_HAMBURG = "Germany (Hamburg)"
    INDIA_DELHI = "India (Delhi)"
    OMAN_MUSCAT = "Oman (Muscat)"
    US_EAST_MINNEAPOLIS = "US East (Minneapolis)"
    US_WEST_LAS_VEGAS = "US West (Las Vegas)"
    US_WEST_PORTLAND = "US West (Portland)"
    US_WEST_SEATTLE = "US West (Seattle)"
    MOROCCO_CASABLANCA = "Morocco (Casablanca)"
    ASIA_PACIFIC_SKT_SEOUL = "Asia Pacific (SKT) - Seoul"
    CANADA_BELL_TORONTO = "Canada (BELL) - Toronto"
    EU_BRITISH_TELECOM_MANCHESTER = "EU (British Telecom) - Manchester"
    EU_VODAFONE_BERLIN = "EU (Vodafone) - Berlin"
    EU_VODAFONE_DORTMUND = "EU (Vodafone) - Dortmund"
    EU_VODAFONE_LONDON = "EU (Vodafone) - London"
    EU_VODAFONE_MANCHESTER = "EU (Vodafone) - Manchester"
    EU_VODAFONE_MUNICH = "EU (Vodafone) - Munich"
    US_EAST_VERIZON_CHICAGO = "US East (Verizon) - Chicago"
    US_EAST_VERIZON_DETROIT = "US East (Verizon) - Detroit"
    US_EAST_VERIZON_HOUSTON = "US East (Verizon) - Houston"
    US_EAST_VERIZON_MIAMI = "US East (Verizon) - Miami"
    US_EAST_VERIZON_MINNEAPOLIS = "US East (Verizon) - Minneapolis"
    US_EAST_VERIZON_TAMPA = "US East (Verizon) - Tampa"
    US_WEST_VERIZON_LOS_ANGELES = "US West (Verizon) - Los Angeles"
    US_WEST_VERIZON_PHOENIX = "US West (Verizon) - Phoenix"
    US_WEST_VERIZON_SAN_FRANCISCO_BAY_AREA = (
        "US West (Verizon) - San Francisco Bay Area"
    )
    ASIA_PACIFIC_KDDI_OSAKA = "Asia Pacific (KDDI) - Osaka"
    ASIA_PACIFIC_KDDI_TOKYO = "Asia Pacific (KDDI) - Tokyo"
    ASIA_PACIFIC_SKT_DAEJEON = "Asia Pacific (SKT) - Daejeon"
    US_EAST_VERIZON_ATLANTA = "US East (Verizon) - Atlanta"
    US_EAST_VERIZON_BOSTON = "US East (Verizon) - Boston"
    US_EAST_VERIZON_DALLAS = "US East (Verizon) - Dallas"
    US_EAST_VERIZON_NEW_YORK = "US East (Verizon) - New York"
    US_WEST_VERIZON_DENVER = "US West (Verizon) - Denver"
    US_WEST_VERIZON_LAS_VEGAS = "US West (Verizon) - Las Vegas"
    US_WEST_VERIZON_SEATTLE = "US West (Verizon) - Seattle"


class OperatingSystem(str, Enum):
    """Savings Plansのオペレーティングシステム"""

    LINUX = "Linux"
    RHEL = "RHEL"
    SUSE = "SUSE"
    RHEL_HA = "Red Hat Enterprise Linux with HA"
    WINDOWS = "Windows"
    UBUNTU_PRO = "Ubuntu Pro"
    WINDOWS_SQL_WEB = "Windows with SQL Web"
    LINUX_SQL_WEB = "Linux with SQL Web"
    LINUX_SQL_STD = "Linux with SQL Std"
    WINDOWS_SQL_STD = "Windows with SQL Std"
    BYOL = "BYOL"
    LINUX_SQL_ENT = "Linux with SQL Ent"
    WINDOWS_SQL_ENT = "Windows with SQL Ent"
    RHEL_SQL_STD = "RHEL with SQL Std"
    RHEL_HA_SQL_STD = "Red Hat Enterprise Linux with HA with SQL Std"
    RHEL_SQL_ENT = "RHEL with SQL Ent"
    RHEL_HA_SQL_ENT = "Red Hat Enterprise Linux with HA with SQL Ent"
    RHEL_SQL_WEB = "RHEL with SQL Web"


class Tenancy(str, Enum):
    """Savings Plansのテナンシー"""

    SHARED = "Shared"
    DEDICATED = "Dedicated"
    HOST = "Host"
