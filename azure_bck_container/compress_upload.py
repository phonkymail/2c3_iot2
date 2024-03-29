#backup_to_container_v1.0
#grupe 3c Amir, Dario, Phong , Rafal

from azure.storage.blob import BlobServiceClient
#import zipfile
import shutil 
import os 
import sys
from time import sleep

def take_backup(src_file_name,  
                dst_file_name=None, 
                src_dir='',  
                dst_dir=''): 
    try: 
#source dir
        src_dir = ("/home/rav/Desktop/python/backup/file.txt")
        dst_dir = "/home/rav/Desktop/python/upload/"
        if not src_file_name: 
            print("Please give atleast the Source File Name") 
            exit() 
        try:          
            # If user provides all the inputs 
            if src_file_name and dst_file_name and src_dir and dst_dir: 
                src_dir = src_dir+src_file_name 
                dst_dir = dst_dir+dst_file_name                  
            # When User Enter Either   'None' or empty String ('') 
            elif dst_file_name is None or not dst_file_name: 
                dst_file_name = src_file_name 
                dst_dir = dst_dir+dst_file_name 
                  
            # When user Enter an empty string with one or more spaces (' ') 
            elif dst_file_name.isspace(): 
                dst_file_name = src_file_name 
                dst_dir = dst_dir+date_format+dst_file_name 
                  
            # When user Enter an a  name for the backup copy 
            else: 
                dst_dir = dst_dir+date_format+dst_file_name 
  
            # Now, just copy the files  from source to destination 
            shutil.copy2(src_dir, dst_dir) 
            print("Backup Successful!") 
        except FileNotFoundError: 
            print("File does not exists!,\ please give the complete path") 

    except PermissionError:   
        dst_dir = dst_dir+date_format+dst_file_name 
        shutil.copytree(src_file_name, dst_dir) 

target = "/home/rav/Desktop/python/upload/backup.zip"
#cridential in Azure contailer page
storage_account_key = x"Pwg8lb5XsQrhB7rFln4LnPT46hIu9F4AMkW0SqR+CTcl7Uz9h26seTd77C0buJj771auAjvzSg8f+AStvyrV+Q=="
storage_account_name = "sletmig"
connection_string = "DefaultEndpointsProtocol=https;AccountName=sletmig;AccountKey=OWM3C2aTDDjNL2xWqjJbTnIkD904InB57tNcycNSQligRfOwBxDth2DbaTqTnugLp1oeTh9CpqZn+AStDPWGWQ==;EndpointSuffix=core.windows.net"
container_name = "backup"

#def do_zip():
#    handle = zipfile.ZipFile('backup.zip','w')
#    handle.write(target, compress_type = zipfile.ZIP_DEFLATED)
#    handle.close()

def uplodtocontainer(file_path, file_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    with open(file_path,"rb") as data:
        blob_client.upload_blob(data)

    print(f'uploaded : {file_name}.')

while True:
#call funtionn arg.file source, file name
    take_backup("file.txt")
    #sleep(5)
    #do_zip()
    sleep(5)
    uplodtocontainer( "/home/rav/Desktop/python/upload.py",'backup.zip')
    sleep(1500)