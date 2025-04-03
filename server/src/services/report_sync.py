
from src.config import settings
from src.services.storage import get_storage_service
from src.utils.logger import setup_logger

logger = setup_logger()


class ReportSyncService:
    REMOTE_REPORT_DIR_PREFIX = "outputs"
    REMOTE_STATUS_FILE_PREFIX = "status"
    LOCAL_STATUS_FILE_PATH = settings.DATA_DIR / "report_status.json"

    def __init__(self):
        self.storage_service = get_storage_service()

    def sync_status_file_to_storage(self) -> None:
        """ステータスファイルをストレージにアップロードする"""
        if not self.LOCAL_STATUS_FILE_PATH.exists():
            logger.warning(f"Status file does not exist: {self.LOCAL_STATUS_FILE_PATH}")
            return

        remote_status_file_path = f"{self.REMOTE_STATUS_FILE_PREFIX}/report_status.json"
        self.storage_service.upload_file(str(self.LOCAL_STATUS_FILE_PATH), remote_status_file_path)

    def sync_report_files_to_storage(self, slug: str) -> None:
        """レポートの中間ファイルと結果ファイルをストレージにアップロードする"""

        report_dir = settings.REPORT_DIR / slug
        if not report_dir.exists():
            logger.warning(f"Report directory does not exist: {report_dir}")
            return

        local_dir = settings.REPORT_DIR / slug
        remote_dir_prefix = f"{self.REMOTE_REPORT_DIR_PREFIX}/{slug}"
        self.storage_service.upload_directory(str(local_dir), remote_dir_prefix)

    def download_status_file_from_storage(self) -> bool:
        """ステータスファイルをストレージからダウンロードする

        Returns:
            bool: ダウンロードに成功した場合はTrue、失敗した場合はFalse
        """
        try:
            remote_status_file_path = f"{self.REMOTE_STATUS_FILE_PREFIX}/report_status.json"
            self.storage_service.download_file(remote_status_file_path, str(self.LOCAL_STATUS_FILE_PATH))
            return True
        except FileNotFoundError:
            logger.warning(f"Status file not found in storage: {remote_status_file_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to download status file from storage: {e}")

    def download_all_report_results_from_storage(self) -> bool:
        """レポート結果ファイル（hierarchical_result.json）のみをストレージからダウンロードする

        Returns:
            bool: ダウンロードに成功した場合はTrue、失敗した場合はFalse
        """
        try:
            self.storage_service.download_directory(
                str(self.REMOTE_REPORT_DIR_PREFIX),
                str(settings.REPORT_DIR),
                target_suffix_list=["json"],
            )
            return True
        except FileNotFoundError:
            logger.warning(f"No report files found in storage with prefix: {self.REMOTE_REPORT_DIR_PREFIX}")
            return False
        except Exception as e:
            logger.error(f"Failed to download report files from storage: {e}")
            return False


def initialize_from_storage() -> bool:
    """サーバー起動時にストレージからファイルを初期化する

    Returns:
        bool: 初期化に成功した場合はTrue、失敗した場合はFalse
    """
    report_sync_service = ReportSyncService()
    status_success = False
    reports_success = False

    try:
        status_success = report_sync_service.download_status_file_from_storage()
    except Exception as e:
        logger.error(f"Failed to download status file from storage: {e}")
        return False
    try:
        reports_success = report_sync_service.download_all_report_results_from_storage()
    except Exception as e:
        logger.error(f"Failed to download report files from storage: {e}")
        return False
    return status_success and reports_success


if __name__ == "__main__":
    initialize_from_storage()
