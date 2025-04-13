from typing import Dict
from urllib.parse import quote

import requests
from rich.console import Console

from enums.aws_lambda import PaymentOption, Region, Term

console = Console()


def get_discount_rate(
    term: Term = Term.ONE_YEAR,
    payment_option: PaymentOption = PaymentOption.PARTIAL_UPFRONT,
    region: Region = Region.ASIA_PACIFIC_TOKYO,
) -> Dict[str, float]:
    """Lambda Savings Plansの割引率を取得する

    Args:
        term (Term, optional): 契約期間. Defaults to Term.ONE_YEAR.
        payment_option (PaymentOption, optional): 支払いオプション. Defaults to PaymentOption.NO_UPFRONT.
        region (Region, optional): リージョン. Defaults to Region.US_EAST_N_VIRGINIA.

    Returns:
        Dict[str, float]: 割引率の辞書
    """
    # APIのURLを構築
    base_url = "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-savings-plan-lambda"
    path_parameters = "/".join(
        [
            quote(term.value),
            quote(payment_option.value),
            quote(region.value),
        ]
    )
    url = f"{base_url}/{path_parameters}/index.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 割引率の計算
        ret = {}
        for key, value in data["regions"][region.value].items():
            discount_rate = 1 - (
                float(value["price"]) / float(value["lambda:PricePerUnit"])
            )
            ret[key] = round(discount_rate, 4)

        if ret:
            return ret

        console.print("[yellow]割引率が見つかりませんでした。[/yellow]")
        return None

    except Exception as e:
        console.print(f"[red]割引率の取得中にエラーが発生しました:[/red] {str(e)}")
        return None
