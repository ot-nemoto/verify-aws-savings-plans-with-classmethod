from enum import Enum


class Term(str, Enum):
    """Fargate Savings Plansの契約期間"""

    ONE_YEAR = "1 year"
    THREE_YEAR = "3 year"


class PaymentOption(str, Enum):
    """Fargate Savings Plansの支払いオプション"""

    ALL_UPFRONT = "All Upfront"
    PARTIAL_UPFRONT = "Partial Upfront"
    NO_UPFRONT = "No Upfront"


class Region(str, Enum):
    """Fargate Savings Plansのリージョン"""

    AFRICA_CAPE_TOWN = "Africa (Cape Town)"
    ASIA_PACIFIC_HONG_KONG = "Asia Pacific (Hong Kong)"
    ASIA_PACIFIC_HYDERABAD = "Asia Pacific (Hyderabad)"
    ASIA_PACIFIC_JAKARTA = "Asia Pacific (Jakarta)"
    ASIA_PACIFIC_MELBOURNE = "Asia Pacific (Melbourne)"
    ASIA_PACIFIC_MUMBAI = "Asia Pacific (Mumbai)"
    ASIA_PACIFIC_OSAKA = "Asia Pacific (Osaka)"
    ASIA_PACIFIC_SEOUL = "Asia Pacific (Seoul)"
    ASIA_PACIFIC_SINGAPORE = "Asia Pacific (Singapore)"
    ASIA_PACIFIC_SYDNEY = "Asia Pacific (Sydney)"
    ASIA_PACIFIC_TOKYO = "Asia Pacific (Tokyo)"
    CANADA_CENTRAL = "Canada (Central)"
    CANADA_WEST_CALGARY = "Canada West (Calgary)"
    EU_FRANKFURT = "EU (Frankfurt)"
    EU_IRELAND = "EU (Ireland)"
    EU_LONDON = "EU (London)"
    EU_MILAN = "EU (Milan)"
    EU_PARIS = "EU (Paris)"
    EU_SPAIN = "EU (Spain)"
    EU_STOCKHOLM = "EU (Stockholm)"
    EU_ZURICH = "EU (Zurich)"
    ISRAEL_TEL_AVIV = "Israel (Tel Aviv)"
    MIDDLE_EAST_BAHRAIN = "Middle East (Bahrain)"
    MIDDLE_EAST_UAE = "Middle East (UAE)"
    SOUTH_AMERICA_SAO_PAULO = "South America (Sao Paulo)"
    US_EAST_N_VIRGINIA = "US East (N. Virginia)"
    US_EAST_OHIO = "US East (Ohio)"
    US_WEST_N_CALIFORNIA = "US West (N. California)"
    US_WEST_OREGON = "US West (Oregon)"
    AWS_GOVCLOUD_US = "AWS GovCloud (US)"
    AWS_GOVCLOUD_US_EAST = "AWS GovCloud (US-East)"
    ASIA_PACIFIC_MALAYSIA = "Asia Pacific (Malaysia)"
    ASIA_PACIFIC_THAILAND = "Asia Pacific (Thailand)"
    MEXICO_CENTRAL = "Mexico (Central)"


class OperatingSystem(str, Enum):
    """Fargate Savings Plansのオペレーティングシステム"""

    LINUX = "Linux"
    WINDOWS = "Windows"


class CPUArchitecture(str, Enum):
    """Fargate Savings PlansのCPUアーキテクチャ"""

    X86 = "X86"
    ARM = "ARM"
