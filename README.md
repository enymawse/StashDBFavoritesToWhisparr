# StashDB Favorite Import to Whisparr

## Overview

`StashDBFavoriteImport.py` is a Python script that imports your favorite performers from [StashDB](https://stashdb.org/) into your [Whisparr](https://whisparr.app/) instance. It queries your StashDB favorite performers via GraphQL and transforms the data into the appropriate format to be used by Whisparr. The data is then sent to Whisparr through its API.

## Features

- Fetches favorite performers from StashDB using GraphQL.
- Queries the Whisparr API to retrieve performer details.
- Transforms and posts performer data into Whisparr.
- Logs successful and failed requests to log files.
- Provides a summary of the import process, including the number of successful and failed requests.

## Requirements

- Python 3.6 or higher
- `requests` library
- `python-dotenv` library

### Install required dependencies:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/enymawse/StashDBFavoritesToWhisparr.git
   cd StashDBFavoritesToWhisparr
   ```

2. Create a `.env` file in the root of the project with the following content:

   ```env
   STASHDB_APIKEY=your-stashdb-apikey
   WHISPARR_APIKEY=your-whisparr-apikey
   ```

   Replace `your-stashdb-apikey` and `your-whisparr-apikey` with your actual API keys.

3. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure your `.env` file is properly set up with valid API keys.

2. Run the script:

   ```bash
   python StashDBFavoritesToWhisparr.py
   ```

3. Once the script completes, it will print a summary:

   ```
   Import complete: X successful, Y failed.
   ```

4. Check the log files for additional details:
   - `StashDBFavoritesToWhisparr.log` for general info logs.
   - `StashDBFavoritesToWhisparr_errors.log` for error logs.

## Example `.env` File

```env
STASHDB_APIKEY=abc123def456
WHISPARR_APIKEY=xyz789ghi012
```

## How It Works

1. The script fetches favorite performers from the StashDB GraphQL API using the provided API key.
2. For each favorite performer, it queries Whisparr using their `stashid`.
3. The performer data is transformed into a format compatible with Whisparr's API.
4. The transformed data is sent to Whisparr via a POST request.
5. The script logs the responses (both successes and errors) and prints a summary of the results at the end.

## Logging

- **General Log**: `StashDBFavoritesToWhisparr.log`
- **Error Log**: `StashDBFavoritesToWhisparr_errors.log`

## API Endpoints

- **StashDB GraphQL API**: https://stashdb.org/graphql
- **Whisparr API**: https://api.whisparr.com
- **Local Whisparr API**: https://yourwhisparrinstance.lan/api/v3

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact

For questions or issues, please open an issue on the GitHub repository.

### Notes:

Ensure you have a `requirements.txt` file that includes the necessary Python libraries like `requests` and `python-dotenv` if you'd like to automate dependency installation:

```txt
requests
python-dotenv
```
