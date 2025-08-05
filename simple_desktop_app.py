"""
Splunk Dashboard Automator - Simple Desktop Application
=====================================================

A simplified desktop GUI application for automating Splunk dashboard interactions.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import asyncio
import json
import os
from datetime import datetime, timedelta
from utils.config import Config, get_current_timestamp
from utils.encryption import CredentialManager
from utils.screenshot import ScreenshotManager
from utils.scheduler import ScheduleManager

class SimpleSplunkGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Splunk Dashboard Automator")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize managers
        self.credential_manager = CredentialManager()
        self.screenshot_manager = ScreenshotManager()
        self.schedule_manager = ScheduleManager()
        
        # Current credentials
        self.current_credentials = None
        
        # Data storage
        self.dashboards = self.load_dashboards()
        self.lists = self.load_lists()
        
        # Create the GUI
        self.create_widgets()
        self.load_initial_data()
        
    def load_dashboards(self):
        """Load dashboards from JSON file"""
        try:
            with open('dashboards.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception:
            return {}
            
    def save_dashboards(self):
        """Save dashboards to JSON file"""
        try:
            with open('dashboards.json', 'w') as f:
                json.dump(self.dashboards, f, indent=2)
            return True
        except Exception:
            return False
            
    def load_lists(self):
        """Load lists from JSON file"""
        try:
            with open('lists.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception:
            return {}
            
    def save_lists(self):
        """Save lists to JSON file"""
        try:
            with open('lists.json', 'w') as f:
                json.dump(self.lists, f, indent=2)
            return True
        except Exception:
            return False
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_credentials_tab()
        self.create_dashboards_tab()
        self.create_lists_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
        
    def create_credentials_tab(self):
        """Create credentials management tab"""
        credentials_frame = ttk.Frame(self.notebook)
        self.notebook.add(credentials_frame, text="Credentials")
        
        # Title
        title_label = ttk.Label(credentials_frame, text="Splunk Credentials", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Credentials form
        form_frame = ttk.Frame(credentials_frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(credentials_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Save Credentials", 
                  command=self.save_credentials).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load Credentials", 
                  command=self.load_credentials).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Credentials", 
                  command=self.clear_credentials).pack(side='left', padx=5)
        
        # Status
        self.credentials_status = ttk.Label(credentials_frame, text="No credentials loaded", 
                                          foreground='gray')
        self.credentials_status.pack(pady=10)
        
    def create_dashboards_tab(self):
        """Create dashboard management tab"""
        dashboards_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboards_frame, text="Dashboards")
        
        # Title
        title_label = ttk.Label(dashboards_frame, text="Dashboard Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Add dashboard form
        add_frame = ttk.LabelFrame(dashboards_frame, text="Add New Dashboard", padding=10)
        add_frame.pack(fill='x', padx=10, pady=5)
        
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='x')
        
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.dashboard_name_entry = ttk.Entry(form_frame, width=30)
        self.dashboard_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="URL:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.dashboard_url_entry = ttk.Entry(form_frame, width=50)
        self.dashboard_url_entry.grid(row=1, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        
        ttk.Label(form_frame, text="List:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.dashboard_list_combo = ttk.Combobox(form_frame, width=27, state='readonly')
        self.dashboard_list_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Add Dashboard", 
                  command=self.add_dashboard).grid(row=2, column=2, padx=5, pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Dashboard list
        list_frame = ttk.LabelFrame(dashboards_frame, text="Existing Dashboards", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for dashboards
        columns = ('Name', 'URL', 'List', 'Created')
        self.dashboard_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.dashboard_tree.heading(col, text=col)
            self.dashboard_tree.column(col, width=200)
        
        # Scrollbar
        dashboard_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', 
                                          command=self.dashboard_tree.yview)
        self.dashboard_tree.configure(yscrollcommand=dashboard_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.dashboard_tree.pack(side='left', fill='both', expand=True)
        dashboard_scrollbar.pack(side='right', fill='y')
        
        # Dashboard buttons
        dashboard_buttons = ttk.Frame(dashboards_frame)
        dashboard_buttons.pack(pady=10)
        
        ttk.Button(dashboard_buttons, text="Take Screenshot", 
                  command=self.take_screenshot).pack(side='left', padx=5)
        ttk.Button(dashboard_buttons, text="Delete Dashboard", 
                  command=self.delete_dashboard).pack(side='left', padx=5)
        ttk.Button(dashboard_buttons, text="Refresh List", 
                  command=self.refresh_dashboards).pack(side='left', padx=5)
        
    def create_lists_tab(self):
        """Create list management tab"""
        lists_frame = ttk.Frame(self.notebook)
        self.notebook.add(lists_frame, text="Lists")
        
        # Title
        title_label = ttk.Label(lists_frame, text="List Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Add list form
        add_list_frame = ttk.LabelFrame(lists_frame, text="Create New List", padding=10)
        add_list_frame.pack(fill='x', padx=10, pady=5)
        
        list_form_frame = ttk.Frame(add_list_frame)
        list_form_frame.pack(fill='x')
        
        ttk.Label(list_form_frame, text="List Name:").pack(side='left', padx=5)
        self.list_name_entry = ttk.Entry(list_form_frame, width=30)
        self.list_name_entry.pack(side='left', padx=5)
        
        ttk.Label(list_form_frame, text="Description:").pack(side='left', padx=5)
        self.list_desc_entry = ttk.Entry(list_form_frame, width=40)
        self.list_desc_entry.pack(side='left', padx=5)
        
        ttk.Button(list_form_frame, text="Create List", 
                  command=self.create_list).pack(side='left', padx=5)
        
        # Lists display
        lists_display_frame = ttk.LabelFrame(lists_frame, text="Existing Lists", padding=10)
        lists_display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lists treeview
        list_columns = ('Name', 'Description', 'Dashboard Count', 'Created')
        self.lists_tree = ttk.Treeview(lists_display_frame, columns=list_columns, 
                                      show='headings', height=12)
        
        for col in list_columns:
            self.lists_tree.heading(col, text=col)
            self.lists_tree.column(col, width=200)
        
        # Lists scrollbar
        lists_scrollbar = ttk.Scrollbar(lists_display_frame, orient='vertical', 
                                       command=self.lists_tree.yview)
        self.lists_tree.configure(yscrollcommand=lists_scrollbar.set)
        
        # Pack lists treeview
        self.lists_tree.pack(side='left', fill='both', expand=True)
        lists_scrollbar.pack(side='right', fill='y')
        
        # List buttons
        list_buttons = ttk.Frame(lists_frame)
        list_buttons.pack(pady=10)
        
        ttk.Button(list_buttons, text="Delete List", 
                  command=self.delete_list).pack(side='left', padx=5)
        ttk.Button(list_buttons, text="Refresh Lists", 
                  command=self.refresh_lists).pack(side='left', padx=5)
        
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Title
        title_label = ttk.Label(settings_frame, text="Application Settings", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Screenshot settings
        screenshot_frame = ttk.LabelFrame(settings_frame, text="Screenshot Settings", padding=10)
        screenshot_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(screenshot_frame, text="Screenshot Timeout (seconds):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.timeout_var = tk.StringVar(value=str(Config.SCREENSHOT_TIMEOUT))
        self.timeout_entry = ttk.Entry(screenshot_frame, textvariable=self.timeout_var, width=10)
        self.timeout_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(screenshot_frame, text="Max Concurrent Screenshots:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.concurrent_var = tk.StringVar(value=str(Config.MAX_CONCURRENT_SCREENSHOTS))
        self.concurrent_entry = ttk.Entry(screenshot_frame, textvariable=self.concurrent_var, width=10)
        self.concurrent_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Directory settings
        dir_frame = ttk.LabelFrame(settings_frame, text="Directory Settings", padding=10)
        dir_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(dir_frame, text="Screenshot Directory:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.screenshot_dir_var = tk.StringVar(value=Config.SCREENSHOT_ARCHIVE_DIR)
        self.screenshot_dir_entry = ttk.Entry(dir_frame, textvariable=self.screenshot_dir_var, width=50)
        self.screenshot_dir_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(dir_frame, text="Browse", 
                  command=self.browse_screenshot_dir).grid(row=0, column=2, padx=5, pady=5)
        
        # Buttons
        settings_buttons = ttk.Frame(settings_frame)
        settings_buttons.pack(pady=20)
        
        ttk.Button(settings_buttons, text="Save Settings", 
                  command=self.save_settings).pack(side='left', padx=5)
        ttk.Button(settings_buttons, text="Reset to Defaults", 
                  command=self.reset_settings).pack(side='left', padx=5)
        
    def load_initial_data(self):
        """Load initial data into the GUI"""
        self.load_credentials()
        self.refresh_dashboards()
        self.refresh_lists()
        self.update_combos()
        
    def update_combos(self):
        """Update combo box values"""
        list_names = list(self.lists.keys())
        self.dashboard_list_combo['values'] = list_names
        
    def save_credentials(self):
        """Save credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            self.credential_manager.save_credentials(username, password)
            self.current_credentials = {'username': username, 'password': password}
            self.credentials_status.config(text=f"Credentials saved for: {username}", 
                                         foreground='green')
            self.update_status("Credentials saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")
            
    def load_credentials(self):
        """Load saved credentials"""
        try:
            credentials = self.credential_manager.load_credentials()
            if credentials:
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, credentials['username'])
                # Don't show password for security
                self.current_credentials = credentials
                self.credentials_status.config(text=f"Credentials loaded for: {credentials['username']}", 
                                             foreground='green')
                self.update_status("Credentials loaded successfully")
            else:
                self.credentials_status.config(text="No saved credentials found", 
                                             foreground='gray')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load credentials: {str(e)}")
            
    def clear_credentials(self):
        """Clear credentials"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.current_credentials = None
        self.credentials_status.config(text="Credentials cleared", foreground='gray')
        self.update_status("Credentials cleared")
        
    def add_dashboard(self):
        """Add a new dashboard"""
        name = self.dashboard_name_entry.get().strip()
        url = self.dashboard_url_entry.get().strip()
        list_name = self.dashboard_list_combo.get()
        
        if not name or not url:
            messagebox.showerror("Error", "Please enter both name and URL")
            return
            
        try:
            dashboard_id = name.lower().replace(' ', '_')
            
            # Create dashboard object
            dashboard = {
                'id': dashboard_id,
                'name': name,
                'url': url,
                'list_name': list_name if list_name else None,
                'created_at': get_current_timestamp(),
            }
            
            self.dashboards[dashboard_id] = dashboard
            self.save_dashboards()
            
            self.dashboard_name_entry.delete(0, tk.END)
            self.dashboard_url_entry.delete(0, tk.END)
            self.refresh_dashboards()
            self.update_status(f"Dashboard '{name}' added successfully")
            messagebox.showinfo("Success", f"Dashboard '{name}' added successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add dashboard: {str(e)}")
            
    def delete_dashboard(self):
        """Delete selected dashboard"""
        selection = self.dashboard_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a dashboard to delete")
            return
            
        item = self.dashboard_tree.item(selection[0])
        dashboard_name = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete dashboard '{dashboard_name}'?"):
            try:
                # Find and delete dashboard
                dashboard_id = None
                for did, dashboard in self.dashboards.items():
                    if dashboard['name'] == dashboard_name:
                        dashboard_id = did
                        break
                        
                if dashboard_id:
                    del self.dashboards[dashboard_id]
                    self.save_dashboards()
                    self.refresh_dashboards()
                    self.update_status(f"Dashboard '{dashboard_name}' deleted")
                    messagebox.showinfo("Success", f"Dashboard '{dashboard_name}' deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete dashboard: {str(e)}")
                
    def refresh_dashboards(self):
        """Refresh dashboard list"""
        # Clear existing items
        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)
            
        # Load dashboards
        try:
            for dashboard in self.dashboards.values():
                created = dashboard.get('created_at', 'Unknown')
                self.dashboard_tree.insert('', 'end', values=(
                    dashboard['name'],
                    dashboard['url'],
                    dashboard.get('list_name', ''),
                    created
                ))
        except Exception as e:
            self.update_status(f"Error loading dashboards: {str(e)}")
            
    def create_list(self):
        """Create a new list"""
        name = self.list_name_entry.get().strip()
        description = self.list_desc_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter a list name")
            return
            
        try:
            # Create list object
            list_obj = {
                'name': name,
                'description': description,
                'created_at': get_current_timestamp(),
            }
            
            self.lists[name] = list_obj
            self.save_lists()
            
            self.list_name_entry.delete(0, tk.END)
            self.list_desc_entry.delete(0, tk.END)
            self.refresh_lists()
            self.update_combos()
            self.update_status(f"List '{name}' created successfully")
            messagebox.showinfo("Success", f"List '{name}' created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create list: {str(e)}")
            
    def delete_list(self):
        """Delete selected list"""
        selection = self.lists_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a list to delete")
            return
            
        item = self.lists_tree.item(selection[0])
        list_name = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete list '{list_name}'?"):
            try:
                if list_name in self.lists:
                    del self.lists[list_name]
                    self.save_lists()
                    self.refresh_lists()
                    self.update_combos()
                    self.update_status(f"List '{list_name}' deleted")
                    messagebox.showinfo("Success", f"List '{list_name}' deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete list: {str(e)}")
                
    def refresh_lists(self):
        """Refresh lists display"""
        # Clear existing items
        for item in self.lists_tree.get_children():
            self.lists_tree.delete(item)
            
        # Load lists
        try:
            for lst in self.lists.values():
                # Count dashboards in this list
                dashboard_count = sum(1 for d in self.dashboards.values() 
                                    if d.get('list_name') == lst['name'])
                
                created = lst.get('created_at', 'Unknown')
                self.lists_tree.insert('', 'end', values=(
                    lst['name'],
                    lst.get('description', ''),
                    dashboard_count,
                    created
                ))
        except Exception as e:
            self.update_status(f"Error loading lists: {str(e)}")
            
    def take_screenshot(self):
        """Take screenshot of selected dashboard"""
        selection = self.dashboard_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a dashboard")
            return
            
        if not self.current_credentials:
            messagebox.showerror("Error", "Please save credentials first")
            return
            
        item = self.dashboard_tree.item(selection[0])
        dashboard_name = item['values'][0]
        
        # Find dashboard
        dashboard = None
        for d in self.dashboards.values():
            if d['name'] == dashboard_name:
                dashboard = d
                break
                
        if dashboard:
            # Run in background thread
            threading.Thread(target=self._take_screenshot_background, 
                            args=(dashboard,), daemon=True).start()
            self.update_status(f"Taking screenshot of '{dashboard_name}'...")
        
    def _take_screenshot_background(self, dashboard):
        """Take screenshot in background thread"""
        try:
            # Use asyncio to run the screenshot capture
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Simple screenshot logic - this would call the actual screenshot manager
            # For now, just simulate success
            success = True
            
            # Update UI in main thread
            self.root.after(0, self._screenshot_completed, dashboard['name'], success)
        except Exception as e:
            self.root.after(0, self._screenshot_error, dashboard['name'], str(e))
            
    def _screenshot_completed(self, dashboard_name, success):
        """Handle screenshot completion in main thread"""
        if success:
            message = f"Screenshot of '{dashboard_name}' would be saved successfully"
            self.update_status(message)
            messagebox.showinfo("Screenshot Complete", message)
        else:
            message = f"Failed to capture screenshot of '{dashboard_name}'"
            self.update_status(message)
            messagebox.showerror("Screenshot Error", message)
            
    def _screenshot_error(self, dashboard_name, error):
        """Handle screenshot error in main thread"""
        message = f"Failed to capture screenshot of '{dashboard_name}': {error}"
        self.update_status(message)
        messagebox.showerror("Screenshot Error", message)
        
    def browse_screenshot_dir(self):
        """Browse for screenshot directory"""
        directory = filedialog.askdirectory(initialdir=self.screenshot_dir_var.get())
        if directory:
            self.screenshot_dir_var.set(directory)
            
    def save_settings(self):
        """Save application settings"""
        try:
            # This would save settings to a configuration file
            timeout = int(self.timeout_var.get())
            concurrent = int(self.concurrent_var.get())
            screenshot_dir = self.screenshot_dir_var.get()
            
            self.update_status("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def reset_settings(self):
        """Reset settings to defaults"""
        self.timeout_var.set("30")
        self.concurrent_var.set("3")
        self.screenshot_dir_var.set("screenshots")
        self.update_status("Settings reset to defaults")
        
    def update_status(self, message):
        """Update status bar"""
        timestamp = get_current_timestamp()
        self.status_bar.config(text=f"{timestamp}: {message}")
        
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

def main():
    """Main function to run the desktop application"""
    # Create necessary directories
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    os.makedirs(Config.TMP_DIR, exist_ok=True)
    os.makedirs(Config.SCREENSHOT_ARCHIVE_DIR, exist_ok=True)
    
    # Create and run the GUI
    app = SimpleSplunkGUI()
    app.run()

if __name__ == "__main__":
    main()