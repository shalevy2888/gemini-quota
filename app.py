import rumps
import requests
import json
import os
import time
from datetime import datetime, timezone
import threading
import subprocess

class GeminiQuotaApp(rumps.App):
    def __init__(self):
        super(GeminiQuotaApp, self).__init__("Gemini Quota")
        self.creds_path = os.path.expanduser("~/.gemini/oauth_creds.json")
        self.config_path = os.path.expanduser("~/.gemini/quota_app_config.json")
        
        self.stats = []
        self.monitored_groups = {"Pro": True, "Flash": True, "Flash-Lite": True}
        self.display_mode = "icon_per_reset" # options: icon, icon_per, icon_per_reset
        self.default_project = "shaylevy"
        self.client_id = "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
        self.last_update_time = 0
        
        self.load_settings()
        
        # Initial Title
        self.title = "⌛ Loading..."
        
        # Build Menu structure
        self.last_update_item = rumps.MenuItem("Last Update: Never")
        self.usage_overview_item = rumps.MenuItem("Usage: --")
        self.reset_overview_item = rumps.MenuItem("Reset: --")
        self.full_stats_menu = rumps.MenuItem("Full Stats")
        self.settings_menu = rumps.MenuItem("Settings")
        
        self.menu = [
            self.last_update_item,
            self.usage_overview_item,
            self.reset_overview_item,
            None,
            self.full_stats_menu,
            None,
            self.settings_menu,
            rumps.MenuItem("Login / Refresh Auth", callback=self.relogin),
            rumps.MenuItem("Refresh Now", callback=self.refresh_now),
        ]
        
        # Build Settings Submenu
        # 1. Monitored Groups
        self.settings_menu.add(rumps.MenuItem("Monitor Groups:"))
        self.pro_toggle = rumps.MenuItem("Monitor Pro", callback=self.toggle_group)
        self.pro_toggle.state = self.monitored_groups.get("Pro", True)
        self.flash_toggle = rumps.MenuItem("Monitor Flash", callback=self.toggle_group)
        self.flash_toggle.state = self.monitored_groups.get("Flash", True)
        self.flash_lite_toggle = rumps.MenuItem("Monitor Flash-Lite", callback=self.toggle_group)
        self.flash_lite_toggle.state = self.monitored_groups.get("Flash-Lite", True)
        self.settings_menu.add(self.pro_toggle)
        self.settings_menu.add(self.flash_toggle)
        self.settings_menu.add(self.flash_lite_toggle)
        
        self.settings_menu.add(None) # Separator
        
        # 2. Display Mode
        self.settings_menu.add(rumps.MenuItem("Display Mode:"))
        self.mode_icon = rumps.MenuItem("Icon Only", callback=self.set_display_mode)
        self.mode_icon_per = rumps.MenuItem("Icon & Percentage", callback=self.set_display_mode)
        self.mode_icon_per_reset = rumps.MenuItem("Icon, Percentage & Reset", callback=self.set_display_mode)
        
        self.settings_menu.add(self.mode_icon)
        self.settings_menu.add(self.mode_icon_per)
        self.settings_menu.add(self.mode_icon_per_reset)
        self.update_mode_checks()
        
        # Timer for updating the "seconds ago" display
        self.ui_timer = rumps.Timer(self.update_ui_counters, 1)
        self.ui_timer.start()
        
        # Start the first update
        threading.Timer(1.0, self.update_stats).start()

    def load_settings(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    cfg = json.load(f)
                    self.monitored_groups = cfg.get("monitored_groups", self.monitored_groups)
                    self.display_mode = cfg.get("display_mode", self.display_mode)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump({
                    "monitored_groups": self.monitored_groups,
                    "display_mode": self.display_mode
                }, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def update_mode_checks(self):
        self.mode_icon.state = (self.display_mode == "icon")
        self.mode_icon_per.state = (self.display_mode == "icon_per")
        self.mode_icon_per_reset.state = (self.display_mode == "icon_per_reset")

    def set_display_mode(self, sender):
        if sender.title == "Icon Only": self.display_mode = "icon"
        elif sender.title == "Icon & Percentage": self.display_mode = "icon_per"
        else: self.display_mode = "icon_per_reset"
        self.update_mode_checks()
        self.save_settings()
        self.update_display()

    def toggle_group(self, sender):
        sender.state = not sender.state
        group_name = sender.title.split(" ")[-1]
        self.monitored_groups[group_name] = sender.state
        self.save_settings()
        self.update_display()

    def relogin(self, _):
        script = 'tell application "Terminal" to do script "gemini login; exit"'
        subprocess.run(["osascript", "-e", "tell application \"Terminal\" to activate", "-e", script])
        rumps.notification("Gemini Quota", "Login Required", "Please complete the login flow in the opened terminal.")

    def get_access_token(self):
        try:
            if not os.path.exists(self.creds_path): return None
            with open(self.creds_path, 'r') as f:
                creds = json.load(f)
            
            access_token = creds.get("access_token")
            expiry_date = creds.get("expiry_date", 0)
            refresh_token = creds.get("refresh_token")
            
            now_ms = time.time() * 1000
            if access_token and now_ms < (expiry_date - 60000):
                return access_token
            
            if refresh_token:
                refresh_url = "https://oauth2.googleapis.com/token"
                data = {"client_id": self.client_id, "refresh_token": refresh_token, "grant_type": "refresh_token"}
                response = requests.post(refresh_url, data=data, timeout=10)
                if response.status_code == 200:
                    new_creds = response.json()
                    access_token = new_creds.get("access_token")
                    creds["access_token"] = access_token
                    creds["expiry_date"] = (time.time() + new_creds.get("expires_in", 3600)) * 1000
                    with open(self.creds_path, 'w') as f:
                        json.dump(creds, f, indent=2)
                    return access_token
            return access_token
        except Exception: return None

    @rumps.timer(300)
    def periodic_update(self, _):
        self.update_stats()

    def refresh_now(self, _):
        self.update_stats()

    def update_ui_counters(self, _):
        if self.last_update_time > 0:
            diff = int(time.time() - self.last_update_time)
            self.last_update_item.title = f"Last Update: {diff}s ago"

    def update_stats(self):
        token = self.get_access_token()
        if not token:
            self.title = "⚠️ Relogin"
            return

        url = "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, json={"project": self.default_project}, timeout=10)
            if response.status_code == 200:
                self.stats = response.json().get("buckets", [])
                self.last_update_time = time.time()
                self.update_display()
                self.update_menu()
            else:
                self.title = "⚠️ Relogin" if response.status_code == 401 else f"⚠️ {response.status_code}"
        except Exception:
            self.title = "⚠️ Error"

    def get_time_diff_str(self, target_iso):
        try:
            target_dt = datetime.strptime(target_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            now_dt = datetime.now(timezone.utc)
            diff = target_dt - now_dt
            seconds = int(diff.total_seconds())
            if seconds <= 0: return "now"
            hours, rem = divmod(seconds, 3600)
            minutes, _ = divmod(rem, 60)
            return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        except: return "--"

    def update_display(self):
        if not self.stats: return

        groups_found = {}
        worst_usage = -1
        
        for bucket in self.stats:
            model_id = bucket.get("modelId", "").lower()
            usage = 100 * (1 - bucket.get("remainingFraction", 1))
            reset_time = bucket.get("resetTime", "")
            group = "Pro" if "pro" in model_id else "Flash-Lite" if "flash-lite" in model_id else "Flash" if "flash" in model_id else None
            
            if group:
                if group not in groups_found or usage > groups_found[group]['usage']:
                    groups_found[group] = {'usage': usage, 'reset': reset_time}

        usage_parts = []
        reset_parts = []
        for g in ["Pro", "Flash"]:
            if g in groups_found:
                u = int(groups_found[g]['usage'])
                r = self.get_time_diff_str(groups_found[g]['reset'])
                usage_parts.append(f"{g}: {u}%")
                reset_parts.append(f"{g} in {r}")
                if self.monitored_groups.get(g) and u > worst_usage:
                    worst_usage = u

        self.usage_overview_item.title = " | ".join(usage_parts) if usage_parts else "Usage: --"
        self.reset_overview_item.title = "Resets: " + ", ".join(reset_parts) if reset_parts else "Resets: --"

        # Unique Gemini Icons: Gemini Symbol + Color Circle
        icon_prefix = "♊️" 
        indicator = "🟢"
        if worst_usage >= 90: indicator = "🔴"
        elif worst_usage >= 80: indicator = "🟠"
        elif worst_usage >= 60: indicator = "🟡"
        elif worst_usage == -1: indicator = "⚪️"

        full_icon = f"{icon_prefix}{indicator}"

        if self.display_mode == "icon":
            self.title = full_icon
        else:
            usage_str = f"{int(worst_usage) if worst_usage != -1 else 0}%"
            if self.display_mode == "icon_per":
                self.title = f"{full_icon} {usage_str}"
            else:
                worst_reset_str = "--:--"
                for g, data in groups_found.items():
                    if self.monitored_groups.get(g) and int(data['usage']) == worst_usage:
                        try:
                            dt = datetime.strptime(data['reset'], "%Y-%m-%dT%H:%M:%SZ")
                            worst_reset_str = dt.strftime("%H:%M")
                        except: pass
                        break
                self.title = f"{full_icon} {usage_str} | {worst_reset_str}"

    def update_menu(self):
        try: self.full_stats_menu.clear()
        except: pass
        for bucket in self.stats:
            model_id = bucket.get("modelId", "")
            usage = int(100 * (1 - bucket.get("remainingFraction", 1)))
            dt_str = bucket.get("resetTime", "")
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
                reset_str = dt.strftime("%H:%M")
            except: reset_str = "??:??"
            self.full_stats_menu.add(rumps.MenuItem(f"{model_id:25} | {usage:3}% | Reset: {reset_str}"))

if __name__ == "__main__":
    GeminiQuotaApp().run()
