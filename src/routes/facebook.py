from flask import Blueprint, request, jsonify
import subprocess
import json
import sys
import os

facebook_bp = Blueprint("facebook", __name__)

@facebook_bp.route("/scrape", methods=["POST"])
def scrape_facebook_event():
    try:
        data = request.get_json()
        facebook_url = data.get("url")
        
        if not facebook_url:
            return jsonify({"error": "Facebook URL is required"}), 400
        
        # Run the scraper script
        result = subprocess.run(
            ["/home/ubuntu/facebook-luma-ui/venv/bin/python", "/home/ubuntu/scraper.py", facebook_url],
            capture_output=True,
            text=True,
            timeout=180 # Increased timeout for Selenium and page scraping
        )
        
        if result.returncode != 0:
            return jsonify({"error": f"Scraper failed: {result.stderr}"}), 500
        
        try:
            event_data = json.loads(result.stdout)
            return jsonify(event_data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON response from scraper"}), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Scraper timed out"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@facebook_bp.route("/import", methods=["POST"])
def import_to_luma():
    try:
        data = request.get_json()
        
        # Extract event data and configuration
        event_data = data.get("event_data")
        luma_api_key = data.get("luma_api_key")
        luma_calendar_id = data.get("luma_calendar_id")
        hosts = data.get("hosts", [])
        
        if not all([event_data, luma_api_key, luma_calendar_id]):
            return jsonify({"error": "Missing required data"}), 400
        
        # Import the importer module and create the event
        sys.path.append("/home/ubuntu")
        from importer import create_luma_event
        
        result = create_luma_event(event_data, luma_api_key, luma_calendar_id, hosts)
        
        if result:
            return jsonify({"success": True, "event": result})
        else:
            return jsonify({"error": "Failed to create event on Lu.ma"}), 500
            
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@facebook_bp.route("/calendar_info", methods=["POST"])
def get_calendar_info():
    try:
        data = request.get_json()
        luma_api_key = data.get("luma_api_key")
        luma_calendar_id = data.get("luma_calendar_id")
        
        if not all([luma_api_key, luma_calendar_id]):
            return jsonify({"error": "Missing API key or calendar ID"}), 400
        
        # Make a request to Lu.ma API to get calendar information
        import requests
        headers = {
            "Authorization": f"Bearer {luma_api_key}",
            "Content-Type": "application/json"
        }
        
        # Try to get calendar info (this endpoint might not exist, so we'll handle gracefully)
        try:
            response = requests.get(f"https://lu.ma/api/public/v1/calendar/{luma_calendar_id}", headers=headers)
            if response.status_code == 200:
                calendar_data = response.json()
                return jsonify({
                    "calendar_id": luma_calendar_id,
                    "calendar_name": calendar_data.get("name", "Unknown Calendar"),
                    "calendar_url": calendar_data.get("url", f"https://lu.ma/calendar/{luma_calendar_id}")
                })
            else:
                # Fallback if calendar info endpoint doesn't exist
                return jsonify({
                    "calendar_id": luma_calendar_id,
                    "calendar_name": "Calendar",
                    "calendar_url": f"https://lu.ma/calendar/{luma_calendar_id}"
                })
        except requests.exceptions.RequestException:
            # Fallback if request fails
            return jsonify({
                "calendar_id": luma_calendar_id,
                "calendar_name": "Calendar",
                "calendar_url": f"https://lu.ma/calendar/{luma_calendar_id}"
            })
            
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



