import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import datetime
import requests
import threading
from typing import Dict, List, Optional
import uuid
import webbrowser
import tempfile
import os

class ICEActivity:
    def __init__(self, activity_id: str = None):
        self.id = activity_id or str(uuid.uuid4())
        self.timestamp = datetime.datetime.now()
        self.activity_type = ""
        self.location = ""
        self.description = ""
        self.priority = "Medium"
        self.status = "Active"
        self.assigned_personnel = []
        self.resources_needed = []
        self.coordinates = {"lat": 0.0, "lng": 0.0}
        self.alert_radius = 1000  # meters
        
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "activity_type": self.activity_type,
            "location": self.location,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "assigned_personnel": self.assigned_personnel,
            "resources_needed": self.resources_needed,
            "coordinates": self.coordinates,
            "alert_radius": self.alert_radius
        }
    
    @classmethod
    def from_dict(cls, data):
        activity = cls(data["id"])
        activity.timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        activity.activity_type = data["activity_type"]
        activity.location = data["location"]
        activity.description = data["description"]
        activity.priority = data["priority"]
        activity.status = data["status"]
        activity.assigned_personnel = data["assigned_personnel"]
        activity.resources_needed = data["resources_needed"]
        activity.coordinates = data["coordinates"]
        activity.alert_radius = data.get("alert_radius", 1000)
        return activity

class WeatherAPI:
    """Mock weather API - replace with actual weather service"""
    
    @staticmethod
    def get_weather(location: str) -> Dict:
        # Simulated weather data - replace with actual API calls
        import random
        conditions = ["Clear", "Cloudy", "Rainy", "Stormy", "Snowy"]
        return {
            "location": location,
            "temperature": random.randint(-10, 35),
            "condition": random.choice(conditions),
            "wind_speed": random.randint(0, 50),
            "visibility": random.randint(1, 10)
        }

class LocationAPI:
    """Mock location API - replace with actual geocoding service"""
    
    @staticmethod
    def geocode(address: str) -> Dict:
        # Simulated geocoding - replace with actual API calls
        import random
        return {
            "lat": round(random.uniform(33.8, 34.2), 6),  # Fullerton, CA area
            "lng": round(random.uniform(-118.0, -117.5), 6),
            "formatted_address": address
        }

class MapGenerator:
    """Generates HTML maps with Google Maps integration"""
    
    @staticmethod
    def generate_map_html(activities: List[ICEActivity]) -> str:
        # Get center point (average of all coordinates)
        if activities:
            center_lat = sum(a.coordinates["lat"] for a in activities) / len(activities)
            center_lng = sum(a.coordinates["lng"] for a in activities) / len(activities)
        else:
            center_lat, center_lng = 33.8703, -117.9242  # Fullerton, CA default
        
        # Priority color mapping
        priority_colors = {
            "Low": "#4CAF50",      # Green
            "Medium": "#FF9800",   # Orange
            "High": "#F44336",     # Red
            "Critical": "#9C27B0"  # Purple
        }
        
        # Status icons
        status_icons = {
            "Active": "⚠️",
            "In Progress": "🚨",
            "Resolved": "✅",  
            "Closed": "⭕"
        }
        
        # Generate map without Google Maps API (using OpenStreetMap instead)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ICE Activity Map</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <style>
        body {{ 
            margin: 0; 
            padding: 0; 
            font-family: Arial, sans-serif; 
        }}
        #map {{ 
            height: 100vh; 
            width: 100%; 
        }}
        .info-panel {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 300px;
        }}
        .legend {{
            margin-top: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 0;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }}
        .alert-banner {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            background: #f44336;
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: bold;
            z-index: 1001;
            animation: blink 1s infinite;
        }}
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0.7; }}
        }}
        .stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }}
        .stat-item {{
            text-align: center;
            padding: 5px;
            background: #f5f5f5;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <!-- Alert Banner for Critical Activities -->
    {"<div class='alert-banner'>🚨 CRITICAL ICE ACTIVITIES DETECTED 🚨</div>" if any(a.priority == "Critical" and a.status in ["Active", "In Progress"] for a in activities) else ""}
    
    <div class="info-panel">
        <h3>🚨 ICE Activity Monitor</h3>
        <div class="stats">
            <div class="stat-item">
                <strong>{len([a for a in activities if a.status == "Active"])}</strong><br>
                <small>Active</small>
            </div>
            <div class="stat-item">
                <strong>{len([a for a in activities if a.priority == "Critical"])}</strong><br>
                <small>Critical</small>
            </div>
            <div class="stat-item">
                <strong>{len([a for a in activities if a.status == "In Progress"])}</strong><br>
                <small>In Progress</small>
            </div>
            <div class="stat-item">
                <strong>{len(activities)}</strong><br>
                <small>Total</small>
            </div>
        </div>
        
        <div class="legend">
            <h4>Priority Levels:</h4>
            <div class="legend-item">
                <div class="legend-color" style="background-color: {priority_colors['Critical']};"></div>
                <span>Critical - Immediate Response</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: {priority_colors['High']};"></div>
                <span>High - Urgent</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: {priority_colors['Medium']};"></div>
                <span>Medium - Monitor</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: {priority_colors['Low']};"></div>
                <span>Low - Routine</span>
            </div>
        </div>
        
        <div style="margin-top: 10px; font-size: 12px; color: #666;">
            Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>

    <div id="map"></div>
    
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // Initialize map with OpenStreetMap
        const map = L.map('map').setView([{center_lat}, {center_lng}], 12);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        // Activity data
        const activities = {json.dumps([a.to_dict() for a in activities])};
        const priorityColors = {json.dumps(priority_colors)};
        
        activities.forEach(activity => {{
            const lat = activity.coordinates.lat;
            const lng = activity.coordinates.lng;
            const color = priorityColors[activity.priority];
            
            // Create custom icon
            const customIcon = L.divIcon({{
                html: `<div style="background-color: ${{color}}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
                iconSize: [20, 20],
                className: 'custom-marker'
            }});
            
            // Create marker
            const marker = L.marker([lat, lng], {{icon: customIcon}}).addTo(map);
            
            // Popup content
            const popupContent = `
                <div style="max-width: 250px;">
                    <h3>${{activity.activity_type}}</h3>
                    <p><strong>Location:</strong> ${{activity.location}}</p>
                    <p><strong>Priority:</strong> <span style="color: ${{color}}; font-weight: bold;">${{activity.priority}}</span></p>
                    <p><strong>Status:</strong> ${{activity.status}}</p>
                    <p><strong>Time:</strong> ${{new Date(activity.timestamp).toLocaleString()}}</p>
                    <p><strong>Description:</strong> ${{activity.description}}</p>
                    ${{activity.assigned_personnel.length > 0 ? 
                      `<p><strong>Personnel:</strong> ${{activity.assigned_personnel.join(', ')}}</p>` : ''}}
                    ${{activity.resources_needed.length > 0 ? 
                      `<p><strong>Resources:</strong> ${{activity.resources_needed.join(', ')}}</p>` : ''}}
                </div>
            `;
            
            marker.bindPopup(popupContent);
            
            // Alert radius circle for critical activities
            if (activity.priority === 'Critical' || activity.priority === 'High') {{
                L.circle([lat, lng], {{
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.1,
                    radius: activity.alert_radius
                }}).addTo(map);
            }}
        }});
        
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            window.location.reload();
        }}, 30000);
    </script>
</body>
</html>
        """
        
        return html_content

class ICEActivityTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("ICE Activity Tracker with Map Integration")
        self.root.geometry("1400x900")
        
        self.activities: List[ICEActivity] = []
        self.weather_api = WeatherAPI()
        self.location_api = LocationAPI()
        self.map_generator = MapGenerator()
        
        self.setup_ui()
        self.load_activities()
        
        # Auto-refresh timer
        self.auto_refresh()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title with alert indicator
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="🚨 ICE Activity Tracker", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        self.alert_label = ttk.Label(title_frame, text="", 
                                    font=("Arial", 12, "bold"), foreground="red")
        self.alert_label.pack(side=tk.RIGHT)
        
        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Emergency Controls", padding="5")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Buttons
        ttk.Button(control_frame, text="🚨 Report New Emergency", 
                  command=self.add_activity).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="📍 View Map", 
                  command=self.show_map).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="🔄 Update Activity", 
                  command=self.update_activity).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="✅ Close Activity", 
                  command=self.close_activity).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="🌤️ Weather Update", 
                  command=self.get_weather_update).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="📊 Generate Report", 
                  command=self.export_data).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="🔄 Refresh All", 
                  command=self.refresh_display).pack(fill=tk.X, pady=2)
        
        # Alert System
        alert_frame = ttk.LabelFrame(control_frame, text="Alert System", padding="5")
        alert_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(alert_frame, text="Auto-refresh (30s)", 
                       variable=self.auto_refresh_var).pack()
        
        ttk.Button(alert_frame, text="🔊 Test Alert", 
                  command=self.test_alert).pack(fill=tk.X, pady=2)
        
        # Filters
        filter_frame = ttk.LabelFrame(control_frame, text="Filters", padding="5")
        filter_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(filter_frame, text="Status:").pack()
        self.status_filter = ttk.Combobox(filter_frame, 
                                         values=["All", "Active", "In Progress", "Resolved", "Closed"])
        self.status_filter.set("All")
        self.status_filter.pack(fill=tk.X, pady=2)
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_activities)
        
        ttk.Label(filter_frame, text="Priority:").pack()
        self.priority_filter = ttk.Combobox(filter_frame, 
                                           values=["All", "Low", "Medium", "High", "Critical"])
        self.priority_filter.set("All")
        self.priority_filter.pack(fill=tk.X, pady=2)
        self.priority_filter.bind('<<ComboboxSelected>>', self.filter_activities)
        
        # Quick Stats
        stats_frame = ttk.LabelFrame(control_frame, text="Quick Stats", padding="5")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=30)
        self.stats_text.pack(fill=tk.X)
        
        # Activity List
        list_frame = ttk.LabelFrame(main_frame, text="Emergency Activities", padding="5")
        list_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for activities with tags for colors
        columns = ("Priority", "Status", "Time", "Type", "Location", "Description")
        self.activity_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        for col in columns:
            self.activity_tree.heading(col, text=col)
            if col == "Priority":
                self.activity_tree.column(col, width=80)
            elif col == "Status":
                self.activity_tree.column(col, width=100)
            elif col == "Time":
                self.activity_tree.column(col, width=120)
            elif col == "Description":
                self.activity_tree.column(col, width=250)
            else:
                self.activity_tree.column(col, width=120)
        
        # Configure tags for priority colors
        self.activity_tree.tag_configure("critical", background="#ffebee", foreground="#c62828")
        self.activity_tree.tag_configure("high", background="#fff3e0", foreground="#ef6c00")
        self.activity_tree.tag_configure("medium", background="#f3e5f5", foreground="#7b1fa2")
        self.activity_tree.tag_configure("low", background="#e8f5e8", foreground="#2e7d32")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.activity_tree.xview)
        self.activity_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for treeview and scrollbars
        self.activity_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("ICE System Ready - Monitoring for emergencies...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Bind double-click to view details
        self.activity_tree.bind("<Double-1>", self.view_activity_details)
        
    def auto_refresh(self):
        """Auto-refresh the display every 30 seconds"""
        if self.auto_refresh_var.get():
            self.refresh_display()
            self.update_alerts()
        
        # Schedule next refresh
        self.root.after(30000, self.auto_refresh)
    
    def update_alerts(self):
        """Update alert indicators"""
        critical_active = [a for a in self.activities 
                          if a.priority == "Critical" and a.status in ["Active", "In Progress"]]
        
        if critical_active:
            self.alert_label.config(text=f"⚠️ {len(critical_active)} CRITICAL ALERTS")
            self.root.bell()  # System beep
        else:
            self.alert_label.config(text="")
    
    def test_alert(self):
        """Test the alert system"""
        messagebox.showwarning("🚨 ALERT TEST", 
                              "This is a test of the ICE Alert System.\n\n"
                              "In a real emergency, this would notify all relevant personnel.")
        self.root.bell()
    
    def show_map(self):
        """Generate and show the map with all activities"""
        try:
            html_content = self.map_generator.generate_map_html(self.activities)
            
            # Create temporary HTML file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            # Open in default browser
            webbrowser.open(f'file://{temp_file.name}')
            
            self.status_var.set("Map opened in browser - Shows real-time activity locations")
            
            # Clean up temp file after a delay
            self.root.after(60000, lambda: self.cleanup_temp_file(temp_file.name))
            
        except Exception as e:
            messagebox.showerror("Map Error", f"Failed to generate map: {str(e)}")
    
    def cleanup_temp_file(self, filename):
        """Clean up temporary map file"""
        try:
            if os.path.exists(filename):
                os.unlink(filename)
        except:
            pass  # Ignore cleanup errors
    
    def update_stats(self):
        """Update the statistics display"""
        total = len(self.activities)
        active = len([a for a in self.activities if a.status == "Active"])
        in_progress = len([a for a in self.activities if a.status == "In Progress"])
        critical = len([a for a in self.activities if a.priority == "Critical"])
        high = len([a for a in self.activities if a.priority == "High"])
        resolved = len([a for a in self.activities if a.status == "Resolved"])
        
        stats_text = f"""📊 ACTIVITY STATISTICS

🚨 Critical: {critical}
⚠️  High: {high}
🔴 Active: {active}
🔵 In Progress: {in_progress}
✅ Resolved: {resolved}
📋 Total: {total}

Last Update:
{datetime.datetime.now().strftime('%H:%M:%S')}
"""
        
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", stats_text)
    
    def add_activity(self):
        dialog = ActivityDialog(self.root, "🚨 Report New Emergency")
        if dialog.result:
            activity = ICEActivity()
            activity.activity_type = dialog.result["type"]
            activity.location = dialog.result["location"]
            activity.description = dialog.result["description"]
            activity.priority = dialog.result["priority"]
            activity.assigned_personnel = dialog.result["personnel"].split(",") if dialog.result["personnel"] else []
            activity.resources_needed = dialog.result["resources"].split(",") if dialog.result["resources"] else []
            
            # Get coordinates
            coords = self.location_api.geocode(activity.location)
            activity.coordinates = {"lat": coords["lat"], "lng": coords["lng"]}
            
            self.activities.append(activity)
            self.save_activities()
            self.refresh_display()
            
            # Show alert for critical activities
            if activity.priority == "Critical":
                messagebox.showwarning("🚨 CRITICAL EMERGENCY", 
                                     f"Critical emergency reported at {activity.location}\n\n"
                                     f"Type: {activity.activity_type}\n"
                                     f"Description: {activity.description}")
                self.root.bell()
            
            self.status_var.set(f"Emergency reported: {activity.activity_type} at {activity.location}")
    
    def update_activity(self):
        selected = self.activity_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an activity to update.")
            return
        
        # Get activity ID from the first column (hidden)
        item = self.activity_tree.item(selected[0])
        values = item["values"]
        
        # Find activity by matching details (since we don't store ID in visible columns)
        activity = None
        for a in self.activities:
            if (a.priority == values[0].split()[-1] and a.status == values[1].split()[-1] and 
                a.activity_type == values[3] and a.location == values[4]):
                activity = a
                break
        
        if activity:
            dialog = ActivityDialog(self.root, f"🔄 Update Emergency - {activity.activity_type}", activity)
            if dialog.result:
                activity.activity_type = dialog.result["type"]
                activity.location = dialog.result["location"]
                activity.description = dialog.result["description"]
                activity.priority = dialog.result["priority"]
                activity.status = dialog.result["status"]
                activity.assigned_personnel = dialog.result["personnel"].split(",") if dialog.result["personnel"] else []
                activity.resources_needed = dialog.result["resources"].split(",") if dialog.result["resources"] else []
                
                self.save_activities()
                self.refresh_display()
                self.status_var.set(f"Updated: {activity.activity_type}")
    
    def close_activity(self):
        selected = self.activity_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an activity to close.")
            return
        
        if messagebox.askyesno("Confirm Closure", "Are you sure you want to close this emergency activity?"):
            item = self.activity_tree.item(selected[0])
            values = item["values"]
            
            # Find and close activity
            for activity in self.activities:
                if (activity.priority == values[0].split()[-1] and activity.status == values[1].split()[-1] and 
                    activity.activity_type == values[3] and activity.location == values[4]):
                    activity.status = "Closed"
                    break
            
            self.save_activities()
            self.refresh_display()
            self.status_var.set("Emergency activity closed")
    
    def get_weather_update(self):
        selected = self.activity_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an activity for weather update.")
            return
        
        item = self.activity_tree.item(selected[0])
        values = item["values"]
        location = values[4]  # Location column
        
        def fetch_weather():
            try:
                weather = self.weather_api.get_weather(location)
                message = f"🌤️ Weather at {location}:\n\n"
                message += f"🌡️ Temperature: {weather['temperature']}°C\n"
                message += f"☁️ Condition: {weather['condition']}\n"
                message += f"💨 Wind Speed: {weather['wind_speed']} km/h\n"
                message += f"👁️ Visibility: {weather['visibility']} km\n\n"
                
                if weather['condition'] in ['Stormy', 'Snowy'] or weather['wind_speed'] > 30:
                    message += "⚠️ Weather conditions may affect emergency response!"
                
                self.root.after(0, lambda: messagebox.showinfo("Weather Update", message))
                self.root.after(0, lambda: self.status_var.set("Weather data retrieved"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Weather fetch failed: {str(e)}"))
        
        threading.Thread(target=fetch_weather, daemon=True).start()
        self.status_var.set("Fetching weather conditions...")
    
    def view_activity_details(self, event):
        selected = self.activity_tree.selection()
        if selected:
            item = self.activity_tree.item(selected[0])
            values = item["values"]
            
            # Find full activity details
            activity = None
            for a in self.activities:
                if (a.priority == values[0].split()[-1] and a.status == values[1].split()[-1] and 
                    a.activity_type == values[3] and a.location == values[4]):
                    activity = a
                    break
            
            if activity:
                # Priority emoji mapping
                priority_emoji = {
                    "Critical": "🚨",
                    "High": "⚠️",
                    "Medium": "🔵",
                    "Low": "🟢"
                }
                
                status_emoji = {
                    "Active": "🔴",
                    "In Progress": "🟡",
                    "Resolved": "✅",
                    "Closed": "⭕"
                }
                
                details = f"{priority_emoji.get(activity.priority, '📍')} EMERGENCY DETAILS\n{'='*60}\n\n"
                details += f"🆔 ID: {activity.id}\n"
                details += f"🏷️  Type: {activity.activity_type}\n"
                details += f"📍 Location: {activity.location}\n"
                details += f"🗺️  Coordinates: {activity.coordinates['lat']:.6f}, {activity.coordinates['lng']:.6f}\n"
                details += f"📝 Description: {activity.description}\n"
                details += f"⚡ Priority: {priority_emoji.get(activity.priority, '')} {activity.priority}\n"
                details += f"📊 Status: {status_emoji.get(activity.status, '')} {activity.status}\n"
                details += f"🕐 Created: {activity.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                details += f"👥 Personnel: {', '.join(activity.assigned_personnel) if activity.assigned_personnel else 'None assigned'}\n"
                details += f"🛠️  Resources: {', '.join(activity.resources_needed) if activity.resources_needed else 'None specified'}\n"
                details += f"📏 Alert Radius: {activity.alert_radius}m\n"
                
                # Add weather info if available
                try:
                    weather = self.weather_api.get_weather(activity.location)
                    details += f"\n🌤️ CURRENT WEATHER:\n"
                    details += f"🌡️ Temperature: {weather['temperature']}°C\n"
                    details += f"☁️ Condition: {weather['condition']}\n"
                    details += f"💨 Wind: {weather['wind_speed']} km/h\n"
                except:
                    details += f"\n🌤️ Weather data unavailable\n"
                
                messagebox.showinfo("Emergency Activity Details", details)
    
    def filter_activities(self, event=None):
        self.refresh_display()
    
    def refresh_display(self):
        # Clear existing items
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Apply filters
        status_filter = self.status_filter.get()
        priority_filter = self.priority_filter.get()
        
        filtered_activities = self.activities
        
        if status_filter != "All":
            filtered_activities = [a for a in filtered_activities if a.status == status_filter]
        
        if priority_filter != "All":
            filtered_activities = [a for a in filtered_activities if a.priority == priority_filter]
        
        # Sort by priority and timestamp
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        filtered_activities.sort(key=lambda x: (priority_order.get(x.priority, 4), x.timestamp), reverse=True)
        
        # Add filtered activities to tree with appropriate tags
        for activity in filtered_activities:
            # Priority and status emojis
            priority_emoji = {
                "Critical": "🚨",
                "High": "⚠️",
                "Medium": "🔵",
                "Low": "🟢"
            }
            
            status_emoji = {
                "Active": "🔴",
                "In Progress": "🟡",
                "Resolved": "✅",
                "Closed": "⭕"
            }
            
            values = (
                f"{priority_emoji.get(activity.priority, '')} {activity.priority}",
                f"{status_emoji.get(activity.status, '')} {activity.status}",
                activity.timestamp.strftime("%m/%d %H:%M"),
                activity.activity_type,
                activity.location,
                activity.description[:60] + "..." if len(activity.description) > 60 else activity.description
            )
            
            # Determine tag for coloring
            tag = activity.priority.lower()
            
            item = self.activity_tree.insert("", tk.END, values=values, tags=(tag,))
            
            # Make critical items blink (visually stand out)
            if activity.priority == "Critical" and activity.status == "Active":
                self.activity_tree.set(item, "Priority", f"🚨⚡ {activity.priority} ⚡🚨")
        
        # Update statistics
        self.update_stats()
        
        # Update status
        critical_count = len([a for a in filtered_activities if a.priority == "Critical" and a.status in ["Active", "In Progress"]])
        if critical_count > 0:
            self.status_var.set(f"⚠️ ALERT: {critical_count} CRITICAL emergencies active | Showing {len(filtered_activities)} of {len(self.activities)} activities")
        else:
            self.status_var.set(f"Monitoring {len(filtered_activities)} of {len(self.activities)} emergency activities")
    
    def save_activities(self):
        try:
            data = [activity.to_dict() for activity in self.activities]
            with open("ice_activities.json", "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save activities: {str(e)}")
    
    def load_activities(self):
        try:
            with open("ice_activities.json", "r") as f:
                data = json.load(f)
                self.activities = [ICEActivity.from_dict(item) for item in data]
            self.refresh_display()
        except FileNotFoundError:
            # Create some sample data for demonstration
            self.create_sample_data()
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load activities: {str(e)}")
    
    def create_sample_data(self):
        """Create sample emergency data for demonstration"""
        sample_activities = [
            {
                "type": "Medical Emergency",
                "location": "Fullerton College Campus",
                "description": "Student collapsed during sports practice, paramedics on scene",
                "priority": "High",
                "status": "In Progress",
                "personnel": ["EMT Team A", "Campus Security"],
                "resources": ["Ambulance", "AED"]
            },
            {
                "type": "Fire Emergency", 
                "location": "Downtown Fullerton",
                "description": "Kitchen fire reported at local restaurant",
                "priority": "Critical",
                "status": "Active",
                "personnel": ["Fire Station 1", "Fire Station 2"],
                "resources": ["Fire Truck", "Ladder Truck", "Water Tanker"]
            },
            {
                "type": "Traffic Accident",
                "location": "Harbor Blvd & Chapman Ave",
                "description": "Multi-vehicle collision blocking intersection",
                "priority": "Medium",
                "status": "Resolved",
                "personnel": ["Police Unit 12", "Tow Service"],
                "resources": ["Police Car", "Tow Truck"]
            }
        ]
        
        for sample in sample_activities:
            activity = ICEActivity()
            activity.activity_type = sample["type"]
            activity.location = sample["location"]
            activity.description = sample["description"]
            activity.priority = sample["priority"]
            activity.status = sample["status"]
            activity.assigned_personnel = sample["personnel"]
            activity.resources_needed = sample["resources"]
            
            # Get coordinates
            coords = self.location_api.geocode(activity.location)
            activity.coordinates = {"lat": coords["lat"], "lng": coords["lng"]}
            
            self.activities.append(activity)
        
        self.save_activities()
        self.refresh_display()
    
    def export_data(self):
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ice_emergency_report_{timestamp}.json"
            
            # Create comprehensive report
            report_data = {
                "report_generated": datetime.datetime.now().isoformat(),
                "total_activities": len(self.activities),
                "active_emergencies": len([a for a in self.activities if a.status == "Active"]),
                "critical_emergencies": len([a for a in self.activities if a.priority == "Critical"]),
                "summary": {
                    "by_priority": {
                        "Critical": len([a for a in self.activities if a.priority == "Critical"]),
                        "High": len([a for a in self.activities if a.priority == "High"]),
                        "Medium": len([a for a in self.activities if a.priority == "Medium"]),
                        "Low": len([a for a in self.activities if a.priority == "Low"])
                    },
                    "by_status": {
                        "Active": len([a for a in self.activities if a.status == "Active"]),
                        "In Progress": len([a for a in self.activities if a.status == "In Progress"]),
                        "Resolved": len([a for a in self.activities if a.status == "Resolved"]),
                        "Closed": len([a for a in self.activities if a.status == "Closed"])
                    }
                },
                "activities": [activity.to_dict() for activity in self.activities]
            }
            
            with open(filename, "w") as f:
                json.dump(report_data, f, indent=2)
            
            messagebox.showinfo("📊 Report Generated", 
                              f"Emergency report exported to {filename}\n\n"
                              f"Total Activities: {report_data['total_activities']}\n"
                              f"Active Emergencies: {report_data['active_emergencies']}\n"
                              f"Critical Emergencies: {report_data['critical_emergencies']}")
            
            self.status_var.set(f"Emergency report exported: {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

class ActivityDialog:
    def __init__(self, parent, title, activity=None):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets(activity)
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self, activity):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Emergency Type
        ttk.Label(main_frame, text="🚨 Emergency Type:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.type_var = tk.StringVar(value=activity.activity_type if activity else "")
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, width=50,
                                 values=["Medical Emergency", "Fire Emergency", "Natural Disaster", 
                                        "Security Incident", "Evacuation", "Search and Rescue",
                                        "Traffic Accident", "Hazmat Incident", "Power Outage",
                                        "Gas Leak", "Bomb Threat", "Active Shooter", "Other"])
        type_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Location
        ttk.Label(main_frame, text="📍 Location:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.location_var = tk.StringVar(value=activity.location if activity else "")
        location_entry = ttk.Entry(main_frame, textvariable=self.location_var, width=50)
        location_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="📝 Description:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.description_text = tk.Text(desc_frame, height=6, width=50)
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        
        if activity:
            self.description_text.insert("1.0", activity.description)
        
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Priority
        ttk.Label(main_frame, text="⚡ Priority Level:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.priority_var = tk.StringVar(value=activity.priority if activity else "Medium")
        priority_frame = ttk.Frame(main_frame)
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        
        priority_colors = {"Low": "🟢", "Medium": "🔵", "High": "⚠️", "Critical": "🚨"}
        for priority in ["Low", "Medium", "High", "Critical"]:
            ttk.Radiobutton(priority_frame, text=f"{priority_colors[priority]} {priority}", 
                           variable=self.priority_var, value=priority).pack(side=tk.LEFT, padx=(0, 20))
        
        # Status (only for updates)
        if activity:
            ttk.Label(main_frame, text="📊 Status:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            self.status_var = tk.StringVar(value=activity.status)
            status_frame = ttk.Frame(main_frame)
            status_frame.pack(fill=tk.X, pady=(0, 10))
            
            status_colors = {"Active": "🔴", "In Progress": "🟡", "Resolved": "✅", "Closed": "⭕"}
            for status in ["Active", "In Progress", "Resolved", "Closed"]:
                ttk.Radiobutton(status_frame, text=f"{status_colors[status]} {status}", 
                               variable=self.status_var, value=status).pack(side=tk.LEFT, padx=(0, 15))
        else:
            self.status_var = tk.StringVar(value="Active")
        
        # Personnel
        ttk.Label(main_frame, text="👥 Assigned Personnel (comma-separated):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.personnel_var = tk.StringVar(value=", ".join(activity.assigned_personnel) if activity else "")
        ttk.Entry(main_frame, textvariable=self.personnel_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Resources
        ttk.Label(main_frame, text="🛠️ Resources Needed (comma-separated):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.resources_var = tk.StringVar(value=", ".join(activity.resources_needed) if activity else "")
        ttk.Entry(main_frame, textvariable=self.resources_var, width=50).pack(fill=tk.X, pady=(0, 10))
        
        # Alert Radius
        ttk.Label(main_frame, text="📏 Alert Radius (meters):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.radius_var = tk.StringVar(value=str(activity.alert_radius) if activity else "1000")
        ttk.Entry(main_frame, textvariable=self.radius_var, width=20).pack(anchor=tk.W, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="💾 Save Emergency", command=self.save).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
    def save(self):
        if not self.type_var.get() or not self.location_var.get():
            messagebox.showerror("⚠️ Validation Error", "Emergency Type and Location are required!")
            return
        
        try:
            radius = int(self.radius_var.get())
            if radius < 100 or radius > 10000:
                raise ValueError("Alert radius must be between 100 and 10000 meters")
        except ValueError as e:
            messagebox.showerror("⚠️ Validation Error", f"Invalid alert radius: {str(e)}")
            return
        
        self.result = {
            "type": self.type_var.get(),
            "location": self.location_var.get(),
            "description": self.description_text.get("1.0", tk.END).strip(),
            "priority": self.priority_var.get(),
            "status": self.status_var.get(),
            "personnel": self.personnel_var.get().strip(),
            "resources": self.resources_var.get().strip(),
            "alert_radius": radius
        }
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

def main():
    root = tk.Tk()
    
    # Set application icon and styling
    root.configure(bg='white')
    
    # Create and configure the application
    app = ICEActivityTracker(root)
    
    # Show startup message
    messagebox.showinfo("🚨 ICE Activity Tracker", 
                       "ICE Emergency Activity Tracker is now running!\n\n"
                       "Features:\n"
                       "• Real-time emergency tracking\n"
                       "• Google Maps integration\n"
                       "• Priority-based alerts\n"
                       "• Weather monitoring\n"
                       "• Automatic notifications\n\n"
                       "Click 'View Map' to see emergency locations with color-coded markers!")
    
    root.mainloop()

if __name__ == "__main__":
    main()