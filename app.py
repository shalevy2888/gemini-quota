import rumps
import requests
import json
import os
import time
from datetime import datetime
import threading

class GeminiQuotaApp(rumps.App):
    def __init__(self):
        super(GeminiQuotaApp, self).__init__("Gemini Quota")
        self.creds_path = os.path.expanduser("~/.gemini/oauth_creds.json")
        self.stats = []
        self.monitored_groups = {"Pro": True, "Flash": True, "Flash-Lite": True}
        self.default_project = "shaylevy"
        self.client_id = "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
        
        # Initial Title
        self.title = "⌛ Loading..."
        
        # Build Menu structure
        self.full_stats_menu = rumps.MenuItem("Full Stats")
        self.settings_menu = rumps.MenuItem("Settings")
        
        self.menu = [
            self.full_stats_menu,
            None,
            self.settings_menu,
            rumps.MenuItem("Refresh Now", callback=self.refresh_now),
        ]
        
        # Add settings toggles
        self.pro_toggle = rumps.MenuItem("Monitor Pro", callback=self.toggle_group)
        self.pro_toggle.state = True
        self.flash_toggle = rumps.MenuItem("Monitor Flash", callback=self.toggle_group)
        self.flash_toggle.state = True
        self.flash_lite_toggle = rumps.MenuItem("Monitor Flash-Lite", callback=self.toggle_group)
        self.flash_lite_toggle.state = True
        
        self.settings_menu.add(self.pro_toggle)
        self.settings_menu.add(self.flash_toggle)
        self.settings_menu.add(self.flash_lite_toggle)
        
        # Start the first update after a short delay to avoid initialization races
        threading.Timer(1.0, self.update_stats).start()

    def toggle_group(self, sender):
        sender.state = not sender.state
        group_name = sender.title.split(" ")[-1]
        self.monitored_groups[group_name] = sender.state
        self.update_display()

    def get_access_token(self):
        try:
            if not os.path.exists(self.creds_path):
                print(f"Credentials file not found at {self.creds_path}")
                return None
                
            with open(self.creds_path, 'r') as f:
                creds = json.load(f)
            
            access_token = creds.get("access_token")
            expiry_date = creds.get("expiry_date", 0)
            refresh_token = creds.get("refresh_token")
            
            now_ms = time.time() * 1000
            if access_token and now_ms < (expiry_date - 60000):
                return access_token
            
            if refresh_token:
                print("Refreshing Access Token...")
                refresh_url = "https://oauth2.googleapis.com/token"
                data = {
                    "client_id": self.client_id,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
                response = requests.post(refresh_url, data=data, timeout=10)
                if response.status_code == 200:
                    new_creds = response.json()
                    access_token = new_creds.get("access_token")
                    creds["access_token"] = access_token
                    creds["expiry_date"] = (time.time() + new_creds.get("expires_in", 3600)) * 1000
                    with open(self.creds_path, 'w') as f:
                        json.dump(creds, f, indent=2)
                    print("Token refreshed successfully.")
                    return access_token
                else:
                    print(f"Failed to refresh token: {response.status_code} {response.text}")
            
            return access_token
        except Exception as e:
            print(f"Error in get_access_token: {e}")
            return None

    @rumps.timer(300)
    def periodic_update(self, _):
        self.update_stats()

    def refresh_now(self, _):
        self.update_stats()

    def update_stats(self):
        token = self.get_access_token()
        if not token:
            self.title = "⚠️ No Auth"
            return

        url = "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json={"project": self.default_project}, timeout=10)
            if response.status_code == 200:
                self.stats = response.json().get("buckets", [])
                self.update_display()
                self.update_menu()
            else:
                self.title = f"⚠️ {response.status_code}"
                print(f"API Error {response.status_code}: {response.text}")
                if response.status_code == 401:
                    self.title = "⚠️ Relogin"
        except Exception as e:
            self.title = "⚠️ Error"
            print(f"Exception during update: {e}")

    def update_display(self):
        if not self.stats:
            return

        worst_usage = -1
        worst_reset = ""
        
        for bucket in self.stats:
            model_id = bucket.get("modelId", "").lower()
            usage = 100 * (1 - bucket.get("remainingFraction", 1))
            reset_time = bucket.get("resetTime", "")
            
            group = None
            if "pro" in model_id: group = "Pro"
            elif "flash-lite" in model_id: group = "Flash-Lite"
            elif "flash" in model_id: group = "Flash"
            
            if group and self.monitored_groups.get(group):
                if usage > worst_usage:
                    worst_usage = usage
                    worst_reset = reset_time

        if worst_usage == -1:
            self.title = "Gemini"
            return

        try:
            dt = datetime.strptime(worst_reset, "%Y-%m-%dT%H:%M:%SZ")
            reset_str = dt.strftime("%H:%M")
        except:
            reset_str = "--:--"

        indicator = "🟢"
        if worst_usage >= 90: indicator = "🔴"
        elif worst_usage >= 80: indicator = "🟠"
        elif worst_usage >= 60: indicator = "🟡"

        self.title = f"{indicator} {int(worst_usage)}% | {reset_str}"

    def update_menu(self):
        try:
            # Safely clear the menu
            self.full_stats_menu.clear()
        except Exception as e:
            # This happens in rumps if the menu is already empty
            print(f"Menu clear notice: {e}")

        for bucket in self.stats:
            model_id = bucket.get("modelId", "")
            usage = int(100 * (1 - bucket.get("remainingFraction", 1)))
            dt_str = bucket.get("resetTime", "")
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
                reset_str = dt.strftime("%H:%M")
            except:
                reset_str = "??:??"
            
            label = f"{model_id:25} | {usage:3}% | Reset: {reset_str}"
            self.full_stats_menu.add(rumps.MenuItem(label))

if __name__ == "__main__":
    app = GeminiQuotaApp()
    app.run()
