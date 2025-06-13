import requests
import json
import sys
import os
import mimetypes

def create_luma_event(event_data, luma_api_key, luma_calendar_id, hosts):
    headers = {
        "Authorization": f"Bearer {luma_api_key}",
        "Content-Type": "application/json"
    }

    # Prepare description with ticket link prepended
    description = event_data.get("description", "")
    ticket_link = event_data.get("ticket_link", "")
    if ticket_link and ticket_link != "":
        description = f"Register/Tickets: {ticket_link}\n\n" + description

    # Prepare hosts data
    luma_hosts = []
    for host in hosts:
        luma_hosts.append({
            "name": host.get("name"),
            "email": host.get("email"),
            "bio": host.get("bio", "")
        })

    # Prepare event data for Lu.ma API
    payload = {
        "calendar_id": luma_calendar_id,
        "name": event_data.get("title", "Facebook Event"),
        "description": description,
        "start_at": event_data.get("start_time"),
        "end_at": event_data.get("end_time"),
        "url": event_data.get("url"),
        "webinar_link": ticket_link,  # Map ticket link to webinar_link
        "timezone": event_data.get("timezone", "UTC"),
        "hosts": luma_hosts
    }

    # Add location if available
    if event_data.get("location") and event_data["location"] != "No location found":
        payload["geo_address_json"] = {
            "name": event_data["location"],
            "address": event_data.get("address", event_data["location"])
        }

    # Send request to create event
    try:
        response = requests.post("https://lu.ma/api/public/v1/event/create", headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        event_response = response.json()
        print(f"Event created successfully: {event_response.get("url")}")

        # Upload image if available
        image_path = event_data.get("image_path")
        if image_path and os.path.exists(image_path):
            event_id = event_response.get("id")
            if event_id:
                upload_image_to_luma(event_id, image_path, luma_api_key)
            else:
                print("Warning: Event ID not found in response, cannot upload image.", file=sys.stderr)
        
        return event_response

    except requests.exceptions.RequestException as e:
        print(f"Error creating event: {e}", file=sys.stderr)
        if response is not None:
            print(f"Response content: {response.text}", file=sys.stderr)
        return None

def upload_image_to_luma(event_id, image_path, luma_api_key):
    headers = {
        "Authorization": f"Bearer {luma_api_key}"
    }
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream" # Default if type cannot be guessed

    with open(image_path, "rb") as f:
        files = {"image": (os.path.basename(image_path), f, mime_type)}
        try:
            response = requests.post(f"https://lu.ma/api/public/v1/event/{event_id}/upload_image", headers=headers, files=files)
            response.raise_for_status()
            print(f"Image uploaded successfully for event {event_id}")
        except requests.exceptions.RequestException as e:
            print(f"Error uploading image for event {event_id}: {e}", file=sys.stderr)
            if response is not None:
                print(f"Response content: {response.text}", file=sys.stderr)

if __name__ == "__main__":
    # This part is for testing the importer directly
    # In the actual app, it will be called from the Flask route
    pass

