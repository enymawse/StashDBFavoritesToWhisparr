import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename='StashDBFavoritesToWhisparr.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Error logging
error_log = logging.getLogger('error')
error_log.setLevel(logging.ERROR)
error_handler = logging.FileHandler('StashDBFavoritesToWhisparr_errors.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_log.addHandler(error_handler)

# Environment Variables
STASHDB_APIKEY = os.getenv('STASHDB_APIKEY')
WHISPARR_APIKEY = os.getenv('WHISPARR_APIKEY')
ROOT_FOLDER_PATH = os.getenv('ROOT_FOLDER_PATH')
MONITORED = os.getenv('MONITORED') or False
SEARCH_ON_ADD = os.getenv('SEARCH_ON_ADD') or False
QUALITY_PROFILE = os.getenv('QUALITY_PROFILE')

STASHDB_ENDPOINT = 'https://stashdb.org/graphql'
WHISPARR_ENDPOINT = 'http://whisparr.home/api/v3/performer'

HEADERS_STASHDB = {
    'ApiKey': STASHDB_APIKEY,
    'Content-Type': 'application/json'
}
HEADERS_WHISPARR = {
    'X-Api-Key': WHISPARR_APIKEY,
    'Content-Type': 'application/json'
}

# GraphQL query to get favorite performers
QUERY_PERFORMERS = '''
query GetFavoritePerformers($page: Int!) {
    queryPerformers(input: { is_favorite: true, per_page: 100, page: $page }) {
        count
        performers {
            id
        }
    }
}
'''

def fetch_favorites():
    """
    Fetch favorite performers from StashDB with pagination.
    """
    performers = []
    page = 1
    while True:
        variables = {'page': page}
        response = requests.post(STASHDB_ENDPOINT, headers=HEADERS_STASHDB, json={'query': QUERY_PERFORMERS, 'variables': variables})
        
        if response.status_code == 200:
            data = response.json()['data']['queryPerformers']
            performers.extend(data['performers'])
            if len(data['performers']) < 100:
                break
            page += 1
        else:
            error_log.error(f"Error fetching favorites: {response.status_code}, {response.text}")
            break
    return performers

def fetch_whisparr_performer(stashid):
    """
    Fetch performer data from Whisparr using StashID.
    """
    url = f'https://api.whisparr.com/v4/performer/{stashid}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        error_log.error(f"Error fetching performer from Whisparr: {response.status_code}, {response.text}")
        return None

def get_performer_status(status):
    """
    Convert Whisparr status to readable format.
    """
    return "active" if status == 0 else "inactive" if status == 1 else "unknown"

def transform_performer_data(performer_data, id_counter):
    """
    Transform the Whisparr performer data into the desired format for import.
    """
    if performer_data:
        return {
            "fullName": performer_data['Name'],
            "Gender": performer_data['Gender'],
            "HairColor": performer_data['HairColor'],
            "Ethnicity": performer_data['Ethnicity'],
            "Status": get_performer_status(performer_data['Status']),
            "CareerStart": performer_data.get('CareerStart'),
            "foreignId": performer_data['ForeignIds']['StashId'],
            "Images": [
                {
                    "CoverType": img['CoverType'],
                    "Url": f"/MediaCover/performer/{id_counter}/headshot.jpg?lastWrite=638607625773718029",
                    "remoteURL": img['Url']
                } for img in performer_data['Images']
            ],
            "monitored": MONITORED,
            "rootFolderPath": ROOT_FOLDER_PATH,
            "qualityProfileId": QUALITY_PROFILE,
            "searchOnAdd": SEARCH_ON_ADD,
            "tags": [],
            "added": "0001-01-01T07:53:00Z",
            "id": id_counter
        }
    return None

def send_to_whisparr(data, fail_ids, already_imported):
    """
    Send transformed performer data to Whisparr and handle errors.
    """
    response = requests.post(WHISPARR_ENDPOINT, headers=HEADERS_WHISPARR, json=data)
    if response.status_code == 201:
        logging.info(f"Successfully added performer: {data['fullName']}")
        return True
    elif response.status_code == 409:
        error_message = response.json().get("message", "")
        if "UNIQUE constraint failed: Performers.ForeignId" in error_message:
            logging.info(f"Performer already exists: {data['fullName']}")
            already_imported.append({"id": data['foreignId'], "name": data['fullName']})
        else:
            error_log.error(f"Conflict posting performer to Whisparr: {response.status_code}, {error_message}")
    else:
        error_log.error(f"Error posting performer to Whisparr: {response.status_code}, {response.text}")
        fail_ids.append({"id": data['foreignId']})
        return False

def main():
    """
    Main function to fetch and import performers from StashDB to Whisparr.
    """
    performers = fetch_favorites()
    success_count = 0
    already_imported = []
    fail_ids = []
    id_counter = 1

    for performer in performers:
        stashid = performer['id']
        whisparr_data = fetch_whisparr_performer(stashid)
        if whisparr_data:
            transformed_data = transform_performer_data(whisparr_data, id_counter)
            if transformed_data and send_to_whisparr(transformed_data, fail_ids, already_imported):
                success_count += 1
            id_counter += 1

    # Log final report
    print(f"Import complete: {success_count} successful, {len(already_imported)} already imported, {len(fail_ids)} failed.")
    if fail_ids:
        for failed_id in fail_ids:
            error_log.error(f"Failed: {failed_id}")

if __name__ == "__main__":
    main()
