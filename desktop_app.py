"""
Splunk Dashboard Automator - Desktop Application
===============================================

A desktop GUI application for automating Splunk dashboard interactions
including screenshot capture, scheduling, and credential management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import asyncio
import json
import os
from datetime import datetime, timedelta
from utils.config import Config, TimeRangePresets, get_current_timestamp
from utils.encryption import CredentialManager
from utils.screenshot import ScreenshotManager
from utils.scheduler import ScheduleManager
from utils.dashboard_manager import DashboardManager, ListManager

class SplunkAutomatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Splunk Dashboard Automator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize managers
        self.credential_manager = CredentialManager()
        self.screenshot_manager = ScreenshotManager()
        self.schedule_manager = ScheduleManager()
        self.dashboard_manager = DashboardManager()
        self.list_manager = ListManager()
        
        # Current credentials
        self.current_credentials = None
        
        # Create the GUI
        self.create_widgets()
        self.load_initial_data()
        
        # Start scheduler in background
        self.start_scheduler()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_credentials_tab()
        self.create_dashboards_tab()
        self.create_lists_tab()
        self.create_scheduler_tab()
        self.create_settings_tab()
        
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
        self.dashboard_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
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
                                      show='headings', height=15)
        
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
        
    def create_scheduler_tab(self):
        """Create scheduler tab"""
        scheduler_frame = ttk.Frame(self.notebook)
        self.notebook.add(scheduler_frame, text="Scheduler")
        
        # Title
        title_label = ttk.Label(scheduler_frame, text="Schedule Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Add schedule form
        add_schedule_frame = ttk.LabelFrame(scheduler_frame, text="Create New Schedule", padding=10)
        add_schedule_frame.pack(fill='x', padx=10, pady=5)
        
        schedule_form = ttk.Frame(add_schedule_frame)
        schedule_form.pack(fill='x')
        
        # Schedule name
        ttk.Label(schedule_form, text="Name:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.schedule_name_entry = ttk.Entry(schedule_form, width=30)
        self.schedule_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Schedule type
        ttk.Label(schedule_form, text="Type:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.schedule_type_combo = ttk.Combobox(schedule_form, 
                                               values=['once', 'daily', 'weekly', 'monthly'],
                                               state='readonly', width=27)
        self.schedule_type_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Time
        ttk.Label(schedule_form, text="Time:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        time_frame = ttk.Frame(schedule_form)
        time_frame.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        self.hour_spinbox = tk.Spinbox(time_frame, from_=0, to=23, width=5, format="%02.0f")
        self.hour_spinbox.pack(side='left')
        ttk.Label(time_frame, text=":").pack(side='left', padx=2)
        self.minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, width=5, format="%02.0f")
        self.minute_spinbox.pack(side='left')
        
        # List selection
        ttk.Label(schedule_form, text="List:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.schedule_list_combo = ttk.Combobox(schedule_form, width=27, state='readonly')
        self.schedule_list_combo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(schedule_form, text="Create Schedule", 
                  command=self.create_schedule).grid(row=3, column=2, padx=5, pady=5)
        
        # Schedules display
        schedules_display_frame = ttk.LabelFrame(scheduler_frame, text="Active Schedules", padding=10)
        schedules_display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Schedules treeview
        schedule_columns = ('Name', 'Type', 'Time', 'List', 'Status', 'Next Run')
        self.schedules_tree = ttk.Treeview(schedules_display_frame, columns=schedule_columns, 
                                          show='headings', height=10)
        
        for col in schedule_columns:
            self.schedules_tree.heading(col, text=col)
            self.schedules_tree.column(col, width=150)
        
        # Schedules scrollbar
        schedules_scrollbar = ttk.Scrollbar(schedules_display_frame, orient='vertical', 
                                           command=self.schedules_tree.yview)
        self.schedules_tree.configure(yscrollcommand=schedules_scrollbar.set)
        
        # Pack schedules treeview
        self.schedules_tree.pack(side='left', fill='both', expand=True)
        schedules_scrollbar.pack(side='right', fill='y')
        
        # Schedule buttons
        schedule_buttons = ttk.Frame(scheduler_frame)
        schedule_buttons.pack(pady=10)
        
        ttk.Button(schedule_buttons, text="Run Now", 
                  command=self.run_schedule_now).pack(side='left', padx=5)
        ttk.Button(schedule_buttons, text="Delete Schedule", 
                  command=self.delete_schedule).pack(side='left', padx=5)
        ttk.Button(schedule_buttons, text="Refresh Schedules", 
                  command=self.refresh_schedules).pack(side='left', padx=5)
        
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
        self.timeout_spinbox = tk.Spinbox(screenshot_frame, from_=10, to=120, width=10)
        self.timeout_spinbox.set(Config.SCREENSHOT_TIMEOUT)
        self.timeout_spinbox.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(screenshot_frame, text="Max Concurrent Screenshots:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.concurrent_spinbox = tk.Spinbox(screenshot_frame, from_=1, to=10, width=10)
        self.concurrent_spinbox.set(Config.MAX_CONCURRENT_SCREENSHOTS)
        self.concurrent_spinbox.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Archive settings
        archive_frame = ttk.LabelFrame(settings_frame, text="Archive Settings", padding=10)
        archive_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(archive_frame, text="Days to Keep Archives:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.archive_days_spinbox = tk.Spinbox(archive_frame, from_=1, to=30, width=10)
        self.archive_days_spinbox.set(Config.DAYS_TO_KEEP_ARCHIVES)
        self.archive_days_spinbox.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Directory settings
        dir_frame = ttk.LabelFrame(settings_frame, text="Directory Settings", padding=10)
        dir_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(dir_frame, text="Screenshot Directory:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.screenshot_dir_entry = ttk.Entry(dir_frame, width=50)
        self.screenshot_dir_entry.insert(0, Config.SCREENSHOT_ARCHIVE_DIR)
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
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
        
    def load_initial_data(self):
        """Load initial data into the GUI"""
        self.load_credentials()
        self.refresh_dashboards()
        self.refresh_lists()
        self.refresh_schedules()
        self.update_combos()
        
    def update_combos(self):
        """Update combo box values"""
        lists = self.list_manager.get_all_lists()
        list_names = [lst['name'] for lst in lists.values()]
        
        self.dashboard_list_combo['values'] = list_names
        self.schedule_list_combo['values'] = list_names
        
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
            dashboard_id = self.dashboard_manager.add_dashboard(name, url, list_name)
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
                dashboards = self.dashboard_manager.get_all_dashboards()
                dashboard_id = None
                for did, dashboard in dashboards.items():
                    if dashboard['name'] == dashboard_name:
                        dashboard_id = did
                        break
                        
                if dashboard_id:
                    self.dashboard_manager.delete_dashboard(dashboard_id)
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
            dashboards = self.dashboard_manager.get_all_dashboards()
            for dashboard in dashboards.values():
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
            list_id = self.list_manager.create_list(name, description)
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
                lists = self.list_manager.get_all_lists()
                list_id = None
                for lid, lst in lists.items():
                    if lst['name'] == list_name:
                        list_id = lid
                        break
                        
                if list_id:
                    self.list_manager.delete_list(list_id)
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
            lists = self.list_manager.get_all_lists()
            dashboards = self.dashboard_manager.get_all_dashboards()
            
            for lst in lists.values():
                # Count dashboards in this list
                dashboard_count = sum(1 for d in dashboards.values() 
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
            
    def create_schedule(self):
        """Create a new schedule"""
        name = self.schedule_name_entry.get().strip()
        schedule_type = self.schedule_type_combo.get()
        hour = int(self.hour_spinbox.get())
        minute = int(self.minute_spinbox.get())
        list_name = self.schedule_list_combo.get()
        
        if not name or not schedule_type:
            messagebox.showerror("Error", "Please enter schedule name and type")
            return
            
        try:
            # Create schedule time
            now = datetime.now()
            schedule_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time is in the past today, schedule for tomorrow (for once and daily)
            if schedule_time <= now and schedule_type in ['once', 'daily']:
                schedule_time += timedelta(days=1)
                
            schedule_id = self.schedule_manager.create_schedule(
                name, schedule_type, schedule_time, list_name
            )
            
            # Clear form
            self.schedule_name_entry.delete(0, tk.END)
            self.hour_spinbox.delete(0, tk.END)
            self.hour_spinbox.insert(0, "09")
            self.minute_spinbox.delete(0, tk.END)
            self.minute_spinbox.insert(0, "00")
            
            self.refresh_schedules()
            self.update_status(f"Schedule '{name}' created successfully")
            messagebox.showinfo("Success", f"Schedule '{name}' created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create schedule: {str(e)}")
            
    def delete_schedule(self):
        """Delete selected schedule"""
        selection = self.schedules_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a schedule to delete")
            return
            
        item = self.schedules_tree.item(selection[0])
        schedule_name = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete schedule '{schedule_name}'?"):
            try:
                schedules = self.schedule_manager.get_all_schedules()
                schedule_id = None
                for sid, schedule in schedules.items():
                    if schedule['name'] == schedule_name:
                        schedule_id = sid
                        break
                        
                if schedule_id:
                    self.schedule_manager.delete_schedule(schedule_id)
                    self.refresh_schedules()
                    self.update_status(f"Schedule '{schedule_name}' deleted")
                    messagebox.showinfo("Success", f"Schedule '{schedule_name}' deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete schedule: {str(e)}")
                
    def run_schedule_now(self):
        """Run selected schedule immediately"""
        selection = self.schedules_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a schedule to run")
            return
            
        item = self.schedules_tree.item(selection[0])
        schedule_name = item['values'][0]
        
        # Run in background thread
        threading.Thread(target=self._run_schedule_background, 
                        args=(schedule_name,), daemon=True).start()
        
        self.update_status(f"Running schedule '{schedule_name}'...")
        
    def _run_schedule_background(self, schedule_name):
        """Run schedule in background thread"""
        try:
            schedules = self.schedule_manager.get_all_schedules()
            schedule_id = None
            for sid, schedule in schedules.items():
                if schedule['name'] == schedule_name:
                    schedule_id = sid
                    break
                    
            if schedule_id and self.current_credentials:
                result = asyncio.run(self.schedule_manager.execute_schedule(
                    schedule_id, self.current_credentials
                ))
                
                # Update UI in main thread
                self.root.after(0, self._schedule_completed, schedule_name, result)
            else:
                self.root.after(0, self._schedule_error, schedule_name, "No credentials available")
        except Exception as e:
            self.root.after(0, self._schedule_error, schedule_name, str(e))
            
    def _schedule_completed(self, schedule_name, result):
        """Handle schedule completion in main thread"""
        if result['success']:
            message = f"Schedule '{schedule_name}' completed successfully. " \
                     f"Captured {result['successful_captures']} screenshots."
            self.update_status(message)
            messagebox.showinfo("Schedule Complete", message)
        else:
            message = f"Schedule '{schedule_name}' completed with errors. " \
                     f"Check the logs for details."
            self.update_status(message)
            messagebox.showwarning("Schedule Complete", message)
            
    def _schedule_error(self, schedule_name, error):
        """Handle schedule error in main thread"""
        message = f"Failed to run schedule '{schedule_name}': {error}"
        self.update_status(message)
        messagebox.showerror("Schedule Error", message)
        
    def refresh_schedules(self):
        """Refresh schedules display"""
        # Clear existing items
        for item in self.schedules_tree.get_children():
            self.schedules_tree.delete(item)
            
        # Load schedules
        try:
            schedules = self.schedule_manager.get_all_schedules()
            for schedule in schedules.values():
                next_run = schedule.get('next_run', 'Unknown')
                status = schedule.get('status', 'Active')
                
                self.schedules_tree.insert('', 'end', values=(
                    schedule['name'],
                    schedule['type'],
                    schedule.get('time', 'Unknown'),
                    schedule.get('list_name', ''),
                    status,
                    next_run
                ))
        except Exception as e:
            self.update_status(f"Error loading schedules: {str(e)}")
            
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
        
        # Run in background thread
        threading.Thread(target=self._take_screenshot_background, 
                        args=(dashboard_name,), daemon=True).start()
        
        self.update_status(f"Taking screenshot of '{dashboard_name}'...")
        
    def _take_screenshot_background(self, dashboard_name):
        """Take screenshot in background thread"""
        try:
            dashboards = self.dashboard_manager.get_all_dashboards()
            dashboard = None
            
            for d in dashboards.values():
                if d['name'] == dashboard_name:
                    dashboard = d
                    break
                    
            if dashboard:
                result = asyncio.run(self.screenshot_manager.capture_dashboard_screenshot(
                    dashboard, self.current_credentials
                ))
                
                # Update UI in main thread
                self.root.after(0, self._screenshot_completed, dashboard_name, result)
            else:
                self.root.after(0, self._screenshot_error, dashboard_name, "Dashboard not found")
        except Exception as e:
            self.root.after(0, self._screenshot_error, dashboard_name, str(e))
            
    def _screenshot_completed(self, dashboard_name, result):
        """Handle screenshot completion in main thread"""
        if result['success']:
            message = f"Screenshot of '{dashboard_name}' saved successfully"
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
        directory = filedialog.askdirectory(initialdir=self.screenshot_dir_entry.get())
        if directory:
            self.screenshot_dir_entry.delete(0, tk.END)
            self.screenshot_dir_entry.insert(0, directory)
            
    def save_settings(self):
        """Save application settings"""
        try:
            # Update Config values (this is just for the current session)
            Config.SCREENSHOT_TIMEOUT = int(self.timeout_spinbox.get())
            Config.MAX_CONCURRENT_SCREENSHOTS = int(self.concurrent_spinbox.get())
            Config.DAYS_TO_KEEP_ARCHIVES = int(self.archive_days_spinbox.get())
            Config.SCREENSHOT_ARCHIVE_DIR = self.screenshot_dir_entry.get()
            
            self.update_status("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def reset_settings(self):
        """Reset settings to defaults"""
        self.timeout_spinbox.delete(0, tk.END)
        self.timeout_spinbox.insert(0, "30")
        
        self.concurrent_spinbox.delete(0, tk.END)
        self.concurrent_spinbox.insert(0, "3")
        
        self.archive_days_spinbox.delete(0, tk.END)
        self.archive_days_spinbox.insert(0, "7")
        
        self.screenshot_dir_entry.delete(0, tk.END)
        self.screenshot_dir_entry.insert(0, "screenshots")
        
        self.update_status("Settings reset to defaults")
        
    def start_scheduler(self):
        """Start the scheduler in background"""
        def scheduler_loop():
            self.schedule_manager.start()
            
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        
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
    app = SplunkAutomatorGUI()
    app.run()

if __name__ == "__main__":
    main()