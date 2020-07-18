import os

	
def mapleHandler(  maple, inFileName ): # function, input file (obj), output file (obj)
	

	inFile = open(inFileName, 'r')
	result = map(maple, inFile) 

	filePointerList = dict()
	
	for pairs in result:
		# write to file
		
		for pair in pairs: 
		
			key = pair[0].strip()
			value = str(pair[1]) + '\n'
			file_path = "./test/" + str(key)
			if os.path.isfile( file_path ):
				filePointerList[key].write(value) # append_data
			else:
				filePointerList[key] = open(file_path, 'a') # create_file
				filePointerList[key].write(value) # append_data
				
				
	for pointer in filePointerList.values():
		pointer.close()
	inFile.close()
	
	
def maple(line): # a single line in the file 
	return [ (line.strip(), 1) ]
	
mapleHandler(maple, "test.txt")


