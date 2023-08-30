import argparse

import os

import pymongo

import xlsxwriter

import subprocess



#pls dont hack me chaja

client = pymongo.MongoClient("mongodb+srv://caitlinjrafael:HQNcgeZufdadIIIa@cluster0.bd9hhj6.mongodb.net/?retryWrites=true&w=majority")

db = client["Project2"]

col1 = db["orders"]

col2 = db["frames"]



#argparse for error checking

parser = argparse.ArgumentParser()

parser.add_argument("--verbose", action="store_true", help="Print to Console")

parser.add_argument("--output", action="store_true", help="Output to XLS")

parser.add_argument("--process", dest="video", help="Process Video File")

args = parser.parse_args()



#group list of nums for the frame ranges

def group_list(list):

 group = [[list[0]]]



 for i in range(1, len(list)):

 if list[i-1]+1 == list[i]:

 group[-1].append(list[i])

 else:

 group.append([list[i]])



 return group



#use ffmpeg to get the duration of video as a timecode

def timecode_duration(video):

 command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video} -sexagesimal"

 return subprocess.getoutput(command)



#get fps of a video

def fps(video):

 command = f"ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate {video}"

 return int(subprocess.getoutput(command).split("/")[0])



#convert timecode to frames

def tc_to_frames(video):

 split_tc = timecode_duration(video).split(":")

 split_sec = split_tc[2].split(".")

 hh = int(split_tc[0])

 mm = int(split_tc[1])

 ss = int(split_sec[0])

 f = (int(split_sec[1]) * .0001) #this is to round ff up to a whole number

 ff = round(f)

 return ff + ((ss + mm*60 + hh*3600) * fps(video))



#convert frames to timecode

def frames_to_tc(frames):

 hh = frames/(60*60*60)

 mm = (frames/(60*60)) % 60

 ss = (frames/60) % 60

 ff = frames%60

 return ( "%02d:%02d:%02d.%02d" % ( hh, mm, ss, ff))



#get a video input and process it

if args.video is None:

 print("No Video To Process Found")

else:

 video = args.video

 #get the duration of video in timecode, then convert that to frames to get total frames in video

 duration = timecode_duration(video)

 total_frames = tc_to_frames(video)

 print(f"Video: {video}\nDuration: {duration}\nTotal Frames: {total_frames}\nAll Ranges Under {total_frames}:")

 #write a query to get only frames within the range

 query = { "frames": { "$lt": total_frames } }

 x = col2.find(query)

 #open the xls file and populate with the data found in query



 #if output selected, create xls file and add the first rows

 if args.output:

 workbook = xlsxwriter.Workbook('output.xls')

 worksheet = workbook.add_worksheet()

 headers = ["User on File", "Date of File", "Location", "Frames", "Timecode Range", "Thumbnail"]

 worksheet.write_row(0, 0, headers)

 row = 4

 for data in x:

 values = list(data.values())

 ranges = values[4]

 print(data)

 if args.output:

 #if the range is a list, then find the median frame and use that to make a thumbnail

 if type(ranges) == list:

 start = ranges[0]

 end = ranges[-1]

 median = int((start + end)/2)

 os.system(f"yes | ffmpeg -ss {frames_to_tc(median)} -i {video} -vf scale=96:74 -vframes 1 output.jpg")

 worksheet.write_row(row, 0, [values[1], values[2], values[3], f"{start}-{end}", f"{frames_to_tc(start)}-{frames_to_tc(end)}"])

 worksheet.insert_image(row, 5, 'output.jpg')

 row += 1

 else:

 os.system(f"yes | ffmpeg -ss {frames_to_tc(ranges)} -i {video} -vf scale=96:74 -vframes 1 output.jpg")
