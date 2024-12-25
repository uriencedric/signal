from datetime import datetime
from io import StringIO

import pandas as pd
import requests


def convert_timestamp_millis_to_date(timestamp_ms):
    return datetime.fromtimestamp(timestamp_ms / 1000)


def convert_timestamp_sec_to_date(timestamp_ms):
    return datetime.fromtimestamp(timestamp_ms)


def fetch_csv_as_dataframe(url, new_columns=None):
    """
    Fetches a CSV file from a given URL and returns it as a pandas DataFrame.
    :param list new_columns: 
    :param str url: The URL of the CSV file to fetch.
    :return pd.DataFrame: A pandas DataFrame containing the CSV data, or None if the fetch fails.
    """

    if new_columns is None:
        new_columns = []
    try:
        # Make the GET request to fetch the CSV data
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Convert the text content of the response to a DataFrame
        csv_data = response.text
        df = pd.read_csv(StringIO(csv_data), skiprows=1)  # Skip the first row with comments

        if new_columns:
            if len(new_columns) != len(df.columns):
                raise ValueError("Length of new_column_names must match the number of columns in the DataFrame")
            df.columns = new_columns

        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV data: {e}")
        return None

