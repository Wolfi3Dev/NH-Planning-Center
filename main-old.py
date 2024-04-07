import pypco
import os
import json
import time
import requests
from datetime import date
import datetime as dt



PCO_KEY = "39d4df6e5549b21a5ca72797e2cce2d2dc61924fbc184083210658be24059048"
PCO_SECRET = "a580066875d4e48647911cd48066955e39cf9dac09145aff3a810257a20c1ca5"


pco = pypco.PCO(PCO_KEY,PCO_SECRET)

print("--------------------------------")
print("Checking for this week's plan...")
print("--------------------------------")



## --- Option for manually adding service IDs --- ##
#service_id = input("Enter Service ID: ")
#service_id = "68159445"

##--- Base URL for all NHE Plans --- ##
nhe_plans = '/services/v2/service_types/95532/plans/'

## Get Offset url and most recent 15 plans starting at the farthest in the future
all_plans = pco.get(nhe_plans)
number_of_plans = all_plans['meta']['total_count']
offset = number_of_plans - 15
offset_url = nhe_plans + '?offset=' + str(offset)
get_plans = pco.get(offset_url)

## Get the current date and time and convert to epoch timestamp for the whole day
## 86400 seconds for epoch day
current = dt.datetime.now()
year = current.year
month = current.month
day = current.day
hour = current.hour
minute = current.minute
#print(year, " ", month, " ", day)
timenow = dt.datetime.now()
epoch_conversion_today = dt.datetime(year,month,day,0,0,0).timestamp()
current_time = dt.datetime(year,month,day,hour,minute,0).timestamp()


## Get the first of the service IDs in the list and set the service id variable
service_id = get_plans['data'][0]['id']
#print(service_id, " service id")

## Retrieve the PCO plan date and convert to epoch timestamp
get_date = pco.get(nhe_plans + service_id)['data']['attributes']['sort_date']
split_date = get_date.split("-")
day_split = (split_date[2]).split("T")
pco_year = split_date[0]
pco_month = split_date[1]
pco_day = day_split[0]
pco_date = dt.datetime(int(pco_year),int(pco_month),int(pco_day),0,0,0).timestamp()
this_week = pco_date + 600000

## Loop through all the plans, moving to the next one if it is behind us

while epoch_conversion_today > this_week:
  #get next service_id
  #while loop?
  next_plan = pco.get('/services/v2/service_types/95532/plans/' + service_id + '/next_plan')['data']['id']
  #print(next_plan)
  get_date = pco.get(nhe_plans + service_id)['data']['attributes']['sort_date']
  split_date = get_date.split("-")
  day_split = (split_date[2]).split("T")
  pco_year = split_date[0]
  pco_month = split_date[1]
  pco_day = day_split[0]
  pco_date = dt.datetime(int(pco_year),int(pco_month),int(pco_day),0,0,0).timestamp()
  this_week = pco_date + 600000
  ###
  #print("service date: " + str(pco_date))
  service_id = next_plan
  #number += 1
  #print(str(number))
    
#for x in list_of_elements:
#  if x['attributes']['item_type'] == "song":
#    song_title = x['attributes']['title'].split('-')[0]
#    song_number += 1
#    print("Song " + str(song_number) + ": " + song_title)
#    #song_file = "song" + str(song_number) + "name" + ".txt"
#    #f = open(song_file, "w")
#    #f.write(song_title)
#    #f.close()
#print()
#print()
service = pco.get(nhe_plans + service_id)
service_date = service['data']['attributes']['dates']
#print("Service date: " + service_date)

is_correct = input("Is " + service_date + " the correct plan date? (y/n):")
if is_correct == "n":
  service_id = input("Please enter the service ID: ")
  print("---------------------------")
  print("-------- Song Info --------")
else:
  print("---------------------------")
  print("-------- Song Info --------")
'''
for x in nhe_plans:
  if pco_date < epoch_conversion_today:
    print("old service")
    next_plan = service['data']['relationships']['next_plan']['data']['id']
    service_id = str(next_plan)
  elif pco_date == epoch_conversion_today:
    print("today!")
  else:
    print("future plan")

'''
'''
service = pco.get(nhe_plans + service_id)
service_date = service['data']['attributes']['dates']
print("Service date: " + service_date)

if pco_date < epoch_conversion_today:
  print("Plan is expired, moving to the next plan")
  next_plan = service['data']['relationships']['next_plan']['data']['id']
  print(next_plan)

elif pco_date == epoch_conversion_today:
  print("Updated the Copyright info")
else: 
  print("Going back one plan")
'''
service_link = nhe_plans + service_id
list_of_items = pco.get(nhe_plans + service_id + '/items')
list_of_elements = list_of_items['data']

# For each song in the service, get all elements with the attribute of "Song"
song_number = 0
song_file_num = 0
for x in list_of_elements:
  if x['attributes']['item_type'] == "song":
    song_id = x['relationships']['song']['data']['id']
    song_info = pco.get('/services/v2/songs/' + song_id)
    song_name = song_info['data']['attributes']['title']
    song_number += 1
    print("---------------------------")
    print(song_name)
    # For each song, write the information to the file, and create it if it does not exist
    song_file = "song" + str(song_number) + "name" + ".txt"
    f = open(song_file, "w")
    f.write(song_name)
    f.close()
    author = song_info['data']['attributes']['author']
    copyright = song_info['data']['attributes']['copyright']
    #print(author)
    if copyright is not None:
      copyright_split = copyright.split()
      author_split = author.split()
      #print(author_split)
    elif copyright is None:
      copyright_split = ""
      author_split = ""
    song_file_num += 1
    if "," in author_split:
      author_split.remove(",")
    
    elif "and" in author_split:
      author_split.remove("and")
    comma = ","
    comma_removed = [ele.replace(comma, '') for ele in author_split]
    if len(comma_removed) <= 2:
      print(" ".join(comma_removed[0:2]))
      song_file = "song" + str(song_file_num) + "info"
      f = open(song_file, "w")
      f.write(" ".join(comma_removed[0:2]))
      f.close()
    elif author_split == "":
      song_file = "song" + str(song_file_num) + "info"
      f = open(song_file, "w")
      f.write("")
      f.close()
    else:
      print(" ".join(comma_removed[0:2]) + " | " + " ".join(comma_removed[2:4]))
      song_file = "song" + str(song_file_num) + "info"
      f = open(song_file, "w")
      f.write(" ".join(comma_removed[0:2]) + " | " + " ".join(comma_removed[2:4]))
      f.close()

    if len(copyright_split) <= 5:
      print(" ".join(copyright_split))
      song_info_file = "song" + str(song_file_num) + "info"
      f = open(song_info_file, "a")
      f.write("\n" + " ".join(copyright_split))
      f.close()
      #print()
    else:
      new_copyright = (" ".join(copyright_split[0:4]))
      song_info_file = "song" + str(song_file_num) + "info"
      f = open(song_info_file, "a")
      f.write("\n")
      if "(" in new_copyright:
        paren_copyright = new_copyright.split("(")
        f.write(paren_copyright[0])
        f.close()
        print(paren_copyright[0])
        #print()
      elif "," in new_copyright:
        comma_copyright = new_copyright.split(",")
        f.write(comma_copyright[0])
        f.close()
        print(comma_copyright[0])
        #print()
      else:
        f.write(new_copyright)
        f.close()
        print(new_copyright)
        #print()
print("---------------------------")
'''
    #song_file = "songname"
    for i in range (4):
      song_file = "songname" + str(i) + ".txt"
      f = open(song_file, "w")
      f.write("This is a test" + str(i) + ".")
      f.close()
      print("\u00A9")

'''
