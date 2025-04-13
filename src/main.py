import calendar
from enum import Enum
from typing import List, Union

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from enums.amazon_ec2 import (
    OperatingSystem as AmazonEc2OperatingSystem,
)
from enums.amazon_ec2 import (
    PaymentOption as AmazonEc2PaymentOption,
)
from enums.amazon_ec2 import (
    Region as AmazonEc2Region,
)
from enums.amazon_ec2 import (
    Tenancy as AmazonEc2Tenancy,
)
from enums.amazon_ec2 import (
    Term as AmazonEc2Term,
)
from enums.aws_fargate import (
    CPUArchitecture as AwsFargateCPUArchitecture,
)
from enums.aws_fargate import (
    OperatingSystem as AwsFargateOperatingSystem,
)
from enums.aws_fargate import (
    PaymentOption as AwsFargatePaymentOption,
)
from enums.aws_fargate import (
    Region as AwsFargateRegion,
)
from enums.aws_fargate import (
    Term as AwsFargateTerm,
)
from enums.aws_lambda import (
    PaymentOption as AwsLambdaPaymentOption,
)
from enums.aws_lambda import (
    Region as AwsLambdaRegion,
)
from enums.aws_lambda import (
    Term as AwsLambdaTerm,
)
from services.amazon_ec2 import get_discount_rate as get_amazon_ec2_discount_rate
from services.aws_fargate import get_discount_rate as get_aws_fargate_discount_rate
from services.aws_lambda import get_discount_rate as get_aws_lambda_discount_rate

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
    term: AmazonEc2Term = typer.Option(AmazonEc2Term.ONE_YEAR, help="契約期間"),
    payment_option: AmazonEc2PaymentOption = typer.Option(
        AmazonEc2PaymentOption.PARTIAL_UPFRONT, help="支払いオプション"
    ),
    region: AmazonEc2Region = typer.Option(
        AmazonEc2Region.ASIA_PACIFIC_TOKYO, help="リージョン"
    ),
    operating_system: AmazonEc2OperatingSystem = typer.Option(
        AmazonEc2OperatingSystem.LINUX, help="オペレーティングシステム"
    ),
    tenancy: AmazonEc2Tenancy = typer.Option(
        AmazonEc2Tenancy.SHARED, help="テナンシー"
    ),
    instance_type: str = typer.Option(
        None,
        help="EC2インスタンスタイプ（指定しない場合は全インスタンスタイプの割引率を表示）",
    ),
):
    """
    EC2 Savings Plansの割引率を取得する

    Args:
        term: 契約期間
        payment_option: 支払いオプション
        region: リージョン
        operating_system: オペレーティングシステム
        tenancy: テナンシー
        instance_type: EC2インスタンスタイプ（オプション）
    """
    discount_rate = get_amazon_ec2_discount_rate(
        instance_type=instance_type,
        term=term,
        payment_option=payment_option,
        region=region,
        operating_system=operating_system,
        tenancy=tenancy,
    )

    if discount_rate is not None:
        console.print(f"[blue]リージョン:[/blue] {region.value}")
        console.print(f"[blue]契約期間:[/blue] {term.value}")
        console.print(f"[blue]支払いオプション:[/blue] {payment_option.value}")
        console.print(f"[blue]OS:[/blue] {operating_system.value}")
        console.print(f"[blue]テナンシー:[/blue] {tenancy.value}")

        for key, value in discount_rate.items():
            console.print(f"[green]{key}:[/green] {value:.4f} ({value:.2%})")

    else:
        console.print("[red]割引率の取得に失敗しました。[/red]")


@app.command()
def aws_fargate_discount_rate(
    term: AwsFargateTerm = typer.Option(AwsFargateTerm.ONE_YEAR, help="契約期間"),
    payment_option: AwsFargatePaymentOption = typer.Option(
        AwsFargatePaymentOption.PARTIAL_UPFRONT, help="支払いオプション"
    ),
    region: AwsFargateRegion = typer.Option(
        AwsFargateRegion.ASIA_PACIFIC_TOKYO, help="リージョン"
    ),
    operating_system: AwsFargateOperatingSystem = typer.Option(
        AwsFargateOperatingSystem.LINUX, help="オペレーティングシステム"
    ),
    cpu_architecture: AwsFargateCPUArchitecture = typer.Option(
        AwsFargateCPUArchitecture.X86, help="CPUアーキテクチャ"
    ),
):
    """
    Fargate Savings Plansの割引率を取得する
    """
    discount_rate = get_aws_fargate_discount_rate(
        term=term,
        payment_option=payment_option,
        region=region,
        operating_system=operating_system,
        cpu_architecture=cpu_architecture,
    )

    if discount_rate is not None:
        console.print(f"[blue]リージョン:[/blue] {region.value}")
        console.print(f"[blue]契約期間:[/blue] {term.value}")
        console.print(f"[blue]支払いオプション:[/blue] {payment_option.value}")
        console.print(f"[blue]OS:[/blue] {operating_system.value}")
        console.print(f"[blue]CPUアーキテクチャ:[/blue] {cpu_architecture.value}")
        for key, value in discount_rate.items():
            console.print(f"[green]{key}:[/green] {value:.4f} ({value:.2%})")

    else:
        console.print("[red]割引率の取得に失敗しました。[/red]")


@app.command()
def aws_lambda_discount_rate(
    term: AwsLambdaTerm = typer.Option(
        AwsLambdaTerm.ONE_YEAR,
        help="契約期間",
    ),
    payment_option: AwsLambdaPaymentOption = typer.Option(
        AwsLambdaPaymentOption.PARTIAL_UPFRONT,
        help="支払いオプション",
    ),
    region: AwsLambdaRegion = typer.Option(
        AwsLambdaRegion.ASIA_PACIFIC_TOKYO,
        help="リージョン",
    ),
) -> None:
    """Lambda Savings Plansの割引率を取得する"""
    discount_rate = get_aws_lambda_discount_rate(
        term=term,
        payment_option=payment_option,
        region=region,
    )

    if discount_rate is not None:
        console.print(f"[blue]リージョン:[/blue] {region.value}")
        console.print(f"[blue]契約期間:[/blue] {term.value}")
        console.print(f"[blue]支払いオプション:[/blue] {payment_option.value}")
        for key, value in discount_rate.items():
            console.print(f"[green]{key}:[/green] {value:.4f} ({value:.2%})")

    else:
        console.print("[red]割引率の取得に失敗しました。[/red]")


if __name__ == "__main__":
    app()
