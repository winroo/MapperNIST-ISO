# basic include
import mapper as mf


myCSVtoMap = "test.csv"
pathToSave = "test-iso.csv"


# the main mapping function
# arguments:
#   input = path to the input CSV
#   output = path to the output CSV
#   type = type of mapping
#      0 ISO 27001:2013  -> to ->  NIST 800 53 rev 5
#      1 NIST 800 53 rev 5 -> to -> ISO 27001:2013
#   printDetails = True/False, print the mapped list if True
#
#   accepted CSV format
#   first column: your control 
#   second column: NIST 800 53 rev5 or ISO27001 controls separated by comma
#   examples of acceptable rows:
#       CM0083, PE-20
#       CM0084,"CP-13,PE-20"
#       CM0085,"CP-11, PE-21"

mf.mapper(myCSVtoMap, pathToSave, 1, True)

# this function print the mapping list
#   type = type of mapping
#      0 ISO 27001:2013  -> to ->  NIST 800 53 rev 5
#      1 NIST 800 53 rev 5 -> to -> ISO 27001:2013
#mf.printMap(0)





