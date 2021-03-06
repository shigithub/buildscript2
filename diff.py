from filecmp import dircmp
from optparse import OptionParser
import os, sys, shutil, os.path, fnmatch

FILE_REMOVED = 'D'
FILE_ADDED = 'A'
FILE_MODIFIED = 'M';

INCLUDE_FILE_PATTERN = 'INCL'
EXCLUDE_FILE_PATTERN = 'EXCL'

# Fiters diff entries by type of operation
def filterByChangeType (diffData, filter):
	return [elem for elem in diffData if elem['op'] in filter]

	
# Filters diff entries by Unix-style filename matchers either in an inclusive or exclusive manner
def filterByFilePattern(diffData, fnMatchers, type):

	resList = []
	for entry in diffData:
		found = False
		for pattern in fnMatchers.split(','):
			if fnmatch.fnmatch(entry['file'], pattern.strip()):
				found = True
				break
		
		if (type == INCLUDE_FILE_PATTERN and found) or (type == EXCLUDE_FILE_PATTERN and not found):
			resList.append(entry)
	
	return resList

	
# Creates a list of diff entries based on differences between source and destination directory
def parseDiff(srcDir, dstDir) :

	resList = []

	def parseDiff_(dcmp):

		for name in dcmp.right_only:
			resList.append({'op': FILE_ADDED, 'dir' : dcmp.right, 'file' : name})

		for name in dcmp.left_only:		
			resList.append({'op' : FILE_REMOVED, 'dir' : dcmp.left, 'file' : name})
			
		for name in dcmp.diff_files:	
			resList.append({ 'op' : FILE_MODIFIED, 'dir' : dcmp.right, 'file': name})
			   
		for sub_dcmp in dcmp.subdirs.values():
			parseDiff_(sub_dcmp)

	print 'Checking for differences...'
	parseDiff_(dircmp(srcDir, dstDir))
	print 'Differences parsed.'	
	return resList

	
# Creates an actual diff in a location pointed by resDir. All files parsed by parseDiff function are put into the diff directory.
# There is also a log file added to the directory which stores all changes that should be done when a patch is applied.
def createDiff(resDir, srcDir, dstDir, diffData) :

	def createEntry(item):	
		op = item['op']
		baseDir = item['dir']
		file = item['file']
		
		if op == FILE_ADDED:
			dir = os.path.relpath(baseDir, dstDir)
		elif op == FILE_REMOVED:
			dir = os.path.relpath(baseDir, srcDir)
		elif op == FILE_MODIFIED:
			dir = os.path.relpath(baseDir, dstDir)
		
		if(dir == '.') :
			path = file
		else:
			path = dir + '\\' + file
		
		return (op, path)	

	def copy(op, path) :
		fullPath = resDir +  '\\_files\\' + path
		baseDir = os.path.dirname(fullPath)
		if not os.path.exists(baseDir):
			os.makedirs(baseDir)	
				
		isFromDest = True if op in [FILE_ADDED, FILE_MODIFIED] else False
		resource = (dstDir if isFromDest else srcDir) + '\\' + path
		
		copyFunc = shutil.copy if not os.path.isdir(resource) else shutil.copytree
		copyFunc(resource, fullPath)

	print 'Creating diff...'
	if os.path.exists(resDir):
		shutil.rmtree(resDir)
	os.makedirs(resDir)	
				
	diffLog = []
	for item in diffData:		
		op, path = createEntry(item)
		copy(op, path)
		diffLog.append( { 'op' : op, 'path' : path } )
	
	print 'Diff created.'	
	return diffLog

def createDiffLog(resDir, changeLog):
	
	print 'Creating diff log...'
	
	f = open(resDir + '\\changes.log', 'w+')
	
	for entry in changeLog:
		op = entry['op']
		path = entry['path']
		writeLine = "{0}: {1}\r\n".format(op, path)
		f.write(writeLine)
		
	f.close()
	print 'Diff log created.'				

#--------------------- MAIN -----------------------		


def main():

	parser = OptionParser(usage="usage: %prog [options] filename",
						version="%prog 1.0")
	parser.add_option("-x", "--exclude-file-pattern",
                      dest="excludes",
					  default="",
                      help="list of comma-separated Unix-style filename patterns e.g. *.pdb,*.asmx that are to be EXCLUDED in the patch")
	parser.add_option("-i", "--include-file-pattern",
                      dest="includes",
                      default="",
                      help="list of comma-separated Unix-style filename patterns e.g. *.pdb,*.asmx that are to be INCLUDED in the patch")
	parser.add_option("-c", "--change-types",
                      dest="changetypes",
                      default=FILE_MODIFIED + FILE_ADDED + FILE_REMOVED,
                      help="types of changes to be included in the patch. Possible types are: A - files added, M - files modified, D - files deleted. Examples: AM, AD, MD, AMD etc")
	(options, args) = parser.parse_args()


	if len(args) != 3:
		parser.error("wrong number of arguments")
	elif len(args) == 0:
		parser.print_help()
	else:
		excludes = options.__dict__['excludes']
		includes = options.__dict__['includes']
		change_types = options.__dict__['changetypes']
		srcDir = args[0]
		dstDir = args[1]
		resDir = args[2]
		diffData = parseDiff(srcDir, dstDir)
		diffData = filterByChangeType(diffData, change_types)
		if len(excludes) != 0:
			diffData = filterByFilePattern(diffData, excludes, EXCLUDE_FILE_PATTERN)
		if len(includes) != 0:
			diffData = filterByFilePattern(diffData, includes, INCLUDE_FILE_PATTERN)
		changeLog = createDiff(resDir, srcDir, dstDir, diffData)
		createDiffLog(resDir, changeLog)

if __name__ == '__main__':
	main()