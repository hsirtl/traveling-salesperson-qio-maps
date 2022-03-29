import json
import os
import logging

from urllib.parse import urlparse
from azure.storage.blob import BlobClient, ContainerClient


def uploadBlobContent(outputBlobContainer, outputBlobName, blobData):
    connection_string = os.environ["StorageConnection"]
    logging.info("Storage Connection: %s", connection_string)
    outputBlobClient = BlobClient.from_connection_string(conn_str=connection_string, container_name=outputBlobContainer, blob_name=outputBlobName)
    outputBlobClient.upload_blob(blobData)


def downloadBlobContent(inputBlobUrl):
    u = urlparse(inputBlobUrl)
    inputBlobContainer = os.path.dirname(u.path)[1:]
    inputBlobName = os.path.basename(u.path)

    logging.info('Uploaded blob name     : %s', inputBlobName)
    logging.info('Uploaded blob container: %s', inputBlobContainer)

    connection_string = os.environ["StorageConnection"]
    inputBlobClient = BlobClient.from_connection_string(conn_str=connection_string, container_name=inputBlobContainer, blob_name=inputBlobName)

    streamdownloader = inputBlobClient.download_blob()
    inputBlobData = json.loads(streamdownloader.readall())

    return inputBlobData


def deleteBlob(blobUrl):
    u = urlparse(blobUrl)
    blobContainer = os.path.dirname(u.path)[1:]
    blobName = os.path.basename(u.path)

    connection_string = os.environ["StorageConnection"]
    blobClient = BlobClient.from_connection_string(conn_str=connection_string, container_name=blobContainer, blob_name=blobName)

    blobClient.delete_blob()