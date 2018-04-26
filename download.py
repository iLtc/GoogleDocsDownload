from __future__ import print_function
import os
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import io
from apiclient.http import MediaIoBaseDownload
import json

# Setup the Drive v3 API
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
	flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
	creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

file_exts = {'gdoc': ['.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
			 'gsheet': ['.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'], 
			 'gslides': ['.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']}

def download(path):
	files = os.listdir(path)
	
	for file in files:
		if os.path.isdir(path + file):
			download(path + file + '/')
		elif file.split(".")[-1] in ['gdoc', 'gsheet', 'gslides']:  # Detect Google Docs File
			print(path + file)
			
			fh = open(path + file)
			
			json_str = fh.read()
			json_data = json.loads(json_str)
			
			doc_id = json_data['doc_id']
			
			fh.close()
			
            # Download PDF
			if not os.path.exists(path + file + '.pdf'):
				# Call the Drive v3 API
				request = service.files().export_media(fileId=doc_id, mimeType='application/pdf')	

				fh = open(path + file + '.pdf', 'wb')
				downloader = MediaIoBaseDownload(fh, request)
				done = False
				while done is False:
					status, done = downloader.next_chunk()
					print ("Download {}.".format( int(status.progress() * 100)))
				fh.close()
				
            # Downliad Office File
			file_ext, file_type = file_exts[file.split(".")[-1]]
			new_file_name = path + file + file_ext
			
			if not os.path.exists(new_file_name):
				# Call the Drive v3 API
				request = service.files().export_media(fileId=doc_id, mimeType=file_type)	

				fh = open(new_file_name, 'wb')
				downloader = MediaIoBaseDownload(fh, request)
				done = False
				while done is False:
					status, done = downloader.next_chunk()
					print ("Download {}.".format( int(status.progress() * 100)))
				fh.close()

download('./')