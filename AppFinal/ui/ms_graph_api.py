import requests
from datetime import datetime, timedelta

def get_upcoming_ms_events(access_token, max_results=10):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Filtrer à partir de maintenant, tri par date de début
    now = datetime.utcnow().isoformat() + "Z"
    url = (
        "https://graph.microsoft.com/v1.0/me/events"
        f"?$select=subject,bodyPreview,onlineMeeting,attendees,start,end,webLink"
        f"&$orderby=start/dateTime"
        f"&$top={max_results}"
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Erreur récupération événements :", response.status_code, response.text)
        return []

    events = []
    for ev in response.json().get("value", []):
        # Convertir en format Google-like
        events.append({
            "summary": ev.get("subject", "No title"),
            "start": ev.get("start", {}).get("dateTime", ""),
            "description": ev.get("bodyPreview", ""),
            "attendees": [
                at.get("emailAddress", {}).get("address", "")
                for at in ev.get("attendees", [])
            ],
            "link": ev.get("webLink", ""),  # lien Outlook Web
            "onlineMeeting": ev.get("onlineMeeting", {})
        })
    return events

import requests
from datetime import datetime

def create_ms_event(access_token, title, description, start_dt, end_dt, participants):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

    attendees = [{"emailAddress": {"address": email}, "type": "required"} for email in participants]

    payload = {
        "subject": title,
        "body": {
            "contentType": "HTML",
            "content": description or ""
        },
        "start": {
            "dateTime": start_str,
            "timeZone": "Africa/Tunis"
        },
        "end": {
            "dateTime": end_str,
            "timeZone": "Africa/Tunis"
        },
        "attendees": attendees,
        "allowNewTimeProposals": True,
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness"
    }

    url = "https://graph.microsoft.com/v1.0/me/events"
    r = requests.post(url, headers=headers, json=payload)

    if r.status_code not in (200, 201):
        raise Exception(f"Erreur création événement: {r.status_code} - {r.text}")

    ev = r.json()

    # 🔹 Éviter le NoneType error
    online_meeting = ev.get("onlineMeeting") or {}
    join_url = online_meeting.get("joinUrl", "")

    return {
        "summary": ev.get("subject", title),
        "start": ev.get("start", {}).get("dateTime"),
        "link": ev.get("webLink", ""),
        "joinUrl": join_url
    }