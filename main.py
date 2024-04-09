import pypco
import datetime as dt

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get PCO account and secret from environment variables
PCO_ACCOUNT = os.getenv("PCO_ACCOUNT")
PCO_SECRET = os.getenv("PCO_SECRET")

pco = pypco.PCO(PCO_ACCOUNT, PCO_SECRET)

print("--------------------------------")
print("Checking for this week's plan...")
print("--------------------------------")

nhe_plans = '/services/v2/service_types/95532/plans/'
all_plans = pco.get(nhe_plans)
number_of_plans = all_plans['meta']['total_count']
offset = number_of_plans - 15
offset_url = nhe_plans + '?offset=' + str(offset)
get_plans = pco.get(offset_url)

current = dt.datetime.now()
year, month, day, hour, minute = current.year, current.month, current.day, current.hour, current.minute

epoch_conversion_today = dt.datetime(year, month, day, 0, 0, 0).timestamp()
current_time = dt.datetime(year, month, day, hour, minute, 0).timestamp()

service_id = get_plans['data'][0]['id']

get_date = pco.get(nhe_plans + service_id)['data']['attributes']['sort_date']
split_date = get_date.split("-")
day_split = split_date[2].split("T")
pco_date = dt.datetime(int(split_date[0]), int(split_date[1]), int(day_split[0]), 0, 0, 0).timestamp()
this_week = pco_date + 600000

while epoch_conversion_today > this_week:
    next_plan = pco.get(f'/services/v2/service_types/95532/plans/{service_id}/next_plan')['data']['id']
    get_date = pco.get(nhe_plans + service_id)['data']['attributes']['sort_date']
    split_date = get_date.split("-")
    day_split = split_date[2].split("T")
    pco_date = dt.datetime(int(split_date[0]), int(split_date[1]), int(day_split[0]), 0, 0, 0).timestamp()
    this_week = pco_date + 600000
    service_id = next_plan

service_link = nhe_plans + service_id
service = pco.get(service_link)
service_date = service['data']['attributes']['dates']

is_correct = input(f"Is {service_date} the correct plan date? (y/n): ")
if is_correct.lower() == "n":
    desired_date = input("Enter the service date in YYYY-MM-DD format: ")
    service_id = input("Please enter the service ID: ")
    print("---------------------------")
    print("-------- Song Info --------")
else:
    print("---------------------------")
    print("-------- Song Info --------")

list_of_items = pco.get(service_link + '/items')
list_of_elements = list_of_items['data']

for song_index, song_item in enumerate(list_of_elements, start=1):
    if song_item['attributes']['item_type'] == "song":
        song_id = song_item['relationships']['song']['data']['id']
        song_info = pco.get('/services/v2/songs/' + song_id)
        song_name = song_info['data']['attributes']['title']
        author = song_info['data']['attributes']['author']
        copyright = song_info['data']['attributes']['copyright']

        author_split = [a.strip(',') for a in author.split()] if author else []
        copyright_split = copyright.split('(', 1)[0] if copyright else ''

        song_file_name = f"song{song_index}.txt"
        with open(song_file_name, "w") as f:
            f.write(f"Title: {song_name}\n")
            f.write(f"Author: {' '.join(author_split)}\n")
            f.write(f"Copyright: {copyright_split}")

print("Song information saved successfully.")
