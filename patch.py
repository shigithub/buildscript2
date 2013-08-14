from filecmp import dircmp
import os, sys, shutil, os.path

FILE_REMOVED = 'D'
FILE_ADDED = 'A'
FILE_MODIFIED = 'M';


def applyChanges(resultDir, patchDir, changesLog):

	for rec in changesLog:
		op = rec[0]
		file = rec[1]
		
		if op in [FILE_ADDED, FILE_MODIFIED] :
			baseDir = os.path.dirname(resultDir + '\\' + file)
			if not os.path.exists(baseDir) :
				os.makedirs(baseDir)
			shutil.copy(patchDir + '\\_files\\' + file, resultDir + '\\' + file)
		elif op == FILE_REMOVED :
			toBeRemoved = resultDir + '\\' + file;
			if os.path.exists(toBeRemoved):
				os.remove(resultDir + '\\' + file)
		
		# add changes
		shutil.copy(patchDir + '\\changes.log', resultDir + '\\changes.log');

def prepareDir(resDir):
	if not os.path.exists(resDir):
		os.makedirs(resDir)
	shutil.rmtree(resDir, ignore_errors = True)
	
def readChangesLog(patchDir) :

	records = []
	f = open(patchDir + '\\changes.log', 'r')
	
	for line in f:
		op, file = line.split(': ')
		records.append((op, file.strip()))
	
	f.close()
	
	return records

#--------------------- MAIN -----------------------		

destDir = sys.argv[1] # dir to be patched
patchDir = sys.argv[2] # patch dir
resultDir = sys.argv[3] # result dir

changesLog = readChangesLog(patchDir)
#prepareDir(resultDir)
shutil.copytree(destDir, resultDir)
applyChanges(resultDir, patchDir, changesLog)

