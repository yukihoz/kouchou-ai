import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import settings
from src.services.storage import AzureBlobStorageService, LocalStorageService, get_storage_service


class TestAzureBlobStorageService:
    """Azure Blob Storageサービスのテスト"""

    @pytest.fixture
    def mock_blob_service_client(self):
        """BlobServiceClientのモック"""
        with patch("src.services.storage.BlobServiceClient") as mock:
            # コンテナクライアントのモック
            container_client_mock = MagicMock()
            container_client_mock.exists.return_value = True

            # BlobServiceClientのモック
            client_mock = MagicMock()
            client_mock.get_container_client.return_value = container_client_mock

            # from_connection_stringメソッドのモック
            mock.from_connection_string.return_value = client_mock

            yield client_mock

    @pytest.fixture
    def azure_storage(self, mock_blob_service_client):
        """Azure Blob Storageサービスのインスタンス"""
        with patch.object(settings, "AZURE_STORAGE_CONNECTION_STRING", "dummy_connection_string"):
            with patch.object(settings, "STORAGE_CONTAINER_NAME", "test-container"):
                storage = AzureBlobStorageService()
                yield storage

    def test_upload_file(self, azure_storage, mock_blob_service_client):
        """ファイルアップロードのテスト"""
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(b"test content")
            temp_path = temp.name

        try:
            # BlobClientのモック
            blob_client_mock = MagicMock()
            mock_blob_service_client.get_blob_client.return_value = blob_client_mock

            # アップロード
            result = azure_storage.upload_file(temp_path, "test/file.txt")

            # 検証
            assert result is True
            mock_blob_service_client.get_blob_client.assert_called_once_with(
                container="test-container", blob="test/file.txt"
            )
            blob_client_mock.upload_blob.assert_called_once()
        finally:
            # 一時ファイルを削除
            os.unlink(temp_path)

    def test_upload_file_not_exists(self, azure_storage):
        """存在しないファイルのアップロードは失敗する"""
        result = azure_storage.upload_file("/path/to/nonexistent/file", "test/file.txt")
        assert result is False

    def test_download_file(self, azure_storage, mock_blob_service_client):
        """ファイルダウンロードのテスト"""
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "downloaded_file.txt"

            # BlobClientのモック
            blob_client_mock = MagicMock()
            blob_client_mock.exists.return_value = True
            download_blob_mock = MagicMock()
            download_blob_mock.readall.return_value = b"test content"
            blob_client_mock.download_blob.return_value = download_blob_mock
            mock_blob_service_client.get_blob_client.return_value = blob_client_mock

            # ダウンロード
            result = azure_storage.download_file("test/file.txt", temp_path)

            # 検証
            assert result is True
            mock_blob_service_client.get_blob_client.assert_called_once_with(
                container="test-container", blob="test/file.txt"
            )
            blob_client_mock.download_blob.assert_called_once()
            assert temp_path.exists()
            with open(temp_path, "rb") as f:
                assert f.read() == b"test content"

    def test_download_file_not_exists(self, azure_storage, mock_blob_service_client):
        """存在しないファイルのダウンロードは失敗する"""
        # 一時ディレクトリを作成
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "downloaded_file.txt"

            # BlobClientのモック
            blob_client_mock = MagicMock()
            blob_client_mock.exists.return_value = False
            mock_blob_service_client.get_blob_client.return_value = blob_client_mock

            # ダウンロード
            result = azure_storage.download_file("test/nonexistent.txt", temp_path)

            # 検証
            assert result is False
            assert not temp_path.exists()

    def test_list_files(self, azure_storage, mock_blob_service_client):
        """ファイル一覧取得のテスト"""
        # コンテナクライアントのモック
        container_client_mock = MagicMock()
        mock_blob_service_client.get_container_client.return_value = container_client_mock

        # list_blobsの戻り値を設定
        blob1 = MagicMock()
        blob1.name = "test/file1.txt"
        blob2 = MagicMock()
        blob2.name = "test/file2.txt"
        container_client_mock.list_blobs.return_value = [blob1, blob2]

        # ファイル一覧取得
        result = azure_storage.list_files("test/")

        # 検証
        assert result == ["test/file1.txt", "test/file2.txt"]
        container_client_mock.list_blobs.assert_called_once_with(name_starts_with="test/")

    def test_file_exists(self, azure_storage, mock_blob_service_client):
        """ファイル存在確認のテスト"""
        # BlobClientのモック
        blob_client_mock = MagicMock()
        blob_client_mock.exists.return_value = True
        mock_blob_service_client.get_blob_client.return_value = blob_client_mock

        # ファイル存在確認
        result = azure_storage.file_exists("test/file.txt")

        # 検証
        assert result is True
        mock_blob_service_client.get_blob_client.assert_called_once_with(
            container="test-container", blob="test/file.txt"
        )
        blob_client_mock.exists.assert_called_once()

    def test_file_not_exists(self, azure_storage, mock_blob_service_client):
        """ファイルが存在しない場合のテスト"""
        # BlobClientのモック
        blob_client_mock = MagicMock()
        blob_client_mock.exists.return_value = False
        mock_blob_service_client.get_blob_client.return_value = blob_client_mock

        # ファイル存在確認
        result = azure_storage.file_exists("test/nonexistent.txt")

        # 検証
        assert result is False


class TestGetStorageService:
    """get_storage_service関数のテスト"""

    def test_get_local_storage(self):
        """STORAGE_TYPE=localの場合はLocalStorageServiceを返す"""
        with patch.object(settings, "STORAGE_TYPE", "local"):
            storage = get_storage_service()
            assert isinstance(storage, LocalStorageService)

    def test_get_azure_blob_storage(self):
        """STORAGE_TYPE=azure_blobの場合はAzureBlobStorageServiceを返す"""
        with patch.object(settings, "STORAGE_TYPE", "azure_blob"):
            with patch.object(settings, "AZURE_STORAGE_CONNECTION_STRING", "dummy_connection_string"):
                with patch("src.services.storage.BlobServiceClient"):
                    storage = get_storage_service()
                    assert isinstance(storage, AzureBlobStorageService)

    def test_get_unknown_storage(self):
        """未知のSTORAGE_TYPEの場合はLocalStorageServiceを返す"""
        with patch.object(settings, "STORAGE_TYPE", "unknown"):
            storage = get_storage_service()
            assert isinstance(storage, LocalStorageService)
