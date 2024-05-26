from elasticsearch import Elasticsearch
import pandas as pd
from tqdm import tqdm

import config

client = Elasticsearch(
  config.ELASTIC_HOST,
  api_key=config.ELASTIC_API_KEY
)

eb_index = "ladies"

eb_mapping = {
    "mappings": {
        "properties": {
            "collection": {"type": "constant_keyword", "value": "Ladies’ Edinburgh Debating Society"},
            "series_uri": {"type": "keyword"},
            "vol_num": {"type": "integer"},
            "vol_title": {"type": "keyword"},
            "genre": {"type": "keyword"},
            "print_location": {"type": "keyword", "null_value": "Unknown" },
            "year_published": {"type": "integer", "null_value": -1},
            "series_num": {"type": "integer"},
            "name": {"type": "text",
                     "fields": {
                         "keyword": {
                             "type": "keyword"
                         }
                     }
                     },
            "alter_names": {"type": "text"},
            "term_type": {"type": "keyword"},
            "page_num": {"type": "integer"},
            "description": {"type": "text"},
            "description_uri": {"type": "keyword"},
        }
    }
}


if __name__ == "__main__":
    # Load the dataframe
    ladies_dataframe = pd.read_json("ladies_kg_nls_dataframe", orient="index")
    ladies_dataframe["year_published"].fillna(-1, inplace=True)
    ladies_dataframe["name"] = ladies_dataframe["vol_title"]
    # Create the index with the defined mapping
    if not client.indices.exists(index=eb_index):
        client.indices.create(index=eb_index, body=eb_mapping)

    page_list = ladies_dataframe.to_dict('records')
    total = len(page_list)
    count = 0
    with tqdm(total=total, desc="Ingestion Progress", unit="step") as pbar:
        for doc in page_list:
            count += 1
            pbar.update(1)
            client.index(index=eb_index, id=doc["page_uri"], document=doc)
