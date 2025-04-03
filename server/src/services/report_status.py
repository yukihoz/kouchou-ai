import json
import threading

from src.config import settings
from src.schemas.admin_report import ReportInput
from src.schemas.report import Report
from src.utils.logger import setup_logger

logger = setup_logger()
STATE_FILE = settings.DATA_DIR / "report_status.json"
_lock = threading.RLock()
_report_status = {}


def load_status() -> None:
    """ステータスファイルをロードする"""
    global _report_status
    try:
        with open(STATE_FILE) as f:
            _report_status = json.load(f)
    except FileNotFoundError:
        _report_status = {}
        logger.info("Status file not found, initializing empty status")
    except json.JSONDecodeError:
        _report_status = {}
        logger.warning("Status file contains invalid JSON, initializing empty status")


def load_status_as_reports() -> list[Report]:
    """ステータスファイルをロードしてReportオブジェクトのリストとして返す"""
    global _report_status
    try:
        with open(STATE_FILE) as f:
            _report_status = json.load(f)
    except FileNotFoundError:
        _report_status = {}
        logger.info("Status file not found, initializing empty status")
    except json.JSONDecodeError:
        _report_status = {}
        logger.warning("Status file contains invalid JSON, initializing empty status")

    return [Report(**report) for report in _report_status.values()]


def save_status() -> None:
    """ステータスファイルを保存する。ストレージが設定されている場合はそこにもアップロードする。"""
    with _lock:
        # ディレクトリが存在しない場合は作成
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

        # ローカルに保存
        with open(STATE_FILE, "w") as f:
            json.dump(_report_status, f, indent=4, ensure_ascii=False)

        # # ストレージにアップロード（ローカル以外の場合）
        # if settings.STORAGE_TYPE != "local":
        #     sync_status_file_to_storage()


def add_new_report_to_status(report_input: ReportInput) -> None:
    """新しいレポートをステータスに追加する"""
    with _lock:
        _report_status[report_input.input] = {
            "slug": report_input.input,
            "status": "processing",
            "title": report_input.question,
            "description": report_input.intro,
        }
        save_status()


def set_status(slug: str, status: str) -> None:
    """レポートのステータスを更新する"""
    with _lock:
        if slug not in _report_status:
            raise ValueError(f"slug {slug} not found in report status")
        _report_status[slug]["status"] = status
        save_status()


def get_status(slug: str) -> str:
    """レポートのステータスを取得する"""
    with _lock:
        return _report_status.get(slug, {}).get("status", "undefined")
