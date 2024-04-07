import datetime as dt
import os

import pypco
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get PCO account and secret from environment variables
PCO_ACCOUNT = os.getenv("PCO_ACCOUNT")
PCO_SECRET = os.getenv("PCO_SECRET")
PCO_KEY = pypco.PCO(PCO_ACCOUNT, PCO_SECRET)

# Set PCO API base URL
pco_base_url = "https://api.planningcenteronline.com"


def main():
    print("--------------------------------")
    print("Checking for this week's plan...")
    print("--------------------------------")
    print("test")

    # Base URL for all NHE Plans
    nhe_plans = '/services/v2/service_types/95532/plans/'
    print(nhe_plans)
    # Get Offset URL and most recent 15 plans starting at the farthest in the future
    all_plans = PCO_KEY.get(nhe_plans)
    number_of_plans = all_plans['meta']['total_count']
    offset = number_of_plans - 15
    offset_url = f"{nhe_plans}?offset={offset}"
    get_plans_response = PCO_KEY.get(offset_url)
    
    # Get the current date and time and convert to epoch timestamp for the whole day
    current = dt.datetime.now()
    year, month, day, hour, minute = current.year, current.month, current.day, current.hour, current.minute
    today = dt.datetime(year, month, day, 0, 0, 0).timestamp()

    # Get the first service ID in the list and set the service id variable
    service_id = get_plans_response['data'][0]['id']

    # Retrieve the PCO plan date and convert to epoch timestamp
    get_date_response = PCO_KEY.get(f"{nhe_plans}{service_id}")
    get_date = get_date_response['data']['attributes']['sort_date']
    pco_date = dt.datetime.strptime(get_date.split("T")[0], "%Y-%m-%d").timestamp()
    this_week = pco_date  

    # Loop through all the plans, moving to the next one if it is behind us
    while today >= this_week:

        next_plan_response = PCO_KEY.get(f"/services/v2/service_types/95532/plans/{service_id}/next_plan")
        next_plan = next_plan_response['data']['id']
        previous_plan = PCO_KEY.get(f"/services/v2/service_types/95532/plans/{service_id}/previous_plan")

        get_date_response = PCO_KEY.get(f"{nhe_plans}{service_id}")
      # You are hitting next_plan. Does it have a currunt_plan or something. Look at the url on 52. put That outside of the while loop. 
      # Ahhh
        get_date = get_date_response['data']['attributes']['sort_date']
        pco_date = dt.datetime.strptime(get_date.split("T")[0], "%Y-%m-%d").timestamp()
        this_week = pco_date 

        service_id = next_plan

    is_correct = input(f"Is {get_date} the correct plan date? (y/n): ")

    if is_correct == "n":
        service_id = input("Please enter the service ID: ")
        print("---------------------------")
        print("-------- Song Info --------")
    else:
        print("---------------------------")
        print("-------- Song Info --------")

    list_of_items = PCO_KEY.get(f"{nhe_plans}{service_id}/items")['data']
    song_file_num = 0
    song_number = 0

    for x in list_of_items:
        if x['attributes']['item_type'] == "song":
            try:
                song_id = x['relationships']['song']['data']['id']
                song_info = PCO_KEY.get(f'/services/v2/songs/{song_id}')
                song_attributes = song_info['data']['attributes']

                song_name = song_attributes['title']
                author = song_attributes['author']
                song_copyright = song_attributes['copyright']

                song_number += 1
                song_file_num += 1

                print("---------------------------")
                print(song_name)

                # Write song name to file
                song_file = f"song{song_number}name.txt"
                with open(song_file, "w") as f:
                    f.write(song_name)

                # Write author info to file
                author_info = " ".join(
                    [word.replace(',', '') for word in author.split() if word.lower() not in ['and', 'with']])
                if author_info:
                    print(author_info)
                    with open(f"song{song_file_num}info.txt", "w") as f:
                        f.write(author_info)

                # Write copyright info to file
                if song_copyright:
                    copyright_info = " ".join(song_copyright.split()[:5])
                    print(copyright_info)
                    with open(f"song{song_file_num}info.txt", "a") as f:
                        f.write(f"\n{copyright_info}")

            except Exception as e:
                print(f"Error processing song: {e}")


if __name__ == "__main__":
    main()
