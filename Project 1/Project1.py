import argparse
import sys
import csv

#argparse for error checking
parser = argparse.ArgumentParser()
parser.add_argument("--job", dest="jobFolder", help="job to process")
parser.add_argument("--verbose", action="store_true", help="show verbose")
parser.add_argument("--TC", dest="timecode", help="Timecode to process")
args =  parser.parse_args()

if args.verbose:
    print("Hi Chaja")

if args.jobFolder is None:
    print("No job selected")
    sys.exit(2)
else:
    job = args.jobFolder

if args.timecode:
    timecodeTC = args.timecode

#group list function to group all of integers
def group_list(list):
    group = [[list[0]]]

    for i in range(1, len(list)):
        if list[i-1]+1 == list[i]:
            group[-1].append(list[i])
        else:
            group.append([list[i]])

    return group

#import all the files and split them by whitespace
baselight_import = open('Baselight_export.txt', 'r')
xytech_import = open('Xytech.txt', 'r')
baselight = baselight_import.read().split()
xytech = xytech_import.read().split()

#create dictionary for baselight (key: file names, value: list of line numbers)
baselight_dict = {}

#populate baselight dictionary, ignoring all characters before "starwars"
for item in baselight:
    if item.startswith("/"):
        key = item[item.find('/starwars'):]
        if key not in baselight_dict.keys():
            baselight_dict[key] = []
    if item.isnumeric():
        baselight_dict[key].append(item)

#populate xytech list for file names, using list comprehension
xytech_list = [item for item in xytech if item.startswith("/")]

#find the items in xytech_list that match the key in baselight_dict and group all of its values so we can print out the ranges between numbers. Write this data to the csv file.
with open('xytech_workorder.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Producer","Operator","Job","Notes"])
    writer.writerow([])
    writer.writerow([])
    for item in xytech_list:
        key = item[item.find('/starwars'):]
        if key in baselight_dict.keys():
            nums = [eval(num) for num in baselight_dict[key]]
            nums = group_list(nums)
            for list in nums:
                writer.writerow([item, list[0]]) if len(list) == 1 else writer.writerow([item, f"{list[0]}-{list[-1]}"])

#print to the console that the file has been created successfully
print("xytech_workorder.csv has been created successfully.")
