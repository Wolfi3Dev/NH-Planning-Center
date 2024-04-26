import pypco
import os
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get PCO account and secret from environment variables
PCO_ACCOUNT = os.getenv("PCO_ACCOUNT")
PCO_SECRET = os.getenv("PCO_SECRET")

pco = pypco.PCO(PCO_ACCOUNT, PCO_SECRET)

# Print header
print("--------------------------------")
print("Checking for this week's plan...")
print("--------------------------------")

# Get plans
nhe_plans = '/services/v2/service_types/95532/plans/'
all_plans = pco.get(nhe_plans)
number_of_plans = all_plans['meta']['total_count']
offset = number_of_plans - 15
offset_url = nhe_plans + '?offset=' + str(offset)
get_plans = pco.get(offset_url)

# Get current date and time
current = datetime.now()
year = current.year
month = current.month
day = current.day
hour = current.hour
minute = current.minute

# Convert to epoch time
timenow = datetime.now()
epoch_conversion_today = datetime(year, month, day, 0, 0, 0).timestamp()
current_time = datetime(year, month, day, hour, minute, 0).timestamp()

# Get service ID
service_id = get_plans['data'][0]['id']

# Get plan date
get_date = pco.get(nhe_plans + service_id)['data']['attributes']['sort_date']
split_date = get_date.split("-")
day_split = (split_date[2]).split("T")
pco_year = split_date[0]
pco_month = split_date[1]
pco_day = day_split[0]
pco_date = datetime(int(pco_year), int(pco_month), int(pco_day), 0, 0, 0).timestamp()
this_week = pco_date + 600000

# Loop until we find the current week's plan
while epoch_conversion_today > this_week:
    next_plan = pco.get('/services/v2/service_types/95532/plans/' + service_id + '/next_plan')['data']['id']
    get_date = pco.get(nhe_plans + service_id)['data']['attributes']['sort_date']
    split_date = get_date.split("-")
    day_split = (split_date[2]).split("T")
    pco_year = split_date[0]
    pco_month = split_date[1]
    pco_day = day_split[0]
    pco_date = datetime(int(pco_year), int(pco_month), int(pco_day), 0, 0, 0).timestamp()
    this_week = pco_date + 600000
    service_id = next_plan

# Get service information
service = pco.get(nhe_plans + service_id)
service_date = service['data']['attributes']['dates']

# Ask user if the plan date is correct
is_correct = input("Is " + service_date + " the correct plan date? (y/n):")
if is_correct == "n":
    service_id = input("Please enter the service ID: ")
    print("---------------------------")
    print("-------- Song Info --------")
else:
    print("---------------------------")
    print("-------- Song Info --------")

# Get song information
service_link = nhe_plans + service_id
list_of_items = pco.get(nhe_plans + service_id + '/items')
list_of_elements = list_of_items['data']

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

        # Write song name to file
        with open("song" + str(song_number) + "name" + ".txt", "w") as f:
            f.write(song_name)

        author = song_info['data']['attributes']['author']
        copyright = song_info['data']['attributes']['copyright']

        # Remove commas and "and" from author list
        if author:
            author_split = author.split()
            if "," in author_split:
                author_split.remove(",")
            elif "and" in author_split:
                author_split.remove("and")
            comma_removed = [ele.replace(",", '') for ele in author_split]
        else:
            author_split = []
        if copyright:
            copyright_split = copyright.split()
        else:
            copyright_split = []

        song_file_num += 1

        if len(comma_removed) <= 2:
            print(" ".join(comma_removed[0:2]))
            with open("song" + str(song_file_num) + "info.txt", "w") as f:
                f.write(" ".join(comma_removed[0:2]))
        elif not author_split:
            with open("song" + str(song_file_num) + "info.txt", "w") as f:
                f.write("")
        else:
            print(" ".join(comma_removed[0:2]) + " | " + " ".join(comma_removed[2:4]))
            with open("song" + str(song_file_num) + "info.txt", "w") as f:
                f.write(" ".join(comma_removed[0:2]) + " | " + " ".join(comma_removed[2:4]))

        if len(copyright_split) <= 5:
            print(" ".join(copyright_split))
            with open("song" + str(song_file_num) + "info.txt", "a") as f:
                f.write("\n" + " ".join(copyright_split))
        else:
            new_copyright = " ".join(copyright_split[0:4])
            with open("song" + str(song_file_num) + "info.txt", "a") as f:
                f.write("\n")
                if "(" in new_copyright:
                    paren_copyright = new_copyright.split("(")
                    f.write(paren_copyright[0])
                    print(paren_copyright[0])
                elif "," in new_copyright:
                    comma_copyright = new_copyright.split(",")
                    f.write(comma_copyright[0])
                    print(comma_copyright[0])
                else:
                    f.write(new_copyright)
                    print(new_copyright)