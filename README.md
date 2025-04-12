# AWS Savings Plans 検証ツール

このツールは、AWS Savings Plansの使用状況を分析し、最適な契約プランを提案するためのツールです。

## 機能

- AWS Cost and Usage Report (CUR)から使用状況データを抽出
- Fargate、EC2、Lambdaの使用状況を分析
- 割引率の計算
- 最適な契約プランの提案

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 使用状況データの抽出

```bash
# Fargateの使用状況を抽出
python main.py aws-fargate monthly-report-2024-12-123456789012.csv

# EC2の使用状況を抽出
python main.py amazon-ec2 monthly-report-2024-12-123456789012.csv

# Lambdaの使用状況を抽出
python main.py aws-lambda monthly-report-2024-12-123456789012.csv

# すべてのサービスの使用状況を抽出
python main.py all monthly-report-2024-12-123456789012.csv
```

### オプション

- `--output-file` または `--output-dir`: 結果をファイルに出力
- `--no-negation`: SavingsPlanNegationを除外
- `--group-by`: データのグループ化（usage_type, item_description）

### グループ化の例

```bash
# usage_typeでグループ化
python main.py aws-fargate monthly-report-2024-12-123456789012.csv --group-by usage_type

# item_descriptionでグループ化
python main.py amazon-ec2 monthly-report-2024-12-123456789012.csv --group-by item_description

# 両方でグループ化
python main.py aws-lambda monthly-report-2024-12-123456789012.csv --group-by usage_type --group-by item_description
```

### 割引率の計算

```bash
python main.py amazon-ec2-discount-rate t3.medium
```

### サポートされているパラメータ

- リージョン: 東京、大阪、バージニア北部など
- オペレーティングシステム: Linux、Windows、RHELなど
- テナンシー: 共有、専有、ホスト

## 出力例

### 使用状況データの抽出結果

```
Fargate使用状況
+------------+----------------+------------------+------------------+------------------+
| month      | aws_account_id | usage_type       | item_description | cost            |
+------------+----------------+------------------+------------------+------------------+
| 2024-12    | 123456789012  | Fargate-vCPU-Hrs | Fargate          | 0.0000000000    |
| 2024-12    | 123456789012  | Fargate-GB-Hrs   | Fargate          | 0.0000000000    |
+------------+----------------+------------------+------------------+------------------+
```

### 割引率の計算結果

```
割引率: 0.28 (28%)
契約期間: 1 year
支払いオプション: Partial Upfront
リージョン: Asia Pacific (Tokyo)
オペレーティングシステム: Linux
テナンシー: Shared
```

## 注意事項

- 割引率は、AWSの公開APIの価格情報に基づいています
- 価格改定により、割引率が変更される可能性があります
- 使用状況データは、AWS Cost and Usage Report (CUR)から取得する必要があります

## ライセンス

MIT