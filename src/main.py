import calendar
import glob
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
    MONTH = "month"


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
        group_by (List[GroupBy], optional): グループ化のキー（usage_type, item_description, month）

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

            # cost列を数値型に変換
            filtered_df["cost"] = pd.to_numeric(filtered_df["cost"], errors="coerce")

            # グループ化の処理
            if group_by:
                group_keys = ["aws_account_id"]
                if GroupBy.MONTH in group_by:
                    group_keys.append("month")
                if GroupBy.USAGE_TYPE in group_by:
                    group_keys.append("usage_type")
                if GroupBy.ITEM_DESCRIPTION in group_by:
                    group_keys.append("item_description")

                filtered_df = (
                    filtered_df.groupby(group_keys)["cost"].sum().reset_index()
                )

            # ソートキーの列が存在する場合のみソート
            sort_keys = []
            if "month" in filtered_df.columns:
                sort_keys.append("month")
            if "usage_type" in filtered_df.columns:
                sort_keys.append("usage_type")
            if "item_description" in filtered_df.columns:
                sort_keys.append("item_description")
            if sort_keys:
                filtered_df = filtered_df.sort_values(sort_keys)

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

    # cost列の表示形式を設定
    if "cost" in df.columns:
        df["cost"] = df["cost"].apply(lambda x: f"{x:.10f}".rstrip("0").rstrip("."))

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
    csv_files: List[str] = typer.Argument(
        ...,
        help="CSVファイルのパス（複数指定可、ワイルドカード使用可）",
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    only_negation: bool = typer.Option(
        False, help="SavingsPlanNegationのみを抽出するかどうか"
    ),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、usage_typeにFargateが含まれる行を抽出します

    Args:
        csv_files: CSVファイルのパス（複数指定可、ワイルドカード使用可）
        negation: SavingsPlanNegationを含めるかどうか
        only_negation: SavingsPlanNegationのみを抽出するかどうか
        group_by: グループ化のキー
        markdown: markdown形式で出力するかどうか
    """
    # ワイルドカードを展開してファイルリストを作成
    expanded_files = []
    for pattern in csv_files:
        matched_files = glob.glob(pattern)
        if not matched_files:
            console.print(
                f"[yellow]警告: パターン '{pattern}' に一致するファイルが見つかりませんでした。[/yellow]"
            )
        expanded_files.extend(matched_files)

    if not expanded_files:
        console.print("[red]有効なファイルが見つかりませんでした。[/red]")
        return

    # 複数のCSVファイルを結合
    all_data = []
    for csv_file in expanded_files:
        # グループ化を適用せずにデータを取得
        df = get_usage_data(csv_file, "Fargate", True, None)  # negationを常にTrueに設定
        if not df.empty:
            # only_negationが指定されている場合は、SavingsPlanNegationのみをフィルタリング
            if only_negation:
                df = df[
                    df["item_description"].str.contains(
                        "SavingsPlanNegation", case=False, na=False
                    )
                ]
            elif not negation:
                df = df[
                    ~df["item_description"].str.contains(
                        "SavingsPlanNegation", case=False, na=False
                    )
                ]
            all_data.append(df)

    if not all_data:
        console.print("[red]有効なデータが見つかりませんでした。[/red]")
        return

    # データフレームを結合
    combined_df = pd.concat(all_data, ignore_index=True)

    # 結合したデータに対してグループ化を適用
    if group_by:
        group_keys = ["aws_account_id"]
        if GroupBy.MONTH in group_by:
            group_keys.append("month")
        if GroupBy.USAGE_TYPE in group_by:
            group_keys.append("usage_type")
        if GroupBy.ITEM_DESCRIPTION in group_by:
            group_keys.append("item_description")

        combined_df = combined_df.groupby(group_keys)["cost"].sum().reset_index()

    display_usage(combined_df, "Fargate使用状況", markdown)


@app.command()
def amazon_ec2(
    csv_files: List[str] = typer.Argument(
        ...,
        help="CSVファイルのパス（複数指定可、ワイルドカード使用可）",
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    only_negation: bool = typer.Option(
        False, help="SavingsPlanNegationのみを抽出するかどうか"
    ),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、usage_typeにBoxが含まれる行を抽出します

    Args:
        csv_files: CSVファイルのパス（複数指定可、ワイルドカード使用可）
        negation: SavingsPlanNegationを含めるかどうか
        only_negation: SavingsPlanNegationのみを抽出するかどうか
        group_by: グループ化のキー
        markdown: markdown形式で出力するかどうか
    """
    # ワイルドカードを展開してファイルリストを作成
    expanded_files = []
    for pattern in csv_files:
        matched_files = glob.glob(pattern)
        if not matched_files:
            console.print(
                f"[yellow]警告: パターン '{pattern}' に一致するファイルが見つかりませんでした。[/yellow]"
            )
        expanded_files.extend(matched_files)

    if not expanded_files:
        console.print("[red]有効なファイルが見つかりませんでした。[/red]")
        return

    # 複数のCSVファイルを結合
    all_data = []
    for csv_file in expanded_files:
        # グループ化を適用せずにデータを取得
        df = get_usage_data(csv_file, "Box", True, None)  # negationを常にTrueに設定
        if not df.empty:
            # only_negationが指定されている場合は、SavingsPlanNegationのみをフィルタリング
            if only_negation:
                df = df[
                    df["item_description"].str.contains(
                        "SavingsPlanNegation", case=False, na=False
                    )
                ]
            elif not negation:
                df = df[
                    ~df["item_description"].str.contains(
                        "SavingsPlanNegation", case=False, na=False
                    )
                ]
            all_data.append(df)

    if not all_data:
        console.print("[red]有効なデータが見つかりませんでした。[/red]")
        return

    # データフレームを結合
    combined_df = pd.concat(all_data, ignore_index=True)

    # 結合したデータに対してグループ化を適用
    if group_by:
        group_keys = ["aws_account_id"]
        if GroupBy.MONTH in group_by:
            group_keys.append("month")
        if GroupBy.USAGE_TYPE in group_by:
            group_keys.append("usage_type")
        if GroupBy.ITEM_DESCRIPTION in group_by:
            group_keys.append("item_description")

        combined_df = combined_df.groupby(group_keys)["cost"].sum().reset_index()

    display_usage(combined_df, "EC2使用状況", markdown)


@app.command()
def aws_lambda(
    csv_files: List[str] = typer.Argument(
        ...,
        help="CSVファイルのパス（複数指定可、ワイルドカード使用可）",
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    only_negation: bool = typer.Option(
        False, help="SavingsPlanNegationのみを抽出するかどうか"
    ),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、usage_typeにLambda-GBが含まれる行を抽出します

    Args:
        csv_files: CSVファイルのパス（複数指定可、ワイルドカード使用可）
        negation: SavingsPlanNegationを含めるかどうか
        only_negation: SavingsPlanNegationのみを抽出するかどうか
        group_by: グループ化のキー
        markdown: markdown形式で出力するかどうか
    """
    # ワイルドカードを展開してファイルリストを作成
    expanded_files = []
    for pattern in csv_files:
        matched_files = glob.glob(pattern)
        if not matched_files:
            console.print(
                f"[yellow]警告: パターン '{pattern}' に一致するファイルが見つかりませんでした。[/yellow]"
            )
        expanded_files.extend(matched_files)

    if not expanded_files:
        console.print("[red]有効なファイルが見つかりませんでした。[/red]")
        return

    # 複数のCSVファイルを結合
    all_data = []
    for csv_file in expanded_files:
        # グループ化を適用せずにデータを取得
        df = get_usage_data(
            csv_file, "Lambda-GB", True, None
        )  # negationを常にTrueに設定
        if not df.empty:
            # only_negationが指定されている場合は、SavingsPlanNegationのみをフィルタリング
            if only_negation:
                df = df[
                    df["item_description"].str.contains(
                        "SavingsPlanNegation", case=False, na=False
                    )
                ]
            elif not negation:
                df = df[
                    ~df["item_description"].str.contains(
                        "SavingsPlanNegation", case=False, na=False
                    )
                ]
            all_data.append(df)

    if not all_data:
        console.print("[red]有効なデータが見つかりませんでした。[/red]")
        return

    # データフレームを結合
    combined_df = pd.concat(all_data, ignore_index=True)

    # 結合したデータに対してグループ化を適用
    if group_by:
        group_keys = ["aws_account_id"]
        if GroupBy.MONTH in group_by:
            group_keys.append("month")
        if GroupBy.USAGE_TYPE in group_by:
            group_keys.append("usage_type")
        if GroupBy.ITEM_DESCRIPTION in group_by:
            group_keys.append("item_description")

        combined_df = combined_df.groupby(group_keys)["cost"].sum().reset_index()

    display_usage(combined_df, "Lambda使用状況", markdown)


@app.command()
def all(
    csv_files: List[str] = typer.Argument(
        ...,
        help="CSVファイルのパス（複数指定可、ワイルドカード使用可）",
    ),
    negation: bool = typer.Option(True, help="SavingsPlanNegationを含めるかどうか"),
    only_negation: bool = typer.Option(
        False, help="SavingsPlanNegationのみを抽出するかどうか"
    ),
    group_by: List[GroupBy] = typer.Option(
        None, help="グループ化のキー（usage_type, item_description）"
    ),
    markdown: bool = typer.Option(False, help="markdown形式で出力するかどうか"),
):
    """
    CSVファイルを読み込み、Fargate、EC2、Lambdaの使用状況を一気に抽出します

    Args:
        csv_files: CSVファイルのパス（複数指定可、ワイルドカード使用可）
        negation: SavingsPlanNegationを含めるかどうか
        only_negation: SavingsPlanNegationのみを抽出するかどうか
        group_by: グループ化のキー
        markdown: markdown形式で出力するかどうか
    """
    # 各サービスの処理を実行
    services = [
        ("Fargate", aws_fargate),
        ("EC2", amazon_ec2),
        ("Lambda", aws_lambda),
    ]

    for service_name, command_func in services:
        console.print(f"\n[bold]{service_name}の処理を開始します[/bold]")
        command_func(
            csv_files=csv_files,
            negation=negation,
            only_negation=only_negation,
            group_by=group_by,
            markdown=markdown,
        )


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
    memory: bool = typer.Option(False, "--memory", help="メモリの割引率を表示"),
    cpu: bool = typer.Option(False, "--cpu", help="CPUの割引率を表示"),
):
    """
    Fargate Savings Plansの割引率を取得する

    Args:
        term: 契約期間
        payment_option: 支払いオプション
        region: リージョン
        operating_system: オペレーティングシステム
        cpu_architecture: CPUアーキテクチャ
        memory: メモリの割引率のみを表示
        cpu: CPUの割引率のみを表示
    """
    discount_rate = get_aws_fargate_discount_rate(
        term=term,
        payment_option=payment_option,
        region=region,
        operating_system=operating_system,
        cpu_architecture=cpu_architecture,
        is_memory=True if not any([memory, cpu]) else memory,
        is_cpu=True if not any([memory, cpu]) else cpu,
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
