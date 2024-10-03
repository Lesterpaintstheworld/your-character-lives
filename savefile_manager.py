import os
import zipfile
import json
from datetime import datetime
from difflib import unified_diff

class SavefileManager:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.last_data = None
        self.last_check_time = None

    def read(self):
        """
        Extracts the latest savefile and returns its content as a structured dictionary.
        """
        latest_save = self._get_latest_save()
        if not latest_save:
            return None

        with zipfile.ZipFile(latest_save, 'r') as zip_ref:
            with zip_ref.open('gamestate') as file:
                content = file.read().decode('utf-8')

        # Parse the content into a structured format
        parsed_content = self._parse_gamestate(content)

        # Store this data for future diff
        self.last_data = parsed_content
        self.last_check_time = datetime.now()

        return parsed_content

    def readiff(self):
        """
        Returns the difference between the last check and now as a structured dictionary.
        """
        current_data = self.read()
        if not self.last_data or not current_data:
            return None

        diff = self._deep_diff(self.last_data, current_data)
        
        # Update last_data for future diffs
        self.last_data = current_data
        self.last_check_time = datetime.now()

        return diff

    def _parse_gamestate(self, content):
        """
        Parses the gamestate content into a structured dictionary.
        """
        # This is a simplified parser. You might need to implement a more robust parser
        # depending on the actual structure of the gamestate file.
        parsed = {}
        current_key = None
        for line in content.split('\n'):
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                parsed[key.strip()] = value.strip()
                current_key = key.strip()
            elif current_key:
                parsed[current_key] += ' ' + line
        return parsed

    def _deep_diff(self, old, new):
        """
        Computes a deep difference between two dictionaries.
        """
        diff = {}
        for key in set(old.keys()) | set(new.keys()):
            if key not in old:
                diff[key] = ('added', new[key])
            elif key not in new:
                diff[key] = ('removed', old[key])
            elif old[key] != new[key]:
                diff[key] = ('changed', old[key], new[key])
        return diff

    def _get_latest_save(self):
        """
        Returns the path to the latest savefile.
        """
        save_files = [f for f in os.listdir(self.save_dir) if f.endswith('.ck3')]
        if not save_files:
            return None

        return os.path.join(self.save_dir, max(save_files, key=lambda x: os.path.getmtime(os.path.join(self.save_dir, x))))

# Example usage:
# save_dir = r"C:\Users\YourUsername\Documents\Paradox Interactive\Crusader Kings III\save games"
# manager = SavefileManager(save_dir)
# print(manager.read())  # Reads the latest save as a structured dictionary
# print(manager.readiff())  # Shows structured changes since last read
