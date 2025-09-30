import os
import pandas as pd
import json
import app.utils.db_utils as _db_utils
from config import conf

class DataframeManager():
    def __init__(self, turnus_set_id=None):
        """Initialize with either a specific turnus set or the active one"""
        self.current_turnus_set = None
        self.df = pd.DataFrame()  # Empty dataframe as default
        self.turnus_data = []     # Empty list as default
        self.load_turnus_set(turnus_set_id)
    
    def load_turnus_set(self, turnus_set_id=None):
        """Load a specific turnus set or the active one"""
        
        if turnus_set_id:
            # Load specific turnus set by ID
            all_sets = _db_utils.get_all_turnus_sets()
            turnus_set = next((ts for ts in all_sets if ts['id'] == turnus_set_id), None)
        else:
            # Load the currently active turnus set
            turnus_set = _db_utils.get_active_turnus_set()
        
        if not turnus_set:
            print("No turnus set found! Using empty data.")
            self.current_turnus_set = None
            self.df = pd.DataFrame()
            self.turnus_data = []
            return False
        
        self.current_turnus_set = turnus_set
        
        try:
            # Use database file paths if available
            if turnus_set.get('turnus_file_path') and turnus_set.get('df_file_path'):
                # Convert database paths to OS-specific paths
                turnus_path = os.path.normpath(turnus_set['turnus_file_path'])
                df_path = os.path.normpath(turnus_set['df_file_path'])
            else:
                # Construct paths based on turnus set identifier
                year_id = turnus_set['year_identifier'].lower()
                turnus_path = os.path.join(conf.turnusfiler_dir, year_id, f'turnuser_{turnus_set["year_identifier"]}.json')
                df_path = os.path.join(conf.turnusfiler_dir, year_id, f'turnus_df_{turnus_set["year_identifier"]}.json')
            
            # Load dataframe
            if os.path.exists(df_path):
                self.df = pd.read_json(df_path)
            else:
                print(f"DataFrame file not found: {df_path}")
                self.df = pd.DataFrame()
            
            # Load turnus data
            if os.path.exists(turnus_path):
                with open(turnus_path, 'r') as f:
                    self.turnus_data = json.load(f)
            else:
                print(f"Turnus file not found: {turnus_path}")
                self.turnus_data = []
            
            return True
        except Exception as e:
            print(f"Error loading turnus set {turnus_set['year_identifier']}: {e}")
            self.df = pd.DataFrame()
            self.turnus_data = []
            return False
    
    def get_current_turnus_info(self):
        """Get information about the currently loaded turnus set"""
        return self.current_turnus_set
    
    def reload_active_set(self):
        """Reload the currently active turnus set (useful after switching sets)"""
        return self.load_turnus_set()
    
    def has_data(self):
        """Check if we have valid data loaded"""
        return not self.df.empty and len(self.turnus_data) > 0