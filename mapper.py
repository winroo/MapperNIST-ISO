#   ISO 27001 vs NIST 800 53 mapper
#   
#   v0.1 
#   Michal Krelina, EUSPA
#   2023-07-17
#
"""
    Comments:

    the mapping is based strictly on Table 1 in https://csrc.nist.gov/CSRC/media/Publications/sp/800-53/rev-5/final/documents/sp800-53r5-to-iso-27001-mapping.docx
    which was prepared by the NIST. For full understanding of the mapping,
    read the notes in the above linked document.
    Therefore, just ISO 27001:2013 is supported at the moment.

    Note, if you map from NIST to ISO, then, by default a a more specific
    NIST 800 53 controls such as SI-4(14) will be generalised to SI-4 and
    then mapped.
    This can be disabled by setting
        self._NIST_generalisation = False
    But then no mapping will be performed.




"""

import csv
import re

# the main mapping function
# arguments:
#   input = path to the input CSV
#   output = path to the output CSV
#   type = type of mapping
#      0 ISO 27001:2013  -> to ->  NIST 800 53 rev 5
#      1 NIST 800 53 rev 5 -> to -> ISO 27001:2013
#   printDetails = True/False, print the mapped list if True
def mapper(input, output, type, printDetails):

    print("Mapping: ")
    if(type == 0):
        print("\t\t ISO 27001:2022  ->  NIST 800 53 rev 5")
    else:
        print("\t\t NIST 800 53 rev 5 -> ISO 27001:2013")

    print("Running... ")    

    map = Map(input, output, type)

    if(printDetails):
        map.print()

    map.save()

    print("Finsihed and saved to: ", output)




# this function print the mapping list
#   type = type of mapping
#      0 ISO 27001:2013  -> to ->  NIST 800 53 rev 5
#      1 NIST 800 53 rev 5 -> to -> ISO 27001:2013
def printMap(type):

    print("Map: ")
    if(type == 0):
        print("\t\t ISO 27001:2013  ->  NIST 800 53 rev 5") 
        printMap = ISO13toNIST     
    else:
        print("\t\t NIST 800 53 rev 5 -> ISO 27001:2013") 
        printMap = NISTtoISO13

    for key in printMap:
        prnt = key + " => "
        for i in range(len(printMap[key])):
            if i>0:
                prnt += ", " + printMap[key][i]
            else:
                prnt += printMap[key][i]
        print(prnt)


# a mapping class
class Map:
    ## considerin one-to-many separated by ","
    def __init__(self, in_path, out_path, type):
        ## map type:
        ##      0 ISO 27001:2022  -> to ->  NIST 800 53 rev 5
        ##      1 NIST 800 53 rev 5 -> to -> ISO 27001:2013
        self._filePath = in_path
        self._resPath = out_path
        self._mapType = type

        self._NIST_generalisation = True
        
        # set the mapping list
        if self._mapType==0:
            self._dataMap = ISO13toNIST
        else:
            self._dataMap = NISTtoISO13

        #reading user's csv
        self._dataUser = self.read_csv(self._filePath)

        #reading user's data
        self._dataUser = self.cleanBefore(self._dataUser)


        #the mapping process
        for row in self._dataUser:
            mapped = []
            for ref in row[1]:
                val = self._dataMap.get(ref, ref)
                #print("\t\t" + str(ref) + " : " + str(val))
                if ref == val:
                    continue
                mapped.append(val)
            mappedFin = []
            for m in mapped:
                mappedFin += m
            while("" in mappedFin):
                mappedFin.remove("")
            if len(mappedFin) == 0:
                mappedFin.append("None")
            mappedFin.sort()
            row.append(mappedFin)
        self._dataUser = self.cleanAfter(self._dataUser)


        # for tetsing purposes
        #print(self._dataMap)
        #self.print(self._dataUser)


    # cleaning function
    def cleanBefore(self,data):

        lines = len(data)
        for i in range(lines):
            for j in range(len(data[i])):
                data[i][j] = self.clean_cell(str(data[i][j]))

        for i in range(lines):
            data[i][1] = data[i][1].split(',')

        if self._NIST_generalisation:
            for i in range(len(data)):
                for j in range(len(data[i][1])):
                    #print(data[i][1][j], re.sub(r"\([0-9]+\)","",data[i][1][j]))
                    data[i][1][j] = re.sub(r"\([0-9]+\)","",data[i][1][j])
                    # remove potential duplicates
                    data[i][1] = list(dict.fromkeys(data[i][1]))

        return data
    

    # cleaning function
    def cleanAfter(self,data):
        for row in data:
            #print(row)
            #delete duplicates
            row[2] = list(dict.fromkeys(row[2]))

            # delete 'None' if other elements are present
            if len(row[2]) > 1 and 'None' in row[2]:
                row[2].remove('None')
                #for i in len(row[2]):
                #    if row[2][i] == 'None':

        return data
    

    
    def clean_cell(self,s):
        #s = s.replace("(", "_")
        #s = s.replace(")", "_")
        #s = re.sub(r"[^\w\s]", '', s)
        s = re.sub(r"\s+", '', s)
        return s

    def print(self, data = None):
        if data is None:
            data = self._dataUser 
        for record in data:
            for i in range(len(record)):
                if i>0:
                    print("\t" + str(record[i]))
                else:
                    print(record[i])
                
    # save output to the CSV format
    def save(self):
        try:
            with open(self._resPath, 'w') as f:
                writer = csv.writer(f)
                for row in self._dataUser:
                    lowstr = ""
                    for i in range(len(row[2])):
                        if i > 0:
                            lowstr += ", " + row[2][i]
                        else:
                            lowstr += row[2][i]
                    rowstr = [row[0], lowstr]
                    #print(rowstr)
                    writer.writerow(rowstr)
                
        except PermissionError:
            print(f"Error: Permission denied to write the file '{self._resPath}'.")
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")

    # reading CSV format
    def read_csv(self,file_path):
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                data = list(reader)
                
            return data

        except FileNotFoundError:
            print(f"Error: The file '{file_path}' does not exist.")
        except PermissionError:
            print(f"Error: Permission denied to read the file '{file_path}'.")
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")


NISTtoISO13 = {
'AC-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.9.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'AC-2':['A.9.2.1','A.9.2.2','A.9.2.3','A.9.2.5','A.9.2.6'],
'AC-3':['A.6.2.2','A.9.1.2','A.9.4.1','A.9.4.4','A.9.4.5','A.13.1.1','A.14.1.2','A.14.1.3','A.18.1.3'],
'AC-4':['A.13.1.3','A.13.2.1','A.14.1.2','A.14.1.3'],
'AC-5':['A.6.1.2'],
'AC-6':['A.9.1.2','A.9.2.3','A.9.4.4','A.9.4.5'],
'AC-7':['A.9.4.2'],
'AC-8':['A.9.4.2'],
'AC-9':['A.9.4.2'],
'AC-10':['None'],
'AC-11':['A.11.2.8','A.11.2.9'],
'AC-12':['None'],
'AC-13':['Withdrawed from 800 53 rev5'],
'AC-14':['None'],
'AC-15':['Withdrawed from 800 53 rev5'],
'AC-16':['None'],
'AC-17':['A.6.2.1','A.6.2.2','A.13.1.1','A.13.2.1','A.14.1.2'],
'AC-18':['A.6.2.1','A.13.1.1','A.13.2.1'],
'AC-19':['A.6.2.1','A.11.1.5','A.11.2.6','A.13.2.1'],
'AC-20':['A.11.2.6','A.13.1.1','A.13.2.1'],
'AC-21':['None'],
'AC-22':['None'],
'AC-23':['None'],
'AC-24':['A.9.4.1'],
'AC-25':['None'],
'AT-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'AT-2':['7.3','A.7.2.2','A.12.2.1'],
'AT-3':['A.7.2.2'],
'AT-4':['None'],
'AT-5':['Withdrawed from 800 53 rev5'],
'AT-6':['None'],
'AU-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'AU-2':['None'],
'AU-3':['A.12.4.1'],
'AU-4':['A.12.1.3'],
'AU-5':['None'],
'AU-6':['A.12.4.1','A.16.1.2','A.16.1.4'],
'AU-7':['None'],
'AU-8':['A.12.4.4'],
'AU-9':['A.12.4.2','A.12.4.3','A.18.1.3'],
'AU-10':['None'],
'AU-11':['A.12.4.1','A.16.1.7'],
'AU-12':['A.12.4.1','A.12.4.3'],
'AU-13':['None'],
'AU-14':['A.12.4.1'],
'AU-15':['Withdrawed from 800 53 rev5'],
'AU-16':['None'],
'CA-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'CA-2':['A.14.2.8','A.18.2.2','A.18.2.3'],
'CA-3':['A.13.1.2','A.13.2.1','A.13.2.2'],
'CA-4':['Withdrawed from 800 53 rev5'],
'CA-5':['8.3','9.2','10.1'],
'CA-6':['9.3'],
'CA-7':['9.1','9.2','A.18.2.2','A.18.2.3'],
'CA-8':['None'],
'CA-9':['None'],
'CM-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'CM-2':['None'],
'CM-3':['8.1','A.12.1.2','A.14.2.2','A.14.2.3','A.14.2.4'],
'CM-4':['A.14.2.3'],
'CM-5':['A.9.2.3','A.9.4.5','A.12.1.2','A.12.1.4','A.12.5.1'],
'CM-6':['None'],
'CM-7':['A.12.5.1'],
'CM-8':['A.8.1.1','A.8.1.2'],
'CM-9':['A.6.1.1'],
'CM-10':['A.18.1.2'],
'CM-11':['A.12.5.1','A.12.6.2'],
'CM-12':['None'],
'CM-13':['None'],
'CM-14':['None'],
'CP-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'CP-2':['7.5.1','7.5.2','7.5.3','A.6.1.1','A.17.1.1','A.17.2.1'],
'CP-3':['A.7.2.2'],
'CP-4':['A.17.1.3'],
'CP-5':['Withdrawed from 800 53 rev5'],
'CP-6':['A.11.1.4','A.17.1.2','A.17.2.1'],
'CP-7':['A.11.1.4','A.17.1.2','A.17.2.1'],
'CP-8':['A.11.2.2','A.17.1.2'],
'CP-9':['A.12.3.1','A.17.1.2','A.18.1.3'],
'CP-10':['A.17.1.2'],
'CP-11':['A.17.1.2'],
'CP-12':['None'],
'CP-13':['A.17.1.2'],
'IA-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'IA-2':['A.9.2.1'],
'IA-3':['None'],
'IA-4':['A.9.2.1'],
'IA-5':['A.9.2.1','A.9.2.4','A.9.3.1','A.9.4.3'],
'IA-6':['A.9.4.2'],
'IA-7':['A.18.1.5'],
'IA-8':['A.9.2.1'],
'IA-9':['None'],
'IA-10':['None'],
'IA-11':['None'],
'IA-12':['None'],
'IR-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'IR-2':['A.7.2.2'],
'IR-3':['None'],
'IR-4':['A.16.1.4','A.16.1.5','A.16.1.6'],
'IR-5':['None'],
'IR-6':['A.6.1.3','A.16.1.2'],
'IR-7':['None'],
'IR-8':['7.5.1','7.5.2','7.5.3','A.16.1.1'],
'IR-9':['None'],
'IR-10':['Withdrawed from 800 53 rev5'],
'MA-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'MA-2':['A.11.2.4','A.11.2.5'],
'MA-3':['None'],
'MA-4':['None'],
'MA-5':['None'],
'MA-6':['A.11.2.4'],
'MA-7':['None'],
'MP-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'MP-2':['A.8.2.3','A.8.3.1','A.11.2.9'],
'MP-3':['A.8.2.2'],
'MP-4':['A.8.2.3','A.8.3.1','A.11.2.9'],
'MP-5':['A.8.2.3','A.8.3.1','A.8.3.3','A.11.2.5','A.11.2.6'],
'MP-6':['A.8.2.3','A.8.3.1','A.8.3.2','A.11.2.7'],
'MP-7':['A.8.2.3','A.8.3.1'],
'MP-8':['None'],
'PE-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'PE-2':['A.11.1.2'],
'PE-3':['A.11.1.1','A.11.1.2','A.11.1.3'],
'PE-4':['A.11.1.2','A.11.2.3'],
'PE-5':['A.11.1.2','A.11.1.3'],
'PE-6':['None'],
'PE-7':['Withdrawed from 800 53 rev5'],
'PE-8':['None'],
'PE-9':['A.11.1.4','A.11.2.1','A.11.2.2','A.11.2.3'],
'PE-10':['A.11.2.2'],
'PE-11':['A.11.2.2'],
'PE-12':['A.11.2.2'],
'PE-13':['A.11.1.4','A.11.2.1'],
'PE-14':['A.11.1.4','A.11.2.1','A.11.2.2'],
'PE-15':['A.11.1.4','A.11.2.1','A.11.2.2'],
'PE-16':['A.8.2.3','A.11.1.6','A.11.2.5'],
'PE-17':['A.6.2.2','A.11.2.6','A.13.2.1'],
'PE-18':['A.8.2.3','A.11.1.4','A.11.2.1'],
'PE-19':['A.11.1.4','A.11.2.1'],
'PE-20':['A.8.2.3'],
'PE-21':['None'],
'PE-22':['A.8.2.2'],
'PE-23':['A.11.1.4','A.11.2.1'],
'PL-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'PL-2':['7.5.1','7.5.2','7.5.3','10.1','A.14.1.1'],
'PL-3':['Withdrawed from 800 53 rev5'],
'PL-4':['A.7.1.2','A.7.2.1','A.8.1.3'],
'PL-5':['Withdrawed from 800 53 rev5'],
'PL-6':['Withdrawed from 800 53 rev5'],
'PL-7':['8.1','A.14.1.1'],
'PL-8':['A.14.1.1'],
'PL-9':['None'],
'PL-10':['None'],
'PL-11':['None'],
'PM-1':['4.1','4.2','4.3','4.4','5.2','5.3','6.1.1','6.2','7.4','7.5.1','7.5.2','7.5.3','8.1','9.3','10.2','A.5.1.1','A.5.1.2','A.6.1.1','A.18.1.1','A.18.2.2'],
'PM-2':['5.1','5.3','A.6.1.1'],
'PM-3':['5.1','6.2','7.1'],
'PM-4':['6.1.1','6.2','7.5.1','7.5.2','7.5.3','8.3','9.2','9.3','10.1'],
'PM-5':['None'],
'PM-6':['5.3','6.1.1','6.2','9.1'],
'PM-7':['None'],
'PM-8':['None'],
'PM-9':['4.3','4.4','6.1.1','6.1.2','6.2','7.5.1','7.5.2','7.5.3','9.3','10.2'],
'PM-10':['9.3','A.6.1.1'],
'PM-11':['4.1'],
'PM-12':['None'],
'PM-13':['7.2','A.7.2.2'],
'PM-14':['6.2'],
'PM-15':['7.4','A.6.1.4'],
'PM-16':['None'],
'PM-17':['None'],
'PM-18':['None'],
'PM-19':['None'],
'PM-20':['None'],
'PM-21':['None'],
'PM-22':['None'],
'PM-23':['None'],
'PM-24':['None'],
'PM-25':['None'],
'PM-26':['None'],
'PM-27':['None'],
'PM-28':['4.3','6.1.2','6.2','7.4','7.5.1','7.5.2','7.5.3'],
'PM-29':['5.1','5.3','9.2','A.6.1.1'],
'PM-30':['4.4','6.2','7.5.1','7.5.2','7.5.3','10.2'],
'PM-31':['4.4','6.2','7.4','7.5.1','7.5.2','7.5.3','9.1','10.1','10.2'],
'PM-32':['None'],
'PS-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'PS-2':['None'],
'PS-3':['A.7.1.1'],
'PS-4':['A.7.3.1','A.8.1.4'],
'PS-5':['A.7.3.1','A.8.1.4'],
'PS-6':['A.7.1.2','A.7.2.1','A.13.2.4'],
'PS-7':['A.6.1.1','A.7.2.1'],
'PS-8':['7.3','A.7.2.3'],
'PS-9':['A.6.1.1'],
'PT-1':['None'],
'PT-2':['None'],
'PT-3':['None'],
'PT-4':['None'],
'PT-5':['None'],
'PT-6':['None'],
'PT-7':['None'],
'PT-8':['None'],
'RA-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'RA-2':['A.8.2.1'],
'RA-3':['6.1.2','8.2','A.12.6.1'],
'RA-4':['Withdrawed from 800 53 rev5'],
'RA-5':['A.12.6.1'],
'RA-6':['None'],
'RA-7':['6.1.3','8.3','10.1'],
'RA-8':['None'],
'RA-9':['A.15.2.2'],
'RA-10':['None'],
'SA-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','8.1','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'SA-2':['None'],
'SA-3':['A.6.1.1','A.6.1.5','A.14.1.1','A.14.2.1','A.14.2.6'],
'SA-4':['8.1','A.14.1.1','A.14.2.7','A.14.2.9','A.15.1.2'],
'SA-5':['7.5.1','7.5.2','7.5.3','A.12.1.1'],
'SA-6':['Withdrawed from 800 53 rev5'],
'SA-7':['Withdrawed from 800 53 rev5'],
'SA-8':['A.14.2.5'],
'SA-9':['A.6.1.1','A.6.1.5','A.7.2.1','A.13.1.2','A.13.2.2','A.15.2.1','A.15.2.2'],
'SA-10':['A.12.1.2','A.14.2.2','A.14.2.4','A.14.2.7'],
'SA-11':['A.14.2.7','A.14.2.8'],
'SA-12':['Withdrawed from 800 53 rev5'],
'SA-13':['Withdrawed from 800 53 rev5'],
'SA-14':['Withdrawed from 800 53 rev5'],
'SA-15':['A.6.1.5','A.14.2.1'],
'SA-16':['None'],
'SA-17':['A.14.2.1','A.14.2.5'],
'SA-18':['Withdrawed from 800 53 rev5'],
'SA-19':['Withdrawed from 800 53 rev5'],
'SA-20':['None'],
'SA-21':['A.7.1.1'],
'SA-22':['None'],
'SA-23':['None'],
'SC-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'SC-2':['None'],
'SC-3':['None'],
'SC-4':['None'],
'SC-5':['None'],
'SC-6':['None'],
'SC-7':['A.13.1.1','A.13.1.3','A.13.2.1','A.14.1.3'],
'SC-8':['A.8.2.3','A.13.1.1','A.13.2.1','A.13.2.3','A.14.1.2','A.14.1.3'],
'SC-9':['Withdrawed from 800 53 rev5'],
'SC-10':['A.13.1.1'],
'SC-11':['None'],
'SC-12':['A.10.1.2'],
'SC-13':['A.10.1.1','A.14.1.2','A.14.1.3','A.18.1.5'],
'SC-14':['Withdrawed from 800 53 rev5'],
'SC-15':['A.13.2.1'],
'SC-16':['None'],
'SC-17':['A.10.1.2'],
'SC-18':['None'],
'SC-19':['None'],
'SC-20':['None'],
'SC-21':['None'],
'SC-22':['None'],
'SC-23':['None'],
'SC-24':['None'],
'SC-25':['None'],
'SC-26':['None'],
'SC-27':['None'],
'SC-28':['A.8.2.3'],
'SC-29':['None'],
'SC-30':['None'],
'SC-31':['None'],
'SC-32':['None'],
'SC-33':['Withdrawed from 800 53 rev5'],
'SC-34':['None'],
'SC-35':['None'],
'SC-36':['None'],
'SC-37':['None'],
'SC-38':['A.12.1.1','A.12.1.2','A.12.1.3','A.12.1.4','A.12.2.1','A.12.3.1','A.12.4.1','A.12.4.2','A.12.4.3','A.12.4.4','A.12.5.1','A.12.6.1','A.12.6.2','A.12.7.1'],
'SC-39':['None'],
'SC-40':['None'],
'SC-41':['None'],
'SC-42':['A.11.1.5'],
'SC-43':['None'],
'SC-44':['None'],
'SC-45':['None'],
'SC-46':['None'],
'SC-47':['None'],
'SC-48':['None'],
'SC-49':['None'],
'SC-50':['None'],
'SC-51':['None'],
'SI-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.18.1.1','A.18.2.2'],
'SI-2':['A.12.6.1','A.14.2.2','A.14.2.3','A.16.1.3'],
'SI-3':['A.12.2.1'],
'SI-4':['None'],
'SI-5':['A.6.1.4'],
'SI-6':['None'],
'SI-7':['None'],
'SI-8':['None'],
'SI-9':['Withdrawed from 800 53 rev5'],
'SI-10':['None'],
'SI-11':['None'],
'SI-12':['None'],
'SI-13':['None'],
'SI-14':['None'],
'SI-15':['None'],
'SI-16':['None'],
'SI-17':['None'],
'SI-18':['None'],
'SI-19':['None'],
'SI-20':['None'],
'SI-21':['None'],
'SI-22':['None'],
'SI-23':['None'],
'SR-1':['5.2','5.3','7.5.1','7.5.2','7.5.3','A.5.1.1','A.5.1.2','A.6.1.1','A.12.1.1','A.15.1.1','A.18.1.1','A.18.2.2'],
'SR-2':['A.14.2.7'],
'SR-3':['A.15.1.2','A.15.1.3'],
'SR-4':['A.14.2.7'],
'SR-5':['A.15.1.3'],
'SR-6':['A.15.2.1'],
'SR-7':['A.15.2.2'],
'SR-8':['None'],
'SR-9':['None'],
'SR-10':['None'],
'SR-11':['None'],
'SR-12':['None']
}


ISO13toNIST = {
'4.1':['PM-1','PM-11'],
'4.2':['PM-1'],
'4.3':['PM-1','PM-9','PM-28'],
'4.4':['PM-1','PM-9','PM-30','PM-31'],
'5.1':['PM-2','PM-3','PM-29'],
'5.2':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PM-1','PS-1','RA-1','SA-1','SC-1','SI-1','SR-1'],
'5.3':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PM-1','PM-2','PM-6','PM-29','PS-1','RA-1','SA-1','SC-1','SI-1','SR-1'],
'6.1.1':['PM-1','PM-4','PM-6','PM-9'],
'6.1.2':['PM-9','PM-28','RA-3'],
'6.1.3':['RA-7'],
'6.2':['PM-1','PM-3','PM-4','PM-6','PM-9','PM-14','PM-28','PM-30','PM-31'],
'7.1':['PM-3'],
'7.2':['PM-13'],
'7.3':['AT-2','PS-8'],
'7.4':['PM-1','PM-15','PM-28','PM-31'],
'7.5.1':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','CP-2','IA-1','IR-1','IR-8','MA-1','MP-1','PE-1','PL-1','PL-2','PM-1','PM-4','PM-9','PM-28','PM-30','PM-31','PS-1','RA-1','SA-1','SA-5','SC-1','SI-1','SR-1'],
'7.5.2':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','CP-2','IA-1','IR-1','IR-8','MA-1','MP-1','PE-1','PL-1','PL-2','PM-1','PM-4','PM-9','PM-28','PM-30','PM-31','PS-1','RA-1','SA-1','SA-5','SC-1','SI-1','SR-1'],
'7.5.3':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','CP-2','IA-1','IR-1','IR-8','MA-1','MP-1','PE-1','PL-1','PL-2','PM-1','PM-4','PM-9','PM-28','PM-30','PM-31','PS-1','RA-1','SA-1','SA-5','SC-1','SI-1','SR-1'],
'8.1':['CM-3','PL-7','PM-1','SA-1','SA-4'],
'8.2':['RA-3'],
'8.3':['CA-5','PM-4','RA-7'],
'9.1':['CA-7','PM-6','PM-31'],
'9.2':['CA-5','CA-7','PM-4','PM-29'],
'9.3':['CA-6','PM-1','PM-4','PM-9','PM-10'],
'10.1':['CA-5','PL-2','PM-4','PM-31','RA-7'],
'10.2':['PM-1','PM-9','PM-30','PM-31'],
'A.5.1.1':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PM-1','PS-1','RA-1','SA-1','SC-1','SI-1','SR-1'],
'A.5.1.2':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PM-1','PS-1','RA-1','SA-1','SC-1','SI-1','SR-1'],
'A.6.1.1':['AC-1','AT-1','AU-1','CA-1','CM-1','CM-9','CP-1','CP-2','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PM-1','PM-2','PM-10','PM-29','PS-1','PS-7','PS-9','RA-1','SA-1','SA-3','SA-9','SC-1','SI-1','SR-1'],
'A.6.1.2':['AC-5'],
'A.6.1.3':['IR-6'],
'A.6.1.4':['PM-15','SI-5'],
'A.6.1.5':['SA-3','SA-9','SA-15'],
'A.6.2.1':['AC-17','AC-18','AC-19'],
'A.6.2.2':['AC-3','AC-17','PE-17'],
'A.7.1.1':['PS-3','SA-21'],
'A.7.1.2':['PL-4','PS-6'],
'A.7.2.1':['PL-4','PS-6','PS-7','SA-9'],
'A.7.2.2':['AT-2','AT-3','CP-3','IR-2','PM-13'],
'A.7.2.3':['PS-8'],
'A.7.3.1':['PS-4','PS-5'],
'A.8.1.1':['CM-8'],
'A.8.1.2':['CM-8'],
'A.8.1.3':['PL-4'],
'A.8.1.4':['PS-4','PS-5'],
'A.8.2.1':['RA-2'],
'A.8.2.2':['MP-3','PE-22'],
'A.8.2.3':['MP-2','MP-4','MP-5','MP-6','MP-7','PE-16','PE-18','PE-20','SC-8','SC-28'],
'A.8.3.1':['MP-2','MP-4','MP-5','MP-6','MP-7'],
'A.8.3.2':['MP-6'],
'A.8.3.3':['MP-5'],
'A.9.1.1':['AC-1'],
'A.9.1.2':['AC-3','AC-6'],
'A.9.2.1':['AC-2','IA-2','IA-4','IA-5','IA-8'],
'A.9.2.2':['AC-2'],
'A.9.2.3':['AC-2','AC-6','CM-5'],
'A.9.2.4':['IA-5'],
'A.9.2.5':['AC-2'],
'A.9.2.6':['AC-2'],
'A.9.3.1':['IA-5'],
'A.9.4.1':['AC-3','AC-24'],
'A.9.4.2':['AC-7','AC-8','AC-9','IA-6'],
'A.9.4.3':['IA-5'],
'A.9.4.4':['AC-3','AC-6'],
'A.9.4.5':['AC-3','AC-6','CM-5'],
'A.10.1.1':['SC-13'],
'A.10.1.2':['SC-12','SC-17'],
'A.11.1.1':['PE-3'],
'A.11.1.2':['PE-2','PE-3','PE-4','PE-5'],
'A.11.1.3':['PE-3','PE-5'],
'A.11.1.4':['CP-6','CP-7','PE-9','PE-13','PE-14','PE-15','PE-18','PE-19','PE-23'],
'A.11.1.5':['AC-19','SC-42'],
'A.11.1.6':['PE-16'],
'A.11.2.1':['PE-9','PE-13','PE-14','PE-15','PE-18','PE-19','PE-23'],
'A.11.2.2':['CP-8','PE-9','PE-10','PE-11','PE-12','PE-14','PE-15'],
'A.11.2.3':['PE-4','PE-9'],
'A.11.2.4':['MA-2','MA-6'],
'A.11.2.5':['MA-2','MP-5','PE-16'],
'A.11.2.6':['AC-19','AC-20','MP-5','PE-17'],
'A.11.2.7':['MP-6'],
'A.11.2.8':['AC-11'],
'A.11.2.9':['AC-11','MP-2','MP-4'],
'A.12.1.1':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PS-1','RA-1','SA-1','SA-5','SC-1','SC-38','SI-1','SR-1'],
'A.12.1.2':['CM-3','CM-5','SA-10','SC-38'],
'A.12.1.3':['AU-4','SC-38'],
'A.12.1.4':['CM-5','SC-38'],
'A.12.2.1':['AT-2','SC-38','SI-3'],
'A.12.3.1':['CP-9','SC-38'],
'A.12.4.1':['AU-3','AU-6','AU-11','AU-12','AU-14','SC-38'],
'A.12.4.2':['AU-9','SC-38'],
'A.12.4.3':['AU-9','AU-12','SC-38'],
'A.12.4.4':['AU-8','SC-38'],
'A.12.5.1':['CM-5','CM-7','CM-11','SC-38'],
'A.12.6.1':['RA-3','RA-5','SC-38','SI-2'],
'A.12.6.2':['CM-11','SC-38'],
'A.12.7.1':['SC-38'],
'A.13.1.1':['AC-3','AC-17','AC-18','AC-20','SC-7','SC-8','SC-10'],
'A.13.1.2':['CA-3','SA-9'],
'A.13.1.3':['AC-4','SC-7'],
'A.13.2.1':['AC-4','AC-17','AC-18','AC-19','AC-20','CA-3','PE-17','SC-7','SC-8','SC-15'],
'A.13.2.2':['CA-3','SA-9'],
'A.13.2.3':['SC-8'],
'A.13.2.4':['PS-6'],
'A.14.1.1':['PL-2','PL-7','PL-8','SA-3','SA-4'],
'A.14.1.2':['AC-3','AC-4','AC-17','SC-8','SC-13'],
'A.14.1.3':['AC-3','AC-4','SC-7','SC-8','SC-13'],
'A.14.2.1':['SA-3','SA-15','SA-17'],
'A.14.2.2':['CM-3','SA-10','SI-2'],
'A.14.2.3':['CM-3','CM-4','SI-2'],
'A.14.2.4':['CM-3','SA-10'],
'A.14.2.5':['SA-8','SA-17'],
'A.14.2.6':['SA-3'],
'A.14.2.7':['SA-4','SA-10','SA-11','SR-2','SR-4'],
'A.14.2.8':['CA-2','SA-11'],
'A.14.2.9':['SA-4'],
'A.14.3.1':['None'],
'A.15.1.1':['SR-1'],
'A.15.1.2':['SA-4','SR-3'],
'A.15.1.3':['SR-3','SR-5'],
'A.15.2.1':['SA-9','SR-6'],
'A.15.2.2':['RA-9','SA-9','SR-7'],
'A.16.1.1':['IR-8'],
'A.16.1.2':['AU-6','IR-6'],
'A.16.1.3':['SI-2'],
'A.16.1.4':['AU-6','IR-4'],
'A.16.1.5':['IR-4'],
'A.16.1.6':['IR-4'],
'A.16.1.7':['AU-11'],
'A.17.1.1':['CP-2'],
'A.17.1.2':['CP-6','CP-7','CP-8','CP-9','CP-10','CP-11','CP-13'],
'A.17.1.3':['CP-4'],
'A.17.2.1':['CP-2','CP-6','CP-7'],
'A.18.1.1':['AC-1','AT-1','AU-1','CA-1','CM-1','CP-1','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PM-1','PS-1','RA-1','SA-1','SC-1','SI-1','SR-1'],
'A.18.1.2':['CM-10'],
'A.18.1.3':['AC-3','AU-9','CP-9'],
'A.18.1.4':['Appendix J Privacy controls'],
'A.18.1.5':['IA-7','SC-13'],
'A.18.2.1':['None'],
'A.18.2.2':['AC-1','AT-1','AU-1','CA-1','CA-2','CA-7','CM-1','CP-1','IA-1','IR-1','MA-1','MP-1','PE-1','PL-1','PM-1','PS-1','RA-1','SA-1','SC-1','SI-1','SR-1'],
'A.18.2.3':['CA-2','CA-7']
}