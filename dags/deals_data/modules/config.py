import os
import yaml
from airflow.configuration import conf

dags_folder = conf.get('core', 'dags_folder')
config_path = os.path.join(dags_folder, "deals_data", "modules", "config.yaml")

# Load config.yaml
config = yaml.safe_load(open(config_path))