import requests
import time
import json
import os
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

class APIPoller:
    def __init__(self):
        """
        Initialize the API poller with configuration from environment variables
        """
        # Get base API URL from environment
        self.api_base_url = os.environ.get('API_URL', 'https://ops.ultrahuman.com/api/web_dashboard/daily_trend')
        self.api_token = os.environ.get('API_TOKEN')
        
        # Optional environment variables with defaults
        self.debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
        
        # Validate required environment variables
        if not self.api_token:
            raise ValueError("API_TOKEN environment variable is required")
        
        self.headers = {
            'Authorization': f'{self.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Initialize InfluxDB client if environment variables are present
        self.influx_url = os.environ.get('INFLUX_URL')
        self.influx_token = os.environ.get('INFLUX_TOKEN')
        self.influx_org = os.environ.get('INFLUX_ORG')
        self.influx_bucket = os.environ.get('INFLUX_BUCKET')
        
        if all([self.influx_url, self.influx_token, self.influx_org, self.influx_bucket]):
            self.influx_client = InfluxDBClient(
                url=self.influx_url,
                token=self.influx_token,
                org=self.influx_org
            )
            # Configure write API with write options
            write_options = WriteOptions(
                batch_size=1,
                flush_interval=1_000,
                write_type=SYNCHRONOUS
            )
            self.write_api = self.influx_client.write_api(write_options=write_options)
            
            # Delete existing data for the timestamp before writing new data
            self.delete_api = self.influx_client.delete_api()
        else:
            self.influx_client = None
            if self.debug_mode:
                print("InfluxDB configuration incomplete - running in debug mode only")

    def store_data(self, data):
        """
        Store the daily data in InfluxDB if configured, overwriting existing data points
        """
        if not self.influx_client:
            return
            
        try:
            if 'data' not in data or 'daily_data' not in data['data']:
                print("No daily data found in API response")
                return

            daily_data = data['data']['daily_data']
            
            for date, metrics in daily_data.items():
                timestamp = datetime.strptime(date, "%Y-%m-%d")
                
                # Delete existing data for this timestamp
                start_time = timestamp
                end_time = timestamp + timedelta(days=1)
                self.delete_api.delete(
                    start=start_time,
                    stop=end_time,
                    predicate='_measurement="daily_metrics"',
                    bucket=self.influx_bucket,
                    org=self.influx_org
                )
                
                if self.debug_mode:
                    print(f"Deleted existing data points for {date}")

                # Create new point
                point = Point("daily_metrics")\
                    .time(timestamp)
                
                for metric_name, metric_value in metrics.items():
                    if metric_value is not None:  # Skip null values
                        point = point.field(metric_name, metric_value)

                self.write_api.write(bucket=self.influx_bucket, org=self.influx_org, record=point)
                print(f"Successfully stored data point for {date}")
                
        except Exception as e:
            print(f"Error storing data in InfluxDB: {e}")