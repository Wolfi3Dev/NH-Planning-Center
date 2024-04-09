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

    # Base URL for all NHE Plans
    nhe_plans = '/services/v2/service_types/95532/plans/'

    # User input for the date
    user_date = input("Enter the date (YYYY-MM-DD): ")
    try:
        date_obj = dt.datetime.strptime(user_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please enter date in YYYY-MM-DD format.")
        return

    # Convert user input date to ISO format
    user_date_iso = date_obj.isoformat()

    # Get plans for the specified date
    plans_for_date_response = PCO_KEY.get(f"{nhe_plans}?filter[future_or_past]=future&filter[range_start]={user_date_iso}&filter[range_end]={user_date_iso}")

    # Check if plans exist for the specified date
    if not plans_for_date_response['data']:
        print("No plans found for the specified date.")
        return

    print(f"Plan Date: {user_date}")
    print("---------------------------")

    # Loop through each plan for the specified date
    for plan in plans_for_date_response['data']:
        plan_id = plan['id']
        # Retrieve song information for the plan
        list_of_items = PCO_KEY.get(f"{nhe_plans}{plan_id}/items")['data']
        
        # Filter items to only include those for the specified date
        items_for_date = [item for item in list_of_items if item['attributes'].get('dates') == user_date]

        # Loop through each item in the plan for the specified date
        for item in items_for_date:
            # Check if the item is a song
            if item['attributes']['item_type'] == "song":
                try:
                    song_id = item['relationships']['song']['data']['id']
                    song_info = PCO_KEY.get(f'/services/v2/songs/{song_id}')
                    song_attributes = song_info['data']['attributes']

                    song_name = song_attributes['title']
                    author = song_attributes.get('author', '')
                    song_copyright = song_attributes.get('copyright', '')

                    print("Title:", song_name)
                    print("Author:", author)
                    print("Copyright:", song_copyright)
                    print("---------------------------")

                except Exception as e:
                    print(f"Error processing song: {e}")

    print("Song information has been displayed.")


if __name__ == "__main__":
    main()
