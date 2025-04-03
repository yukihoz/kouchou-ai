import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from src.config import settings

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """ストレージサービスの抽象基底クラス

    ファイルやディレクトリのアップロード・ダウンロード機能を提供する抽象基底クラスです。
    異なるストレージバックエンド（ローカルストレージ、Azure Blob Storageなど）に対して
    共通のインターフェースを定義します。
    """

    @abstractmethod
    def upload_file(self, local_file_path: str, remote_blob_path: str):
        """ローカルファイルをストレージにアップロードする

        Args:
            local_file_path: アップロードするローカルファイルのパス
            remote_blob_path: ストレージ上の保存先パス
        """
        pass

    @abstractmethod
    def download_file(self, remote_blob_path: str, local_file_path: str):
        """ストレージからファイルをダウンロードする

        Args:
            remote_blob_path: ダウンロードするストレージ上のファイルパス
            local_file_path: ローカルの保存先パス
        """
        pass

    @abstractmethod
    def download_directory(
        self, remote_dir_prefix: str, local_dir_path: str, target_suffix_list: list[str] | None = None
    ):
        """ストレージから指定プレフィックスに一致するファイル群をディレクトリとしてダウンロードする

        Args:
            remote_dir_prefix: ダウンロードするストレージ上のディレクトリプレフィックス
            local_dir_path: ローカルの保存先ディレクトリパス
        """
        pass

    @abstractmethod
    def upload_directory(
        self, local_dir_path: str, remote_dir_prefix: str, target_suffix_list: list[str] | None = None
    ):
        """ローカルディレクトリをストレージにアップロードする

        Args:
            local_dir_path: アップロードするローカルディレクトリのパス
            remote_dir_prefix: ストレージ上の保存先プレフィックス
            target_suffix_list: アップロード対象とするファイルの拡張子リスト（省略可能）
        """
        pass


class LocalStorageService(StorageService):
    """ローカルストレージサービス（実質何もしない）

    ローカルストレージを使用する場合のサービス実装です。
    実際にはファイルの移動を行わないため、ほとんどのメソッドは何も処理を行いません。
    """

    def upload_file(self, local_path: str | Path, remote_path: str) -> None:
        """ローカルストレージの場合はアップロード操作は不要

        Args:
            local_path: アップロード元のローカルファイルパス（文字列またはPathオブジェクト）
            remote_path: アップロード先のパス（文字列）
        """
        logger.debug(f"LocalStorageService: upload_file は何もしません - {local_path} -> {remote_path}")

    def download_file(self, remote_path: str, local_path: str | Path) -> None:
        """ローカルストレージの場合はダウンロード操作は不要

        Args:
            remote_path: ダウンロード元のパス（文字列）
            local_path: ダウンロード先のローカルファイルパス（文字列またはPathオブジェクト）
        """
        logger.debug(f"LocalStorageService: download_file は何もしません - {remote_path} -> {local_path}")

    def download_directory(
        self, remote_dir_prefix: str, local_dir_path: str, target_suffix_list: list[str] | None = None
    ) -> None:
        """ローカルストレージの場合はファイル一覧取得は不要

        Args:
            remote_dir_prefix: ダウンロード対象のディレクトリプレフィックス
            local_dir_path: ダウンロード先のローカルディレクトリパス
            target_suffix_list: ダウンロード対象とするファイルの拡張子リスト（省略可能）
        """
        logger.debug(
            f"LocalStorageService: download_directory は何もしません - {remote_dir_prefix} -> {local_dir_path}"
        )

    def upload_directory(
        self, local_dir_path: str, remote_dir_prefix: str, target_suffix_list: list[str] | None = None
    ) -> None:
        """ディレクトリをストレージにアップロードする

        ローカルストレージの場合、ディレクトリのアップロード操作は実質的に不要なため何も行いません。

        Args:
            local_dir_path: アップロード元のローカルディレクトリパス（文字列）
            remote_dir_prefix: アップロード先のディレクトリプレフィックス（文字列）
            target_suffix_list: アップロード対象とするファイルの拡張子リスト（省略可能）
        """
        logger.debug(f"LocalStorageService: upload_directory は何もしません - {local_dir_path} -> {remote_dir_prefix}")


class AzureBlobStorageService(StorageService):
    """Azure Blob Storageを使用するストレージサービス

    Azure Blob Storageを使用するストレージサービスの実装です。
    ファイルやディレクトリのアップロード・ダウンロードをAzure Blob Storageとの間で行います。
    """

    def __init__(self):
        """AzureBlobStorageServiceのコンストラクタ

        設定からAzure Blob Storageの接続情報を取得し、クライアントを初期化します。
        """
        self.blob_service_client = BlobServiceClient(
            account_url=settings.azure_blob_storage_account_url,
            credential=DefaultAzureCredential(),
        )
        self.container_client = self.blob_service_client.get_container_client(
            settings.AZURE_BLOB_STORAGE_CONTAINER_NAME
        )

    def _has_target_suffix(self, blob_path: str, target_suffix_list: list[str] | None) -> bool:
        """指定されたsuffixで終わるファイルを判定する

        Args:
            blob_path: 判定対象のBlobパス（文字列）
            target_suffix_list: 対象とする拡張子のリスト（Noneの場合は全てのファイルが対象）

        Returns:
            bool: 指定された拡張子で終わる場合はTrue、それ以外はFalse
        """
        if target_suffix_list is None:
            return True
        return any(blob_path.endswith(suffix) for suffix in target_suffix_list)

    def upload_file(self, local_file_path: str, remote_blob_path: str, skip_if_same: bool = True) -> None:
        """ファイルをストレージにアップロードする

        ローカルファイルをAzure Blob Storageにアップロードします。
        skip_if_sameがTrueの場合、同一ファイルが既に存在する場合はアップロードをスキップします。

        Args:
            local_file_path: アップロードするローカルファイルのパス（文字列）
            remote_blob_path: Azure Blob Storage上の保存先パス（文字列）
                パスが「/」で終わる場合、元のファイル名が自動的に追加されます
                パスが空または「.」の場合、元のファイル名のみが使用されます
            skip_if_same: 同一ファイルが存在する場合にスキップするかどうか（デフォルト: True）
        """
        try:
            if remote_blob_path.endswith("/"):
                remote_blob_path = remote_blob_path + os.path.basename(local_file_path)
            elif remote_blob_path == "" or remote_blob_path == ".":
                remote_blob_path = os.path.basename(local_file_path)

            blob_client = self.container_client.get_blob_client(remote_blob_path)

            # 同一ファイルチェック
            if skip_if_same and blob_client.exists():
                # ローカルファイルのサイズを取得
                local_file_size = os.path.getsize(local_file_path)

                # リモートBlobのプロパティを取得
                blob_properties = blob_client.get_blob_properties()
                remote_file_size = blob_properties.size

                # サイズが同じ場合はスキップ（より厳密にするならハッシュ値も比較する）
                if local_file_size == remote_file_size:
                    logger.info(
                        f"Skipped upload for '{local_file_path}' - identical file already exists at '{remote_blob_path}'"
                    )
                    return

            # ファイルをアップロード
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            logger.info(f"Uploaded file '{local_file_path}' to blob '{remote_blob_path}'")
        except Exception as e:
            logger.error(f"Failed to upload file '{local_file_path}' to blob '{remote_blob_path}': {str(e)}")
            raise

    def upload_directory(
        self,
        local_dir_path: str,
        remote_dir_prefix: str,
        target_suffix_list: list[str] | None = None,
        skip_if_same: bool = True,
    ) -> None:
        """ディレクトリをストレージにアップロードする

        ローカルディレクトリ内のファイルをAzure Blob Storageにアップロードします。

        Args:
            local_dir_path: アップロードするローカルディレクトリのパス（文字列）
            remote_dir_prefix: Azure Blob Storage上の保存先プレフィックス（文字列）
            target_suffix_list: アップロード対象とするファイルの拡張子リスト（省略可能）
                指定された場合、リストに含まれる拡張子を持つファイルのみがアップロードされます
            skip_if_same: 同一ファイルが存在する場合にスキップするかどうか（デフォルト: True）
        """
        try:
            prefix = remote_dir_prefix
            if prefix and not prefix.endswith("/"):
                prefix += "/"

            files_processed = 0

            for root, _, files in os.walk(local_dir_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, local_dir_path)
                    remote_blob_path = (
                        prefix + relative_path.replace(os.sep, "/") if prefix else relative_path.replace(os.sep, "/")
                    )
                    if not self._has_target_suffix(remote_blob_path, target_suffix_list):
                        continue

                    files_processed += 1
                    self.upload_file(file_path, remote_blob_path, skip_if_same=skip_if_same)

            if files_processed == 0:
                logger.warning(f"No files matching the criteria were found in '{local_dir_path}'")

        except Exception as e:
            logger.error(f"Failed to upload directory '{local_dir_path}' to '{remote_dir_prefix}': {str(e)}")
            raise

    def download_file(self, remote_blob_path: str, local_file_path: str) -> None:
        """ファイルをダウンロードする

        Azure Blob Storageからファイルをローカルにダウンロードします。

        Args:
            remote_blob_path: ダウンロードするAzure Blob Storage上のファイルパス（文字列）
            local_file_path: ローカルの保存先パス（文字列）
                必要に応じて親ディレクトリが自動的に作成されます

        Raises:
            FileNotFoundError: 指定されたBlobが存在しない場合
        """
        try:
            blob_client = self.container_client.get_blob_client(remote_blob_path)
            try:
                downloader = blob_client.download_blob()
            except ResourceNotFoundError as err:
                logger.error(
                    f"Blob '{remote_blob_path}' not found in container '{self.container_client.container_name}'."
                )
                raise FileNotFoundError(
                    f"Blob '{remote_blob_path}' not found in container '{self.container_client.container_name}'."
                ) from err

            os.makedirs(os.path.dirname(local_file_path), exist_ok=True) if os.path.dirname(local_file_path) else None
            with open(local_file_path, "wb") as file:
                file.write(downloader.readall())
            logger.info(f"Downloaded blob '{remote_blob_path}' to local file '{local_file_path}'")
        except Exception as e:
            if not isinstance(e, FileNotFoundError):
                logger.error(f"Failed to download blob '{remote_blob_path}' to '{local_file_path}': {str(e)}")
            raise

    def download_directory(
        self, remote_dir_prefix: str, local_dir_path: str, target_suffix_list: list[str] | None = None
    ) -> None:
        """ディレクトリをダウンロードする

        指定されたプレフィックスに一致するAzure Blob Storage上のファイル群をローカルディレクトリにダウンロードします。

        Args:
            remote_dir_prefix: ダウンロードするAzure Blob Storage上のディレクトリプレフィックス（文字列）
            local_dir_path: ローカルの保存先ディレクトリパス（文字列）
            target_suffix_list: ダウンロード対象とするファイルの拡張子リスト（省略可能）
                指定された場合、リストに含まれる拡張子を持つファイルのみがダウンロードされます

        Raises:
            FileNotFoundError: 一致するファイルが見つからない場合
        """
        try:
            prefix = remote_dir_prefix
            if prefix and not prefix.endswith("/"):
                prefix += "/"

            blobs_list = self.container_client.list_blobs(name_starts_with=prefix)
            found = False

            for blob in blobs_list:
                blob_name = blob.name
                # target_suffixが指定されていて、blob名がそのsuffixで終わらなければスキップ
                if not self._has_target_suffix(blob_name, target_suffix_list):
                    continue

                found = True
                # プレフィックス部分を除いた相対パスを計算し、ローカルのパスと結合
                relative_path = blob_name[len(prefix) :] if prefix else blob_name
                local_path = os.path.join(local_dir_path, relative_path)

                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # blob をローカルファイルにダウンロード
                self.download_file(blob_name, local_path)

            if not found:
                error_msg = f"No blobs found with prefix '{remote_dir_prefix}' and suffix '{target_suffix_list}' in container '{self.container_client.container_name}'."
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        except Exception as e:
            if not isinstance(e, FileNotFoundError):
                logger.error(
                    f"Failed to download directory with prefix '{remote_dir_prefix}' to '{local_dir_path}': {str(e)}"
                )
            raise


def get_storage_service() -> StorageService:
    """設定に基づいて適切なストレージサービスを返す

    設定ファイルのSTORAGE_TYPE設定に基づいて、適切なストレージサービスのインスタンスを返します。

    Returns:
        StorageService: 設定に基づいたストレージサービスのインスタンス
            - "local": LocalStorageService
            - "azure_blob": AzureBlobStorageService
            - その他: LocalStorageService（デフォルト）
    """
    if settings.STORAGE_TYPE == "local":
        logger.info("Using LocalStorageService")
        return LocalStorageService()
    elif settings.STORAGE_TYPE == "azure_blob":
        if not settings.AZURE_BLOB_STORAGE_ACCOUNT_NAME or not settings.AZURE_BLOB_STORAGE_CONTAINER_NAME:
            error_msg = "Azure Blob Storageの設定が不足しています。AZURE_BLOB_STORAGE_ACCOUNT_NAME と AZURE_BLOB_STORAGE_CONTAINER_NAME を設定してください。"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info(
            f"Using AzureBlobStorageService with account {settings.AZURE_BLOB_STORAGE_ACCOUNT_NAME} and container {settings.AZURE_BLOB_STORAGE_CONTAINER_NAME}"
        )
        return AzureBlobStorageService()

    logger.warning(f"Unknown storage type: {settings.STORAGE_TYPE}, falling back to local storage")
    return LocalStorageService()


if __name__ == "__main__":
    storage_service = AzureBlobStorageService()
    slug = "0309-example"
    local_dir_path = f"/Users/nasuka/workspace/shotokutaishi/server/broadlistening/pipeline/outputs/{slug}"
    remote_dir_prefix = f"example_outputs_1/{slug}"
    storage_service.upload_directory(local_dir_path, remote_dir_prefix)
    storage_service.download_directory(remote_dir_prefix, f"local_outputs_1/{slug}")
