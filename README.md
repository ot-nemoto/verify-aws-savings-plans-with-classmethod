# AWS Savings Plans 検証ツール

このツールは、AWSの利用状況レポート（CSV）から、Fargate、EC2、Lambdaの使用状況を抽出し、Savings Plansの適用状況を確認するためのものです。

## 機能

- Fargate、EC2、Lambdaの使用状況を抽出
- Savings Plansの適用状況（SavingsPlanNegation）の確認
- 使用状況のソート（usage_type, item_description）
- CSVファイルへの出力

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本的な使用方法

```bash
python main.py all <CSVファイル>
```

### オプション

- `--no-savings-plan`: SavingsPlanNegationを除外して表示
- `--output-dir <ディレクトリ>`: 結果をCSVファイルとして出力

### 例

```bash
# すべての使用状況を表示
python main.py all monthly-report-2024-12-540638230969.csv

# SavingsPlanNegationを除外して表示
python main.py all monthly-report-2024-12-540638230969.csv --no-savings-plan

# 結果をCSVファイルとして出力
python main.py all monthly-report-2024-12-540638230969.csv --output-dir output
```

## 出力形式

出力は以下の列を含むテーブル形式で表示されます：

- month: 月
- aws_account_id: AWSアカウントID
- usage_type: 使用タイプ
- item_description: アイテムの説明
- cost: コスト

## 注意事項

- CSVファイルはGitの管理対象外です（`.gitignore`に設定済み）
- 出力ディレクトリもGitの管理対象外です（`.gitignore`に設定済み）

## ライセンス

MIT