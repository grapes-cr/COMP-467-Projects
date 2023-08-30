import argparse
import sys
import pymongo
import csv

client = pymongo.MongoClient(my_token)
db = client["Project2"]
col1 = db["orders"]
col2 = db["frames"]

#argparse for error checking
parser = argparse.ArgumentParser()
parser.add_argument("--files", dest="work_files", help="Files to Process", nargs="+")
parser.add_argument("--verbose", action="store_true", help="Print to Console")
parser.add_argument("--xytech", dest="xytech_file", help="Choose Xytech File")
parser.add_argument("--output", action="store_true", help="Output to CSV")
args =  parser.parse_args()

if args.work_files is None:
    print("No Baselight or Flame files selected")
    sys.exit(2)
else:
    job = args.work_files

#group list of nums for the frame ranges
def group_list(list):
    group = [[list[0]]]

    for i in range(1, len(list)):
        if list[i-1]+1 == list[i]:
            group[-1].append(list[i])
        else:
            group.append([list[i]])

    return group

#if output selected, create xytech_workorder.csv and add the first rows
if args.output:
    with open('xytech_workorder.csv', 'a+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Machine","User on File","Date of File","Location","Frames"])
        writer.writerow([])
        writer.writerow([])

#for every file listed in --files, populate DB with collections, print to console with --verbose and populate csv with --output
for file in job:
    list = file.split("_")
    date = list[2].split(".")[0]
    if args.verbose:
        print("")
        print(list[0], list[1], date)
        print("-----")
    col1.insert_one({ "machine": list[0], "user_on_file": list[1], "date_of_file": date })
    file_contents = open(file, 'r').read().split()
    file_dict = {}

    if args.xytech_file is None:
        print("No Xytech file selected")
    else:
        for item in file_contents:
            if list[0] == "Baselight":
                if item.startswith("/"):
                    key = item[item.find('Avatar'):]
                    if key not in file_dict.keys():
                        file_dict[key] = []
            if list[0] == "Flame":
                if item.startswith("Avatar"):
                    key = item[item.find('Avatar'):]
                    if key not in file_dict.keys():
                        file_dict[key] = []
            if item.isnumeric():
                file_dict[key].append(item)

        file = args.xytech_file
        xytech_import = open(file, 'r')
        xytech = xytech_import.read().split()
        xytech_list = [item for item in xytech if item.startswith("/")]

        with open('xytech_workorder.csv', 'a+', newline='') as file:
            writer = csv.writer(file)
            for item in xytech_list:
                key = item[item.find('Avatar'):]
                if key in file_dict.keys():
                    nums = [eval(num) for num in file_dict[key]]
                    nums = group_list(nums)
                    for li in nums:
                        if len(li) == 1:
                            col2.insert_one({ "user_on_file": list[1], "date_of_file": date, "location": item, "frames": f"{li[0]}"})
                            if args.verbose:
                                print(item, li[0])  
                            if args.output:
                                writer.writerow([list[0], list[1], date, item, li[0]])  
                        else:
                            col2.insert_one({ "user_on_file": list[1], "date_of_file": date, "location": item, "frames": f"{li[0]}-{li[-1]}"})
                            if args.verbose:
                                print(item, f"{li[0]}-{li[-1]}")
                            if args.output:
                                writer.writerow([list[0], list[1], date, item, f"{li[0]}-{li[-1]}"])  
            
            print("Successfully added to DB.")

if args.output:
    print("\nxytech_workorder.csv was successfully created.")