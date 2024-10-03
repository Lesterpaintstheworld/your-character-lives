import os
import zipfile
import json
from datetime import datetime

class SavefileManager:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.last_data = None
        self.last_check_time = None

    def read(self):
        """
        Extracts the latest savefile and returns its content as a string.
        """
        latest_save = self._get_latest_save()
        if not latest_save:
            return None

        with zipfile.ZipFile(latest_save, 'r') as zip_ref:
            with zip_ref.open('gamestate') as file:
                content = file.read().decode('utf-8')

        # Store this data for future diff
        self.last_data = content
        self.last_check_time = datetime.now()

        return content

    def readiff(self):
        """
        Returns the difference between the last check and now.
        """
        current_data = self.read()
        if not self.last_data or not current_data:
            return None

        # Here we're just doing a simple string comparison
        # In a real implementation, you might want to use a more sophisticated
        # diff algorithm, possibly operating on structured data
        changes = []
        for i, (old_line, new_line) in enumerate(zip(self.last_data.splitlines(), current_data.splitlines())):
            if old_line != new_line:
                changes.append(f"Line {i+1} changed: '{old_line}' -> '{new_line}'")

        return "\n".join(changes)

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
# print(manager.read())  # Reads the latest save
# print(manager.readiff())  # Shows changes since last read
