def juiceHandler( juice, inFileList, outFileName ):
	
	
	for inFileName in inFileList:
		outFile = open(outFileName, 'a')

		print(inFileName)
		inFile = open( inFileName ,'r')
		result = juice(inFile) 
		
#		outFile = open(outFileName, 'a')
		for item in result:
			#write to file outFile
			outFile.write( inFileName + ':' + str(item) + '\n')
		inFile.close()
		outFile.close()



def file_len(fname):
	import subprocess
	p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	result, err = p.communicate()
	if p.returncode != 0:
			raise IOError(err)
	return int(result.strip().split()[0])
		
def juice(values): # key, list of value
#	result = sum( 1 for _ in values)
	result = file_len(values.name)
	return [result]
	
	
	
inFileList = ['./test/Animal', './test/Dog', './test/Cat', './test/Queen', './test/Bird', "./test/following", "./test/example", "./test/demonstrates", "./test/the", "./test/common"]
outFileName = 'result.txt'

juiceHandler(juice,  inFileList, outFileName)