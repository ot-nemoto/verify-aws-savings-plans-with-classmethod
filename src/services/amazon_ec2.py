from typing import Optional
from urllib.parse import quote

import requests
from rich.console import Console

from enums.amazon_ec2 import OperatingSystem, PaymentOption, Region, Tenancy, Term

console = Console()


def get_discount_rate(
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
