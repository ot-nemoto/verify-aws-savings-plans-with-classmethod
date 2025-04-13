import calendar
from enum import Enum
from typing import List, Optional, Union
from urllib.parse import quote

import pandas as pd
import requests
import typer
from rich.console import Console
from rich.table import Table

from enums.amazon_ec2 import (
    OperatingSystem,
    PaymentOption,
    Region,
    Tenancy,
    Term,
)

app = typer.Typer()
console = Console()


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


def create_usage_table(
    df: pd.DataFrame, title: str, markdown: bool = False
) -> Union[Table, str]:
    """
    使用状況のテーブルを作成します。

    Args:
        df (pd.DataFrame): 使用状況データ
        title (str): テーブルのタイトル
        markdown (bool): markdown形式で出力するかどうか

    Returns:
        Union[Table, str]: 作成されたテーブルまたはmarkdown形式の文字列
    """
    if markdown:
        # markdown形式で出力
        markdown_lines = []
        markdown_lines.append(f"## {title}\n")

        # ヘッダー行
        headers = df.columns.tolist()
        markdown_lines.append("| " + " | ".join(headers) + " |")
        markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # データ行
        for _, row in df.iterrows():
            markdown_lines.append("| " + " | ".join(str(value) for value in row) + " |")

        return "\n".join(markdown_lines)
    else:
        # rich.table形式で出力
        table = Table(title=title)
        for column in df.columns:
            table.add_column(column)
        for _, row in df.iterrows():
            table.add_row(*[str(value) for value in row])
        return table


def get_usage_data(
    csv_file: str,
    usage_type: str,
    negation: bool = True,
    group_by: List[GroupBy] = None,
) -> pd.DataFrame:
    """
    CSVファイルから指定されたusage_typeの使用状況データを取得します

    Args:
        csv_file (str): CSVファイルのパス
        usage_type (str): 抽出するusage_type
        negation (bool, optional): SavingsPlanNegationを含めるかどうか
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
            if not negation:
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
                "aws_account_id",
                "month",
                "usage_type",
                "item_description",
                "cost",
            ]
            filtered_df = filtered_df[selected_columns]

            # グループ化の処理
            if group_by:
                group_keys = ["aws_account_id", "month"]
                if GroupBy.USAGE_TYPE in group_by:
                    group_keys.append("usage_type")
                if GroupBy.ITEM_DESCRIPTION in group_by:
                    group_keys.append("item_description")

                filtered_df = (
                    filtered_df.groupby(group_keys)["cost"].sum().reset_index()
                )

            # ソートキーの列が存在する場合のみソート
            sort_keys = []
            if "usage_type" in filtered_df.columns:
                sort_keys.append("usage_type")
            if "item_description" in filtered_df.columns:
                sort_keys.append("item_description")
            if sort_keys:
                filtered_df = filtered_df.sort_values(sort_keys)

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


def display_usage(df: pd.DataFrame, title: str, markdown: bool = False):
    """
    使用状況データを表示します

    Args:
        df (pd.DataFrame): 使用状況データ
        title (str): 表示するタイトル
        markdown (bool): markdown形式で出力するかどうか
    """
    if df.empty:
        return

    # 結果の表示
    console.print(f"[green]抽出された行数:[/green] {len(df)}")

    # テーブルを作成して表示
    if markdown:
        markdown_table = create_usage_table(df, title, markdown=True)
        # markdownのソースを直接出力
        console.print(markdown_table)
    else:
        table = create_usage_table(df, title)
        console.print(table)


@app.command()
def aws_fargate(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(
        None, help="出力ファイルのパス（指定しない場合は表示のみ）"
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、usage_typeにFargateが含まれる行を抽出します
    """
    title = "Fargate使用状況"
    df = get_usage_data(csv_file, "Fargate", negation, group_by)

    if output_file:
        df.to_csv(output_file, index=False)
        console.print(f"[green]結果を保存しました:[/green] {output_file}")
    else:
        display_usage(df, title, markdown)


@app.command()
def amazon_ec2(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(
        None, help="出力ファイルのパス（指定しない場合は表示のみ）"
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、usage_typeにBoxが含まれる行を抽出します
    """
    title = "EC2使用状況"
    df = get_usage_data(csv_file, "Box", negation, group_by)

    if output_file:
        df.to_csv(output_file, index=False)
        console.print(f"[green]結果を保存しました:[/green] {output_file}")
    else:
        display_usage(df, title, markdown)


@app.command()
def aws_lambda(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(
        None, help="出力ファイルのパス（指定しない場合は表示のみ）"
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、usage_typeにLambda-GBが含まれる行を抽出します
    """
    title = "Lambda使用状況"
    df = get_usage_data(csv_file, "Lambda-GB", negation, group_by)

    if output_file:
        df.to_csv(output_file, index=False)
        console.print(f"[green]結果を保存しました:[/green] {output_file}")
    else:
        display_usage(df, title, markdown)


@app.command()
def all(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_dir: str = typer.Option(
        None, help="出力ディレクトリのパス（指定しない場合は表示のみ）"
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、Fargate、EC2、Lambdaの使用状況を一気に抽出します
    """
    # Fargateの抽出
    fargate_output = f"{output_dir}/fargate_usage.csv" if output_dir else None
    fargate_title = "Fargate使用状況"
    fargate_df = get_usage_data(csv_file, "Fargate", negation, group_by)
    if fargate_output:
        fargate_df.to_csv(fargate_output, index=False)
        console.print(f"[green]Fargateの結果を保存しました:[/green] {fargate_output}")
    else:
        display_usage(fargate_df, fargate_title, markdown)

    # EC2の抽出
    ec2_output = f"{output_dir}/ec2_usage.csv" if output_dir else None
    ec2_title = "EC2使用状況"
    ec2_df = get_usage_data(csv_file, "Box", negation, group_by)
    if ec2_output:
        ec2_df.to_csv(ec2_output, index=False)
        console.print(f"[green]EC2の結果を保存しました:[/green] {ec2_output}")
    else:
        display_usage(ec2_df, ec2_title, markdown)

    # Lambdaの抽出
    lambda_output = f"{output_dir}/lambda_usage.csv" if output_dir else None
    lambda_title = "Lambda使用状況"
    lambda_df = get_usage_data(csv_file, "Lambda-GB", negation, group_by)
    if lambda_output:
        lambda_df.to_csv(lambda_output, index=False)
        console.print(f"[green]Lambdaの結果を保存しました:[/green] {lambda_output}")
    else:
        display_usage(lambda_df, lambda_title, markdown)


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
