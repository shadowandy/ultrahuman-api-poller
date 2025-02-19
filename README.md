# Polling Daily Trends metrics from Ultrahuman

These codes extracts the daily trends from https://vision.ultrahuman.com and stores them into InfluxDB for visualisation using Grafana. This setup is just the API poller that extracts metrics and stores into InfluxDB.

The metrics extracted are:
- sleep_score
- total_sleep
- awake_time
- deep_sleep
- rem_sleep
- light_sleep
- sleep_efficiency
- movement_score
- total_steps
- total_calories
- phase_advance_steps
- recovery_score
- average_temperature
- avg_rhr
- avg_hrv
- activity_mins

# Requirements

For this to work, it requires your "Authorization" key which you can easily get via the browser's inspect element feature after login.

