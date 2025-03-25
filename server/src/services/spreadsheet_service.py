import re
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from src.config import settings
from src.utils.logger import setup_logger

slogger = setup_logger()


def parse_spreadsheet_url(url: str) -> tuple[str, str | None]:
        # スプレッドシートIDのパターン
    pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, url)
    
    if not match:
        raise ValueError("有効なGoogleスプレッドシートのURLではありません")
    
    sheet_id = match.group(1)
    
    # シート名の抽出（#gid=XXXの形式）
    gid_pattern = r"gid=(\d+)"
    gid_match = re.search(gid_pattern, url)
    sheet_name = gid_match.group(1) if gid_match else None
    
    return sheet_id, sheet_name


def fetch_public_spreadsheet(sheet_id: str, sheet_name: str | None = None) -> pd.DataFrame:
        # 公開スプレッドシートのCSVエクスポートURL
    base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"
    
    params = {
        "format": "csv",
    }
    
    if sheet_name:
        params["gid"] = sheet_name
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        response.encoding = "utf-8"
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        if "comment" not in df.columns and "comment-body" not in df.columns:
            raise ValueError("スプレッドシートには 'comment' または 'comment-body' カラムが必要です")
 
        # カラム名の調整
        if "comment-body" not in df.columns and "comment" in df.columns:
            df["comment-body"] = df["comment"]
        
        if "comment" not in df.columns and "comment-body" in df.columns:
            df["comment"] = df["comment-body"]
        
        # comment-idがなければ作成
        if "comment-id" not in df.columns:
            df["comment-id"] = [f"id-{i+1}" for i in range(len(df))]
            
        return df
        
    except requests.exceptions.RequestException as e:
        slogger.error(f"スプレッドシートの取得エラー: {e}")
        raise ValueError(f"スプレッドシートの取得に失敗しました: {e}") from e


def save_as_csv(df: pd.DataFrame, file_name: str) -> Path:
    input_path = settings.INPUT_DIR / f"{file_name}.csv"
    df.to_csv(input_path, index=False)

    return input_path


def process_spreadsheet_url(url: str, file_name: str) -> Path:
    try:
        sheet_id, sheet_name = parse_spreadsheet_url(url)
        df = fetch_public_spreadsheet(sheet_id, sheet_name)
        return save_as_csv(df, file_name)
    except Exception as e:
        slogger.error(f"スプレッドシートURL処理エラー: {e}")
        raise ValueError(f"スプレッドシートの処理に失敗しました: {e}") from e


# 将来的に認証対応が必要になった場合の拡張ポイント
# def fetch_private_spreadsheet(sheet_id: str, sheet_name: str | None = None, credentials=None) -> pd.DataFrame:
#     """
#     アクセス制限されているスプレッドシートからデータを取得する機能
#     """
#     # ここにgspreadやGoogleAPIClientを使った認証付きのデータ取得コードを実装
#     pass
