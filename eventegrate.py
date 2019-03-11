from __future__ import print_function
import datetime
import pickle
import os.path
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def build_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def iterate_calendars(service, email):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(minAccessRole='owner', pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            print("Calendar:", calendar_list_entry['summary'])
            share_calendar(service, calendar_list_entry['id'], email)
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

def share_calendar(service, id, email):
    print('Checking current acls for %s:' % id)
    acls = service.acl().list(calendarId=id).execute()
    exists = any(filter(lambda r: r['id'] == 'user:' + email, acls['items']))
    if exists:
        print("User already has access!")
        return
    else:
        print("Sharing to user: ")

    new_rule = {
        'scope': {
            'type': 'user',
            'value': email,
        },
        'role': 'writer'
    }

    created_rule = service.acl().insert(calendarId=id, body=new_rule).execute()
    print("Created rule:", created_rule['id'])

def main():
    """Experimental tool to see if we can automatically share calendars.
    """
    service = build_creds()

    # Call the Calendar API
    email_to_share_to = 'dfitch@wisc.edu'
    iterate_calendars(service, email_to_share_to)


if __name__ == '__main__':
    main()
