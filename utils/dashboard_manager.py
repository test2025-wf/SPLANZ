"""
Dashboard Manager Module
========================

This module provides functionality for managing Splunk dashboards and lists
including creation, deletion, organization, and persistence.
"""

import json
import uuid
import logging
from typing import Dict, List, Optional, Any
from utils.config import Config, get_current_timestamp, validate_url, sanitize_filename

logger = logging.getLogger(__name__)

class DashboardManager:
    """
    Manages Splunk dashboard configurations and metadata.
    
    This class handles dashboard creation, deletion, updates, and persistence
    to JSON files. Each dashboard contains metadata like name, URL, creation
    time, and optional list assignment.
    """
    
    def __init__(self):
        """Initialize the dashboard manager"""
        self.dashboards_file = Config.DASHBOARD_FILE
        self.dashboards = self._load_dashboards()
        
    def _load_dashboards(self) -> Dict[str, Any]:
        """
        Load dashboards from JSON file.
        
        Returns:
            dict: Dictionary of dashboard configurations keyed by ID
        """
        try:
            with open(self.dashboards_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} dashboards from {self.dashboards_file}")
                return data
        except FileNotFoundError:
            logger.info(f"No existing dashboards file found, creating new one")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in dashboards file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading dashboards: {e}")
            return {}
            
    def _save_dashboards(self) -> bool:
        """
        Save dashboards to JSON file.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(self.dashboards_file, 'w') as f:
                json.dump(self.dashboards, f, indent=2, default=str)
            logger.info(f"Saved {len(self.dashboards)} dashboards to {self.dashboards_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving dashboards: {e}")
            return False
            
    def add_dashboard(self, name: str, url: str, list_name: Optional[str] = None) -> str:
        """
        Add a new dashboard.
        
        Args:
            name (str): Dashboard name
            url (str): Dashboard URL
            list_name (str, optional): Name of list to assign dashboard to
            
        Returns:
            str: Dashboard ID
            
        Raises:
            ValueError: If name/URL invalid or dashboard already exists
        """
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Dashboard name cannot be empty")
            
        if not url or not url.strip():
            raise ValueError("Dashboard URL cannot be empty")
            
        if not validate_url(url):
            raise ValueError("Invalid URL format")
            
        # Check for duplicate names
        for dashboard in self.dashboards.values():
            if dashboard['name'].lower() == name.strip().lower():
                raise ValueError(f"Dashboard with name '{name}' already exists")
                
        # Generate unique ID
        dashboard_id = str(uuid.uuid4())
        
        # Create dashboard object
        dashboard = {
            'id': dashboard_id,
            'name': name.strip(),
            'url': url.strip(),
            'list_name': list_name.strip() if list_name else None,
            'created_at': get_current_timestamp(),
            'last_captured': None,
            'capture_count': 0,
            'active': True
        }
        
        # Add to collection
        self.dashboards[dashboard_id] = dashboard
        
        # Save to file
        if self._save_dashboards():
            logger.info(f"Added dashboard: {name} (ID: {dashboard_id})")
            return dashboard_id
        else:
            # Rollback on save failure
            del self.dashboards[dashboard_id]
            raise Exception("Failed to save dashboard to file")
            
    def update_dashboard(self, dashboard_id: str, name: Optional[str] = None, 
                        url: Optional[str] = None, list_name: Optional[str] = None) -> bool:
        """
        Update an existing dashboard.
        
        Args:
            dashboard_id (str): Dashboard ID to update
            name (str, optional): New dashboard name
            url (str, optional): New dashboard URL
            list_name (str, optional): New list assignment
            
        Returns:
            bool: True if updated successfully
            
        Raises:
            ValueError: If dashboard not found or invalid parameters
        """
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard with ID '{dashboard_id}' not found")
            
        dashboard = self.dashboards[dashboard_id]
        
        # Update fields if provided
        if name is not None:
            if not name.strip():
                raise ValueError("Dashboard name cannot be empty")
            dashboard['name'] = name.strip()
            
        if url is not None:
            if not url.strip():
                raise ValueError("Dashboard URL cannot be empty")
            if not validate_url(url):
                raise ValueError("Invalid URL format")
            dashboard['url'] = url.strip()
            
        if list_name is not None:
            dashboard['list_name'] = list_name.strip() if list_name else None
            
        dashboard['updated_at'] = get_current_timestamp()
        
        # Save changes
        if self._save_dashboards():
            logger.info(f"Updated dashboard: {dashboard['name']} (ID: {dashboard_id})")
            return True
        else:
            raise Exception("Failed to save dashboard updates")
            
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a dashboard.
        
        Args:
            dashboard_id (str): Dashboard ID to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            ValueError: If dashboard not found
        """
        if dashboard_id not in self.dashboards:
            raise ValueError(f"Dashboard with ID '{dashboard_id}' not found")
            
        dashboard_name = self.dashboards[dashboard_id]['name']
        del self.dashboards[dashboard_id]
        
        if self._save_dashboards():
            logger.info(f"Deleted dashboard: {dashboard_name} (ID: {dashboard_id})")
            return True
        else:
            raise Exception("Failed to save after dashboard deletion")
            
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific dashboard by ID.
        
        Args:
            dashboard_id (str): Dashboard ID
            
        Returns:
            dict or None: Dashboard data if found
        """
        return self.dashboards.get(dashboard_id)
        
    def get_all_dashboards(self) -> Dict[str, Any]:
        """
        Get all dashboards.
        
        Returns:
            dict: All dashboard configurations keyed by ID
        """
        return self.dashboards.copy()
        
    def get_dashboards_by_list(self, list_name: str) -> Dict[str, Any]:
        """
        Get all dashboards in a specific list.
        
        Args:
            list_name (str): List name to filter by
            
        Returns:
            dict: Dashboards in the specified list
        """
        filtered = {}
        for dashboard_id, dashboard in self.dashboards.items():
            if dashboard.get('list_name') == list_name:
                filtered[dashboard_id] = dashboard
        return filtered
        
    def update_capture_stats(self, dashboard_id: str, success: bool = True) -> bool:
        """
        Update dashboard capture statistics.
        
        Args:
            dashboard_id (str): Dashboard ID
            success (bool): Whether the capture was successful
            
        Returns:
            bool: True if updated successfully
        """
        if dashboard_id not in self.dashboards:
            logger.warning(f"Cannot update stats for unknown dashboard: {dashboard_id}")
            return False
            
        dashboard = self.dashboards[dashboard_id]
        dashboard['capture_count'] = dashboard.get('capture_count', 0) + 1
        
        if success:
            dashboard['last_captured'] = get_current_timestamp()
            dashboard['last_capture_status'] = 'success'
        else:
            dashboard['last_capture_status'] = 'failed'
            
        return self._save_dashboards()


class ListManager:
    """
    Manages dashboard lists for organization and grouping.
    
    This class handles creation, deletion, and management of dashboard lists
    which allow users to organize dashboards into logical groups for
    scheduling and bulk operations.
    """
    
    def __init__(self):
        """Initialize the list manager"""
        self.lists_file = "lists.json"
        self.lists = self._load_lists()
        
    def _load_lists(self) -> Dict[str, Any]:
        """
        Load lists from JSON file.
        
        Returns:
            dict: Dictionary of list configurations keyed by ID
        """
        try:
            with open(self.lists_file, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} lists from {self.lists_file}")
                return data
        except FileNotFoundError:
            logger.info(f"No existing lists file found, creating new one")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in lists file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading lists: {e}")
            return {}
            
    def _save_lists(self) -> bool:
        """
        Save lists to JSON file.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(self.lists_file, 'w') as f:
                json.dump(self.lists, f, indent=2, default=str)
            logger.info(f"Saved {len(self.lists)} lists to {self.lists_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving lists: {e}")
            return False
            
    def create_list(self, name: str, description: str = "") -> str:
        """
        Create a new dashboard list.
        
        Args:
            name (str): List name
            description (str): List description
            
        Returns:
            str: List ID
            
        Raises:
            ValueError: If name invalid or list already exists
        """
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("List name cannot be empty")
            
        # Check for duplicate names
        for lst in self.lists.values():
            if lst['name'].lower() == name.strip().lower():
                raise ValueError(f"List with name '{name}' already exists")
                
        # Generate unique ID
        list_id = str(uuid.uuid4())
        
        # Create list object
        list_obj = {
            'id': list_id,
            'name': name.strip(),
            'description': description.strip() if description else "",
            'created_at': get_current_timestamp(),
            'active': True
        }
        
        # Add to collection
        self.lists[list_id] = list_obj
        
        # Save to file
        if self._save_lists():
            logger.info(f"Created list: {name} (ID: {list_id})")
            return list_id
        else:
            # Rollback on save failure
            del self.lists[list_id]
            raise Exception("Failed to save list to file")
            
    def update_list(self, list_id: str, name: Optional[str] = None, 
                   description: Optional[str] = None) -> bool:
        """
        Update an existing list.
        
        Args:
            list_id (str): List ID to update
            name (str, optional): New list name
            description (str, optional): New list description
            
        Returns:
            bool: True if updated successfully
            
        Raises:
            ValueError: If list not found or invalid parameters
        """
        if list_id not in self.lists:
            raise ValueError(f"List with ID '{list_id}' not found")
            
        lst = self.lists[list_id]
        
        # Update fields if provided
        if name is not None:
            if not name.strip():
                raise ValueError("List name cannot be empty")
            lst['name'] = name.strip()
            
        if description is not None:
            lst['description'] = description.strip() if description else ""
            
        lst['updated_at'] = get_current_timestamp()
        
        # Save changes
        if self._save_lists():
            logger.info(f"Updated list: {lst['name']} (ID: {list_id})")
            return True
        else:
            raise Exception("Failed to save list updates")
            
    def delete_list(self, list_id: str) -> bool:
        """
        Delete a list.
        
        Args:
            list_id (str): List ID to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            ValueError: If list not found
        """
        if list_id not in self.lists:
            raise ValueError(f"List with ID '{list_id}' not found")
            
        list_name = self.lists[list_id]['name']
        del self.lists[list_id]
        
        if self._save_lists():
            logger.info(f"Deleted list: {list_name} (ID: {list_id})")
            return True
        else:
            raise Exception("Failed to save after list deletion")
            
    def get_list(self, list_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific list by ID.
        
        Args:
            list_id (str): List ID
            
        Returns:
            dict or None: List data if found
        """
        return self.lists.get(list_id)
        
    def get_all_lists(self) -> Dict[str, Any]:
        """
        Get all lists.
        
        Returns:
            dict: All list configurations keyed by ID
        """
        return self.lists.copy()
        
    def get_list_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a list by name.
        
        Args:
            name (str): List name
            
        Returns:
            dict or None: List data if found
        """
        for lst in self.lists.values():
            if lst['name'].lower() == name.lower():
                return lst
        return None