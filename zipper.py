import os, sys, zipfile
from zipfile import ZipFile as zip

def zipAll(zipName, outputDir):
	z = zip(zipName, 'w',  zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk(outputDir):
		for file in files:
			absPath = os.path.join(root, file)
			z.write(os.path.join(root, file), os.path.relpath(absPath, outputDir))
	z.close()

	

def unzipAll(zipName, outputDir):
    z = zip(zipName)
    z.extractall(outputDir)
			

op = sys.argv[1]
inputFile = sys.argv[2]
outputDir = sys.argv[3]

if op == 'zip':
	zipAll(inputFile, outputDir)
elif op == 'unzip':
	unzipAll(inputFile, outputDir)