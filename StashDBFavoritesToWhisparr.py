import os
import requests
import json
import logging

# Set up logging
logging.basicConfig(filename='StashDBFavoriteImport.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
error_log = logging.getLogger('error')
error_log.setLevel(logging.ERROR)
error_handler = logging.FileHandler('StashDBFavoriteImport_errors.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_log.addHandler(error_handler)

# Environment Variables
STASHDB_APIKEY = os.getenv('STASHDB_APIKEY')
WHISPARR_APIKEY = os.getenv('WHISPARR_APIKEY')

STASHDB_ENDPOINT = 'https://stashdb.org/graphql'
WHISPARR_ENDPOINT = 'https://whisparr.home/api/v3/performer'
HEADERS_STASHDB = {
    'Authorization': f'ApiKey {STASHDB_APIKEY}',
    'Content-Type': 'application/json'
}
HEADERS_WHISPARR = {
    'X-Api-Key': WHISPARR_APIKEY,
    'Content-Type': 'application/json'
}

# GraphQL query to get favorite performers
query = '''
query GetFavoritePerformers {
    queryPerformers(input: { is_favorite: true, per_page: 100 }) {
        count
        performers {
            id
        }
    }
}
'''

# Fetch favorite performers from StashDB
def fetch_favorites():
    response = requests.post(STASHDB_ENDPOINT, headers=HEADERS_STASHDB, json={'query': query})
    if response.status_code == 200:
        return response.json()['data']['queryPerformers']['performers']
    else:
        error_log.error(f"Error fetching favorites: {response.status_code}, {response.text}")
        return []

# Fetch performer data from Whisparr using stashid
def fetch_whisparr_performer(stashid):
    url = f'https://api.whisparr.com/v4/performer/{stashid}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        error_log.error(f"Error fetching performer from Whisparr: {response.status_code}, {response.text}")
        return None

# Transform the Whisparr data into the desired format
def transform_performer_data(performer_data, id_counter):
    if performer_data:
        return {
            "fullName": performer_data['Name'],
            "Gender": performer_data['Gender'],
            "HairColor": performer_data['HairColor'],
            "Ethnicity": performer_data['Ethnicity'],
            "Status": "active" if performer_data['Status'] == 0 else "retired",
            "CareerStart": performer_data.get('CareerStart', None),
            "foreignId": performer_data['ForeignIds']['StashId'],
            "Images": [
                {
                    "CoverType": img['CoverType'],
                    "Url": f"/MediaCover/performer/{id_counter}/headshot.jpg?lastWrite=638607625773718029",
                    "remoteURL": img['Url']
                } for img in performer_data['Images']
            ],
            "monitored": True,
            "rootFolderPath": "/data/media/videos/",
            "qualityProfileId": 4,
            "searchOnAdd": True,
            "tags": [],
            "added": "0001-01-01T07:53:00Z",
            "id": id_counter
        }
    return None

# Send transformed performer data to Whisparr
def send_to_whisparr(data):
    response = requests.post(WHISPARR_ENDPOINT, headers=HEADERS_WHISPARR, json=data)
    if response.status_code == 201:
        logging.info(f"Successfully added performer: {data['fullName']}")
        return True
    else:
        error_log.error(f"Error posting performer to Whisparr: {response.status_code}, {response.text}")
        return False

# Main process
def main():
    performers = fetch_favorites()
    success_count = 0
    fail_count = 0
    id_counter = 1

    for performer in performers:
        stashid = performer['id']
        whisparr_data = fetch_whisparr_performer(stashid)
        if whisparr_data:
            transformed_data = transform_performer_data(whisparr_data, id_counter)
            if transformed_data and send_to_whisparr(transformed_data):
                success_count += 1
            else:
                fail_count += 1
            id_counter += 1

    print(f"Import complete: {success_count} successful, {fail_count} failed.")

if __name__ == "__main__":
    main()
