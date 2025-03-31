# kouchou-ai-server
kouchou-aiのAPIサーバーです。
レポートの作成、取得などを行うことができます。

## 開発環境

* rye
* python 3.12
* OpenAI API Key


## セットアップ（開発環境）
プロジェクトのルートディレクトリ（kouchou-ai/）にまだ.envがない場合は、kouchou-ai/で以下のコマンドを実行し、.envファイル内の環境変数を記載してください。
すでに.envがある場合は、最新のenv.exampleと比較して、欠けている内容があれば追加してください。
```bash
cp .env.example .env
```
ユーザーが独自に設定すべき環境変数は現状以下の1つ
* OPENAI_API_KEY
  * OpenAIのAPIキー。レポート作成時に利用。

※ APIキーは他人と共有しないでください。GithubやSlackにもアップロードしないよう注意してください。  
※ このキーを設定しなくてもサーバーは起動しますが、/admin/reportsなど一部のエンドポイントでエラーになります。  
※ APIキーを設定してレポート作成などを行うと、OpenAI APIの使用料金が発生します。料金はOpenAIの[公式ドキュメント](https://openai.com/ja-JP/api/pricing/)を参照してください。  
※ OpenAI APIを使用しない機能は無料で利用できます（通常のインターネット利用の通信料等は除く）。

## 起動
プロジェクトのルートディレクトリ（kouchou-ai/）で以下のコマンドを実行してください。
```bash
docker compose up api
```

起動後、 `http://localhost:8000/docs` でSwagger UIが立ち上がるので、
そちらでAPIの動作を確認できます。

## 認証が必要なエンドポイントについて

一部のエンドポイントでは、**APIキーによる認証**が必要です。  
APIキーには **管理者用** と **公開用** の2種類があります。

### 1. 管理者用APIキー
`/admin/reports` などの管理者向けエンドポイントは、**管理者用APIキー** が必要です。  
Swagger UI 右上の **Authorize** ボタンをクリックし、`.env` ファイルで設定した `ADMIN_API_KEY` を入力してください。

このキーを入力すると、レポート作成やコメントデータの取得など、管理者向けの操作が可能になります。

### 2. 公開用APIキー
`/reports` や `/reports/{slug}` などのエンドポイントは、**公開用APIキー** が必要です。  
同じく Swagger UI の **Authorize** ボタンから、`.env` ファイルで設定した `PUBLIC_API_KEY` を入力してください。

このキーを入力することで、作成済みのレポート一覧や特定のレポートデータを取得できます。

### 注意事項
- APIキーが未入力、または無効な場合は **401 Unauthorized** エラーになります。

## 開発用Tips
- **ホットリロード対応**  
  `server` フォルダ内のコードを編集して保存すると、自動的にサーバーが再起動します。  
  手動で再起動する必要はありません。

- **サーバーの終了**  
  `docker compose up api` を実行したターミナルで **Ctrl + C** を押すと停止できます。

- **envファイルを編集した場合**  
  .env の内容を変更した場合は、サーバーを終了した後に以下のコマンドでサーバーを再起動してください。
```bash
docker compose down
docker compose up api
```