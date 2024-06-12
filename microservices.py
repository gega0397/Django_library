import sys
import threading
import time
import requests
from datetime import datetime, timedelta
from collections import deque
import pytz
from decouple import config

base_urls = {'reserve': 'http://localhost:8000/api/reserve_due',
             'borrow': 'http://localhost:8000/api/borrow_due'}
token_url = "http://localhost:8000/api/token/"
token_refresh = "http://localhost:8000/api/token/refresh/"

FETCH_INTERVAL_MINUTES = 10

credentials = {
    "email": "system@mail.com",
    "password": config('SYSTEM_PASSWORD')
}

access_token = None
refresh_token = None
token_lock = threading.Lock()

data_queue = deque()


def authenticate():
    global access_token, refresh_token
    response = requests.post(token_url, json=credentials)
    if response.status_code == 200:
        data = response.json()
        with token_lock:
            access_token = data.get("access")
            refresh_token = data.get("refresh")
        print("Authentication successful")
    else:
        print("Authentication failed")


def refresh_access_token():
    global access_token
    with token_lock:
        response = requests.post(token_refresh, json={"refresh": refresh_token})
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access")
            print("Access token refreshed")
        else:
            print("Failed to refresh access token")


def fetch_data(start_time, end_time):
    global access_token
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    params = {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat()
    }

    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        refresh_access_token()
        return fetch_data(start_time, end_time)
    else:
        print(f'Failed to fetch data: {response.status_code}')
        return None


def data_provider(data_queue):
    tz = pytz.timezone('Asia/Tbilisi')
    start_time = datetime.now(tz)
    end_time = start_time + timedelta(minutes=FETCH_INTERVAL_MINUTES)

    while True:
        data = fetch_data(start_time, end_time)
        print('data', data)
        if data:
            for item in data:
                data_queue.append(item)
        time.sleep(FETCH_INTERVAL_MINUTES * 60)
        start_time = end_time
        end_time = start_time + timedelta(minutes=FETCH_INTERVAL_MINUTES)


def data_processor(data_queue):
    while True:
        if data_queue:
            data = data_queue.popleft()
            print(data)
            tbilisi_tz = pytz.timezone('Asia/Tbilisi')
            now = datetime.now(tz=tbilisi_tz)
            due_date = datetime.fromisoformat(data['due_date'])

            if now >= due_date:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                }
                response = requests.post(base_url, headers=headers, json=[data])
                if response.status_code == 200:
                    print('Data sent successfully')
                elif response.status_code == 401:
                    refresh_access_token()
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                    }
                    response = requests.post(base_url, headers=headers, json=[data])
                    if response.status_code == 200:
                        print('Data sent successfully after refreshing token')
                    else:
                        print(f'Failed to send data after refreshing token: {response.status_code}')
                else:
                    print(f'Failed to send data: {response.status_code}')
            else:
                sleep_time = (due_date - now).total_seconds()
                data_queue.appendleft(data)
                print(f"sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
        else:
            time.sleep(1)


if __name__ == '__main__':
    base_url = base_urls[sys.argv[1] if len(sys.argv) > 1 else 'borrow']
    print("Base URL:", base_url)
    try:
        authenticate()

        fetcher_thread = threading.Thread(target=data_provider, args=(data_queue,))
        processor_thread = threading.Thread(target=data_processor, args=(data_queue,))
        #
        #
        fetcher_thread.start()
        processor_thread.start()
        #
        #
        fetcher_thread.join()
        processor_thread.join()

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Stopping the process...")
        sys.exit()
