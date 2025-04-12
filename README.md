# AWS Savings Plans 検証ツール

このツールは、AWS Savings Plansの利用状況を分析し、最適な契約プランを提案するためのツールです。

## 機能

- AWS Cost and Usage Report (CUR) から利用データを抽出
- Fargate、EC2、Lambdaの利用状況を分析
- Savings Plansの割引率を計算
- 最適な契約プランを提案

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 利用データの抽出

```bash
python main.py all <cur_file_path>
```

### Savings Plansの割引率計算

```bash
python main.py test-savings-plans <instance_type> [--term {1 year,3 year}] [--payment-option {All Upfront,Partial Upfront,No Upfront}] [--region <region>] [--operating-system <os>] [--tenancy {Shared,Dedicated,Host}]
```

例：
```bash
# t3.mediumインスタンスの1年契約、前払いなしの割引率を計算
python main.py test-savings-plans t3.medium

# t3.mediumインスタンスの3年契約、全額前払いの割引率を計算
python main.py test-savings-plans t3.medium --term "3 year" --payment-option "All Upfront"

# Windows OS、専有テナンシーの割引率を計算
python main.py test-savings-plans t3.medium --operating-system "Windows" --tenancy "Dedicated"
```

### サポートされているパラメータ

#### リージョン
- US East (N. Virginia)
- US West (Oregon)
- EU (Ireland)
- Asia Pacific (Tokyo)
- その他多数のリージョン

#### オペレーティングシステム
- Linux
- RHEL
- SUSE
- Red Hat Enterprise Linux with HA
- Windows
- Ubuntu Pro
- Windows with SQL Web
- Linux with SQL Web
- その他多数のOS

#### テナンシー
- Shared
- Dedicated
- Host

## 出力例

### 利用データの抽出結果

```
Fargate Usage:
┌─────────┬─────────────────┬──────────────────────────────┬──────────────────────────────────────┬──────────┐
│ Month   │ AWS Account ID  │ Usage Type                   │ Item Description                     │ Cost     │
├─────────┼─────────────────┼──────────────────────────────┼──────────────────────────────────────┼──────────┤
│ 2024-12 │ 123456789012    │ Fargate-vCPU-Hours:perCPU    │ Amazon Elastic Container Service     │ $0.00    │
└─────────┴─────────────────┴──────────────────────────────┴──────────────────────────────────────┴──────────┘

EC2 Usage:
┌─────────┬─────────────────┬──────────────────────────────┬──────────────────────────────────────┬──────────┐
│ Month   │ AWS Account ID  │ Usage Type                   │ Item Description                     │ Cost     │
├─────────┼─────────────────┼──────────────────────────────┼──────────────────────────────────────┼──────────┤
│ 2024-12 │ 123456789012    │ BoxUsage:t3.medium          │ Amazon Elastic Compute Cloud         │ $0.00    │
└─────────┴─────────────────┴──────────────────────────────┴──────────────────────────────────────┴──────────┘
```

### 割引率計算結果

```
割引率: 0.28 (28%)
```

## 注意事項

- 割引率は、AWSの公開APIから取得した価格情報に基づいて計算されます
- 実際の割引率は、AWSの価格改定により変更される可能性があります
- 計算結果は参考値としてご利用ください

## ライセンス

MIT