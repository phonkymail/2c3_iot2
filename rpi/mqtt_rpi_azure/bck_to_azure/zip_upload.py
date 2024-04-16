from azure.storage.blob import BlobServiceClient, ContainerClient
import shutil
from time import sleep
from datetime import datetime

# Azure Storage Account connection string
connection_string = "[get connection string from Access Keys in Azure]"
container_name = "[fill a container name]"

def create_container(name):
    container_client = ContainerClient.from_connection_string(connection_string, name)
    if not container_client.exists():
        container_client.create_container()
        print(f"Container '{name}' created")
    else:
        print(f"Container '{name}' exists")

def take_backup(src_file_path, dst_file_path):
    try:
        shutil.copy2(src_file_path, dst_file_path)
        print("Backup successful!")
    except FileNotFoundError:
        print("File does not exist!")

def upload_to_container(file_path, file_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data)

    print(f"Uploaded: {file_name}")

backup_number = 1
while True:
    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    create_container(container_name)
    sleep(3)
    take_backup("/home/plekea16/Desktop/bck_to_azure/sensor_data.db", "/home/plekea16/Desktop/bck_to_azure/upload/sensor_data_bck.zip")
    sleep(3)
    upload_to_container("/home/plekea16/Desktop/bck_to_azure/upload/sensor_data_bck.zip", f'backup :{current_date}.zip')
    sleep(6)
    backup_number += 1
