import csv
from pathlib import Path

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


def extract_usage(csv_file: str, usage_type: str, title: str, output_file: str = None, no_savings_plan: bool = False):
    """
    CSVファイルを読み込み、指定されたusage_typeを含む行を抽出します
    """
    console.print(f"[bold]ファイル処理中:[/bold] {csv_file}")

    try:
        # pandasでCSVを読み込む
        df = pd.read_csv(csv_file)

        # 'usage_type'列に指定された文字列が含まれる行をフィルタリング
        if 'usage_type' in df.columns:
            filtered_df = df[df['usage_type'].str.contains(
                usage_type, case=False, na=False)]

            # SavingsPlanNegationのフィルタリング
            if no_savings_plan:
                filtered_df = filtered_df[~filtered_df['item_description'].str.contains(
                    'SavingsPlanNegation', case=False, na=False)]

            # 結果があるか確認
            if filtered_df.empty:
                console.print("[yellow]該当する行は見つかりませんでした。[/yellow]")
                return

            # 指定された列のみを選択
            selected_columns = ['month', 'aws_account_id',
                                'usage_type', 'item_description', 'cost']
            filtered_df = filtered_df[selected_columns]

            # usage_typeとitem_descriptionでソート
            filtered_df = filtered_df.sort_values(
                ['usage_type', 'item_description'])

            # cost列のフォーマットを修正
            filtered_df['cost'] = filtered_df['cost'].apply(
                lambda x: f"{x:.10f}".rstrip('0').rstrip('.'))

            # 結果の表示
            console.print(
                f"[green]抽出された行数:[/green] {len(filtered_df)}")

            # テーブルで結果を表示
            table = Table(title=title)

            # 列の追加
            for column in filtered_df.columns:
                table.add_column(column)

            # 行の追加（最初の10行のみ表示）
            for _, row in filtered_df.head(10).iterrows():
                table.add_row(*[str(value) for value in row])

            console.print(table)

            # 出力ファイルが指定されている場合、結果を保存
            if output_file:
                filtered_df.to_csv(output_file, index=False)
                console.print(f"[green]結果を保存しました:[/green] {output_file}")
        else:
            console.print("[red]CSVファイルに 'usage_type' 列が見つかりません。[/red]")

    except Exception as e:
        console.print(f"[red]エラーが発生しました:[/red] {str(e)}")


@app.command()
def aws_fargate(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(None, help="出力ファイルのパス（指定しない場合は表示のみ）"),
    no_savings_plan: bool = typer.Option(False, help="SavingsPlanNegationを除外")
):
    """
    CSVファイルを読み込み、usage_typeにFargateが含まれる行を抽出します
    """
    title = "Fargate使用状況"
    extract_usage(csv_file, "Fargate", title, output_file, no_savings_plan)


@app.command()
def amazon_ec2(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(None, help="出力ファイルのパス（指定しない場合は表示のみ）"),
    no_savings_plan: bool = typer.Option(False, help="SavingsPlanNegationを除外")
):
    """
    CSVファイルを読み込み、usage_typeにBoxが含まれる行を抽出します
    """
    title = "EC2使用状況"
    extract_usage(csv_file, "Box", title, output_file, no_savings_plan)


@app.command()
def aws_lambda(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_file: str = typer.Option(None, help="出力ファイルのパス（指定しない場合は表示のみ）"),
    no_savings_plan: bool = typer.Option(False, help="SavingsPlanNegationを除外")
):
    """
    CSVファイルを読み込み、usage_typeにLambda-GBが含まれる行を抽出します
    """
    title = "Lambda使用状況"
    extract_usage(csv_file, "Lambda-GB", title, output_file, no_savings_plan)


@app.command()
def all(
    csv_file: str = typer.Argument(..., help="CSVファイルのパス"),
    output_dir: str = typer.Option(None, help="出力ディレクトリのパス（指定しない場合は表示のみ）"),
    no_savings_plan: bool = typer.Option(False, help="SavingsPlanNegationを除外")
):
    """
    CSVファイルを読み込み、Fargate、EC2、Lambdaの使用状況を一気に抽出します
    """
    # Fargateの抽出
    fargate_output = f"{output_dir}/fargate_usage.csv" if output_dir else None
    fargate_title = "Fargate使用状況"
    extract_usage(csv_file, "Fargate", fargate_title,
                  fargate_output, no_savings_plan)

    # EC2の抽出
    ec2_output = f"{output_dir}/ec2_usage.csv" if output_dir else None
    ec2_title = "EC2使用状況"
    extract_usage(csv_file, "Box", ec2_title, ec2_output, no_savings_plan)

    # Lambdaの抽出
    lambda_output = f"{output_dir}/lambda_usage.csv" if output_dir else None
    lambda_title = "Lambda使用状況"
    extract_usage(csv_file, "Lambda-GB", lambda_title,
                  lambda_output, no_savings_plan)


if __name__ == "__main__":
    app()
