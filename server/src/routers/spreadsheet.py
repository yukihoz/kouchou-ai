from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import pandas as pd
import os
from src.config import settings
from src.services.spreadsheet_service import process_spreadsheet_url
from src.utils.logger import setup_logger

slogger = setup_logger()
router = APIRouter()

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


async def verify_admin_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


class SpreadsheetInput(BaseModel):
    url: str
    file_name: str


@router.post("/admin/spreadsheet/import")
async def import_spreadsheet(
    input_data: SpreadsheetInput, api_key: str = Depends(verify_admin_api_key)
):
    try:
        file_path = process_spreadsheet_url(input_data.url, input_data.file_name)
        return {
            "status": "success",
            "message": "スプレッドシートのインポートが完了しました",
            "file_path": str(file_path),
            "file_name": input_data.file_name
        }
    except ValueError as e:
        slogger.error(f"スプレッドシートのインポートエラー: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        slogger.error(f"予期せぬエラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内部サーバーエラー: {str(e)}")


@router.get("/admin/spreadsheet/data/{file_name}")
async def get_spreadsheet_data(
    file_name: str, api_key: str = Depends(verify_admin_api_key)
):
    """
    インポート済みのスプレッドシートデータを取得するエンドポイント
    """
    input_path = settings.INPUT_DIR / f"{file_name}.csv"
    try:
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail=f"ファイル {file_name}.csv が見つかりません")
        
        df = pd.read_csv(input_path)
        
        # コメントデータをJSON形式に変換
        comments = []
        for _, row in df.iterrows():
            comment = {
                "id": row.get("comment-id", f"id-{len(comments)+1}"),
                "comment": row.get("comment-body", row.get("comment", "")),
            }
            
            # オプションフィールドを追加
            if "source" in df.columns:
                comment["source"] = row.get("source")
            if "url" in df.columns:
                comment["url"] = row.get("url")
                
            comments.append(comment)
            
        return {
            "status": "success",
            "file_name": file_name,
            "comments": comments,
            "total": len(comments)
        }
    except HTTPException:
        raise
    except Exception as e:
        slogger.error(f"スプレッドシートデータの取得エラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"データ取得中にエラーが発生しました: {str(e)}")
