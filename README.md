# AWS Savings Plans 検証ツール

このツールは、AWS Savings Plansの使用状況を分析し、最適な契約プランを提案するためのツールです。

## 機能

- AWS Cost and Usage Report (CUR)から使用状況データを抽出
- Fargate、EC2、Lambdaの使用状況を分析
- 割引率の計算と表示（通常形式またはmarkdown形式）
- 複数のCSVファイルの一括処理（ワイルドカード対応）

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 使用状況データの抽出

```bash
# Fargateの使用状況を抽出（単一ファイル）
python src/main.py aws-fargate -f monthly-report-2024-12-123456789012.csv

# 複数のCSVファイルを指定（ワイルドカード使用）
python src/main.py aws-fargate -f "528051582013/*.csv" -f "540638230969/*.csv"

# 特定の月のファイルを指定
python src/main.py aws-fargate -f "528051582013/monthly-report-2024-*.csv"

# EC2の使用状況を抽出
python src/main.py amazon-ec2 -f monthly-report-2024-12-123456789012.csv

# Lambdaの使用状況を抽出
python src/main.py aws-lambda -f monthly-report-2024-12-123456789012.csv
```

### オプション

- `--no-negation`: SavingsPlanNegationを除外
- `--only-negation`: SavingsPlanNegationのみを抽出
- `--group-by`: データのグループ化（month, usage_type, item_description）
- `--markdown`: 結果をmarkdown形式で出力

### グループ化の例

```bash
# 月でグループ化
python src/main.py aws-fargate -f "*.csv" --group-by month

# 使用タイプでグループ化
python src/main.py aws-fargate -f "*.csv" --group-by usage_type

# 複数条件でグループ化
python src/main.py aws-fargate -f "*.csv" --group-by month --group-by usage_type
```

### 割引率の計算

```bash
# EC2の割引率を表示（全インスタンスタイプ）
python src/main.py amazon-ec2-discount-rate

# 特定のインスタンスタイプの割引率を表示
python src/main.py amazon-ec2-discount-rate -i t3.medium

# Fargateの割引率を表示
python src/main.py aws-fargate-discount-rate

# Lambdaの割引率を表示
python src/main.py aws-lambda-discount-rate
```

### 割引率の計算結果

```
リージョン: Asia Pacific (Tokyo)
契約期間: 1 year
支払いオプション: Partial Upfront

t3.medium: 0.2800 (28.00%)
```

### サポートされているパラメータ

#### 共通
- 契約期間: 1年、3年
- 支払いオプション: 全額前払い、一部前払い、前払いなし
- リージョン: 東京、大阪、バージニア北部など

#### EC2固有
- オペレーティングシステム: Linux、Windows、RHELなど
- テナンシー: 共有、専有、ホスト
- インスタンスタイプ: オプショナル（指定しない場合は全タイプ）

## 出力例

### 使用状況データの抽出結果

```
Fargate使用状況
+------------+----------------+------------------+------------------+------------------+
| month      | aws_account_id | usage_type       | item_description | cost            |
+------------+----------------+------------------+------------------+------------------+
| 2024-12    | 123456789012  | Fargate-vCPU-Hrs | Fargate          | 123.4567        |
| 2024-12    | 123456789012  | Fargate-GB-Hrs   | Fargate          | 45.6789         |
+------------+----------------+------------------+------------------+------------------+
```

## 注意事項

- 割引率は、AWSの公開APIの価格情報に基づいています
- 価格改定により、割引率が変更される可能性があります
- 使用状況データは、AWS Cost and Usage Report (CUR)から取得する必要があります
- ワイルドカードを使用する場合は、パターンを引用符で囲む必要があります

## ライセンス

MIT