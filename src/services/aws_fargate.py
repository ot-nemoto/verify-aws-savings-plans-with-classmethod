from typing import Dict
from urllib.parse import quote

import requests
from rich.console import Console

from enums.aws_fargate import (
    CPUArchitecture,
    OperatingSystem,
    PaymentOption,
    Region,
    Term,
)

console = Console()


def get_discount_rate(
    term: Term = Term.ONE_YEAR,
    payment_option: PaymentOption = PaymentOption.PARTIAL_UPFRONT,
    region: Region = Region.ASIA_PACIFIC_TOKYO,
    operating_system: OperatingSystem = OperatingSystem.LINUX,
    cpu_architecture: CPUArchitecture = CPUArchitecture.X86,
) -> Dict[str, float]:
    """
    AWS FargateのSavings Plans割引率を取得します。

    AWSの公開APIを使用して、FargateのSavings Plans割引率を計算します。
    割引率は、通常価格に対するSavings Plans価格の割合から計算されます。

    Args:
        term (Term): 契約期間（1年または3年）
        payment_option (PaymentOption): 支払いオプション（全額前払い、一部前払い、前払いなし）
        region (Region): AWSリージョン
        operating_system (OperatingSystem): オペレーティングシステム
        cpu_architecture (CPUArchitecture): CPUアーキテクチャ
    Returns:
        Optional[float]: 割引率（0.0-1.0の範囲）またはNone（取得失敗時）
    """
    # URLを設定
    base_url = "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-savings-plan-fargate-with-arm"
    path_parameters = "/".join(
        [
            quote(term.value),
            quote(payment_option.value),
            quote(region.value),
            quote(operating_system.value),
            quote(cpu_architecture.value),
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
                float(value["price"]) / float(value["fargate:PricePerUnit"])
            )
            ret[key] = round(discount_rate, 4)

        if ret:
            return ret

        console.print("[yellow]割引率が見つかりませんでした。[/yellow]")
        return None

    except Exception as e:
        console.print(f"[red]割引率の取得中にエラーが発生しました:[/red] {str(e)}")
        return None
