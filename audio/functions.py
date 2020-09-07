import shutil
import os

def handle_uploaded_file(f):  

	path = "audio/static/upload/"
	# files = os.listdir(path)

	for file in os.listdir(path):
		print(os.listdir(path))
		try:
			shutil.rmtree(os.path.join(path,file))
		except OSError as error:
			os.remove(os.path.join(path,file))

	with open('audio/static/upload/'+f.name, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)  
