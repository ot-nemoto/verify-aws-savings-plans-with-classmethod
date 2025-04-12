import calendar
from enum import Enum
from typing import List, Optional
from urllib.parse import quote

import pandas as pd
import requests
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


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


class GroupBy(str, Enum):
    USAGE_TYPE = "usage_type"
    ITEM_DESCRIPTION = "item_description"


def get_days_in_month(month_str: str) -> int:
    """
    年月文字列（YYYY-MM）からその月の日数を返します

    Args:
        month_str (str): 年月文字列（YYYY-MM形式）

    Returns:
        int: その月の日数
    """
    try:
        year, month = map(int, month_str.split("-"))
        return calendar.monthrange(year, month)[1]
    except (ValueError, IndexError):
        console.print(f"[red]無効な年月形式です: {month_str}[/red]")
        return 0


def get_compute_savings_plans_ec2_discount_rate(
    instance_type: str,
    term: Term = Term.ONE_YEAR,
    payment_option: PaymentOption = PaymentOption.NO_UPFRONT,
    region: Region = Region.ASIA_PACIFIC_TOKYO,
    operating_system: OperatingSystem = OperatingSystem.LINUX,
    tenancy: Tenancy = Tenancy.SHARED,
) -> Optional[float]:
    """
    AWS EC2インスタンスのSavings Plans割引率を取得します。

    AWSの公開APIを使用して、指定されたEC2インスタンスタイプのSavings Plans割引率を計算します。
    割引率は、通常価格に対するSavings Plans価格の割合から計算されます。

    Args:
        instance_type (str): EC2インスタンスタイプ
        term (Term): 契約期間（1年または3年）
        payment_option (PaymentOption): 支払いオプション（全額前払い、一部前払い、前払いなし）
        region (Region): AWSリージョン
        operating_system (OperatingSystem): オペレーティングシステム
        tenancy (Tenancy): テナンシー（共有、専有、ホスト）

    Returns:
        Optional[float]: 割引率（0.0-1.0の範囲）またはNone（取得失敗時）

    Examples:
        >>> get_compute_savings_plans_ec2_discount_rate("t3.medium")
        0.28  # 28%の割引率

    Note:
        - 割引率は、1 - (Savings Plans価格 / 通常価格) で計算されます
        - インスタンスタイプが見つからない場合はNoneを返します
        - APIリクエストに失敗した場合はNoneを返します
    """
    # URLのパラメータを設定
    params = {
        "term": term.value,
        "payment_option": payment_option.value,
        "region": region.value,
        "os": operating_system.value,
        "tenancy": tenancy.value,
    }

    # パラメータをエンコード
    encoded_params = {k: quote(v) for k, v in params.items()}

    base_url = "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-savings-plan-ec2"
    path = "/".join(
        [
            encoded_params["term"],
            encoded_params["payment_option"],
            encoded_params["region"],
            encoded_params["os"],
            encoded_params["tenancy"],
            "index.json",
        ]
    )
    url = f"{base_url}/{path}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # インスタンスタイプの検索
        for instance_data in data["regions"][region.value].values():
            if instance_data["ec2:InstanceType"] == instance_type:
                original_price = float(instance_data["ec2:PricePerUnit"])
                savings_plan_price = float(instance_data["price"])
                discount_rate = 1 - (savings_plan_price / original_price)
                return round(discount_rate, 4)

        console.print(
            f"[yellow]インスタンスタイプ {instance_type} の割引率が見つかりませんでした。[/yellow]"
        )
        return None

    except Exception as e:
        console.print(f"[red]割引率の取得中にエラーが発生しました:[/red] {str(e)}")
        return None


def create_usage_table(df: pd.DataFrame, title: str) -> Table:
    """
    使用状況のテーブルを作成します。

    Args:
        df (pd.DataFrame): 使用状況データ
        title (str): テーブルのタイトル

    Returns:
        Table: 作成されたテーブル
    """
    table = Table(title=title)

    # 列の追加
    for column in df.columns:
        table.add_column(column)

    # 行の追加
    for _, row in df.iterrows():
        table.add_row(*[str(value) for value in row])

    return table


def get_usage_data(
    csv_file: str,
    usage_type: str,
    no_negation: bool = False,
    group_by: List[GroupBy] = None,
) -> pd.DataFrame:
    """
    CSVファイルから指定されたusage_typeの使用状況データを取得します

    Args:
        csv_file (str): CSVファイルのパス
        usage_type (str): 抽出するusage_type
        no_negation (bool, optional): SavingsPlanNegationを除外するかどうか
        group_by (List[GroupBy], optional): グループ化のキー（usage_type, item_description）

    Returns:
        pd.DataFrame: 使用状況データ
    """
    console.print(f"[bold]ファイル処理中:[/bold] {csv_file}")

    try:
        # pandasでCSVを読み込む
        df = pd.read_csv(csv_file)

        # 'usage_type'列に指定された文字列が含まれる行をフィルタリング
        if "usage_type" in df.columns:
            filtered_df = df[
                df["usage_type"].str.contains(usage_type, case=False, na=False)
            ]

            # SavingsPlanNegationのフィルタリング
            if no_negation:
                filtered_df = filtered_df[
                    ~filtered_df["item_description"].str.contains(
                        "SavingsPlanNegation", case=False, na=False
                    )
                ]

            # 結果があるか確認
            if filtered_df.empty:
                console.print("[yellow]該当する行は見つかりませんでした。[/yellow]")
                return pd.DataFrame()

            # 指定された列のみを選択
            selected_columns = [
                "month",
                "aws_account_id",
                "usage_type",
                "item_description",
                "cost",
            ]
            filtered_df = filtered_df[selected_columns]

            # グループ化の処理
            if group_by:
                group_keys = ["month", "aws_account_id"]
                if GroupBy.USAGE_TYPE in group_by:
                    group_keys.append("usage_type")
                if GroupBy.ITEM_DESCRIPTION in group_by:
                    group_keys.append("item_description")

                filtered_df = (
                    filtered_df.groupby(group_keys)["cost"].sum().reset_index()
                )

                # グループ化されていない列に「合計」を設定
                if GroupBy.USAGE_TYPE not in group_by:
                    filtered_df["usage_type"] = "合計"
                if GroupBy.ITEM_DESCRIPTION not in group_by:
                    filtered_df["item_description"] = "合計"

            # usage_typeとitem_descriptionでソート
            filtered_df = filtered_df.sort_values(["usage_type", "item_description"])

            # cost列のフォーマットを修正
            filtered_df["cost"] = filtered_df["cost"].apply(
                lambda x: f"{x:.10f}".rstrip("0").rstrip(".")
            )

            return filtered_df
        else:
            console.print("[red]CSVファイルに 'usage_type' 列が見つかりません。[/red]")
            return pd.DataFrame()

    except Exception as e:
        console.print(f"[red]エラーが発生しました:[/red] {str(e)}")
        return pd.DataFrame()


def display_usage(df: pd.DataFrame, title: str):
    """
    使用状況データを表示します

    Args:
        df (pd.DataFrame): 使用状況データ
        title (str): 表示するタイトル
    """
    if df.empty:
        return

    # 結果の表示
    console.print(f"[green]抽出された行数:[/green] {len(df)}")

    # テーブルを作成して表示
    table = create_usage_table(df, title)
    console.print(table)


@app.command()
def aws_fargate(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(
        None, help="出力ファイルのパス（指定しない場合は表示のみ）"
    ),
    no_negation: bool = typer.Option(False, help="SavingsPlanNegationを除外"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
):
    """
    CSVファイルを読み込み、usage_typeにFargateが含まれる行を抽出します
    """
    title = "Fargate使用状況"
    df = get_usage_data(csv_file, "Fargate", no_negation, group_by)

    if output_file:
        df.to_csv(output_file, index=False)
        console.print(f"[green]結果を保存しました:[/green] {output_file}")
    else:
        display_usage(df, title)


@app.command()
def amazon_ec2(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(
        None, help="出力ファイルのパス（指定しない場合は表示のみ）"
    ),
    no_negation: bool = typer.Option(False, help="SavingsPlanNegationを除外"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
):
    """
    CSVファイルを読み込み、usage_typeにBoxが含まれる行を抽出します
    """
    title = "EC2使用状況"
    df = get_usage_data(csv_file, "Box", no_negation, group_by)

    if output_file:
        df.to_csv(output_file, index=False)
        console.print(f"[green]結果を保存しました:[/green] {output_file}")
    else:
        display_usage(df, title)


@app.command()
def aws_lambda(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(
        None, help="出力ファイルのパス（指定しない場合は表示のみ）"
    ),
    no_negation: bool = typer.Option(False, help="SavingsPlanNegationを除外"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
):
    """
    CSVファイルを読み込み、usage_typeにLambda-GBが含まれる行を抽出します
    """
    title = "Lambda使用状況"
    df = get_usage_data(csv_file, "Lambda-GB", no_negation, group_by)

    if output_file:
        df.to_csv(output_file, index=False)
        console.print(f"[green]結果を保存しました:[/green] {output_file}")
    else:
        display_usage(df, title)


@app.command()
def all(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_dir: str = typer.Option(
        None, help="出力ディレクトリのパス（指定しない場合は表示のみ）"
    ),
    no_negation: bool = typer.Option(False, help="SavingsPlanNegationを除外"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
):
    """
    CSVファイルを読み込み、Fargate、EC2、Lambdaの使用状況を一気に抽出します
    """
    # Fargateの抽出
    fargate_output = f"{output_dir}/fargate_usage.csv" if output_dir else None
    fargate_title = "Fargate使用状況"
    fargate_df = get_usage_data(csv_file, "Fargate", no_negation, group_by)
    if fargate_output:
        fargate_df.to_csv(fargate_output, index=False)
        console.print(f"[green]Fargateの結果を保存しました:[/green] {fargate_output}")
    else:
        display_usage(fargate_df, fargate_title)

    # EC2の抽出
    ec2_output = f"{output_dir}/ec2_usage.csv" if output_dir else None
    ec2_title = "EC2使用状況"
    ec2_df = get_usage_data(csv_file, "Box", no_negation, group_by)
    if ec2_output:
        ec2_df.to_csv(ec2_output, index=False)
        console.print(f"[green]EC2の結果を保存しました:[/green] {ec2_output}")
    else:
        display_usage(ec2_df, ec2_title)

    # Lambdaの抽出
    lambda_output = f"{output_dir}/lambda_usage.csv" if output_dir else None
    lambda_title = "Lambda使用状況"
    lambda_df = get_usage_data(csv_file, "Lambda-GB", no_negation, group_by)
    if lambda_output:
        lambda_df.to_csv(lambda_output, index=False)
        console.print(f"[green]Lambdaの結果を保存しました:[/green] {lambda_output}")
    else:
        display_usage(lambda_df, lambda_title)


@app.command()
def amazon_ec2_discount_rate(
    instance_type: str = typer.Argument(..., help="EC2インスタンスタイプ"),
    term: Term = typer.Option(Term.ONE_YEAR, help="契約期間"),
    payment_option: PaymentOption = typer.Option(
        PaymentOption.PARTIAL_UPFRONT, help="支払いオプション"
    ),
    region: Region = typer.Option(Region.ASIA_PACIFIC_TOKYO, help="リージョン"),
    operating_system: OperatingSystem = typer.Option(
        OperatingSystem.LINUX, help="オペレーティングシステム"
    ),
    tenancy: Tenancy = typer.Option(Tenancy.SHARED, help="テナンシー"),
):
    """
    Savings Plansの割引率を取得する
    """
    discount_rate = get_compute_savings_plans_ec2_discount_rate(
        instance_type=instance_type,
        term=term,
        payment_option=payment_option,
        region=region,
        operating_system=operating_system,
        tenancy=tenancy,
    )

    if discount_rate is not None:
        console.print(
            f"[green]割引率:[/green] {discount_rate:.4f} ({discount_rate:.2%})"
        )
        console.print(f"[blue]契約期間:[/blue] {term.value}")
        console.print(f"[blue]支払いオプション:[/blue] {payment_option.value}")
        console.print(f"[blue]リージョン:[/blue] {region.value}")
        console.print(
            f"[blue]オペレーティングシステム:[/blue] {operating_system.value}"
        )
        console.print(f"[blue]テナンシー:[/blue] {tenancy.value}")
    else:
        console.print("[red]割引率の取得に失敗しました。[/red]")


if __name__ == "__main__":
    app()
