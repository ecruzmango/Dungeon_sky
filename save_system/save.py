import os
import json
import datetime
from pathlib import Path

class SaveSystem:
    def __init__(self):
        # Create saves directory in user's documents folder
        self.save_dir = os.path.join(str(Path.home()), "Documents", "YourGameName", "saves")
        os.makedirs(self.save_dir, exist_ok=True)
        
    def create_save_data(self, player, current_boss_state):
        """Create a dictionary containing all necessary game state data"""
        save_data = {
            "player": {
                "health": player.health if hasattr(player, "health") else 100,
                "position": [player.rect.x, player.rect.y] if hasattr(player, "rect") else [0, 0],
                # Add more player attributes as needed
            },
            "game_state": {
                "current_boss": current_boss_state,
                "bosses_defeated": [],  # List of defeated bosses
                "unlocked_levels": [],  # List of unlocked levels
                # Add more game state data as needed
            },
            "timestamp": str(datetime.datetime.now())
        }
        return save_data

    def save_game(self, player, current_boss_state, slot_number=1):
        """Save the game state to a specific slot"""
        save_data = self.create_save_data(player, current_boss_state)
        
        # Create the save file path
        save_file = os.path.join(self.save_dir, f"save_slot_{slot_number}.json")
        
        try:
            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=4)
            return True, f"Game saved successfully to slot {slot_number}"
        except Exception as e:
            return False, f"Error saving game: {str(e)}"

    def load_game(self, slot_number=1):
        """Load the game state from a specific slot"""
        save_file = os.path.join(self.save_dir, f"save_slot_{slot_number}.json")
        
        try:
            if not os.path.exists(save_file):
                return False, "No save file found", None
            
            with open(save_file, 'r') as f:
                save_data = json.load(f)
            return True, "Game loaded successfully", save_data
        except Exception as e:
            return False, f"Error loading game: {str(e)}", None

    def list_saves(self):
        """List all available save files with their timestamps"""
        saves = []
        for file in os.listdir(self.save_dir):
            if file.startswith("save_slot_") and file.endswith(".json"):
                try:
                    with open(os.path.join(self.save_dir, file), 'r') as f:
                        save_data = json.load(f)
                        slot_number = int(file.split('_')[2].split('.')[0])
                        saves.append({
                            "slot": slot_number,
                            "timestamp": save_data["timestamp"],
                            "filepath": os.path.join(self.save_dir, file)
                        })
                except:
                    continue
        return sorted(saves, key=lambda x: x["slot"])

    def delete_save(self, slot_number):
        """Delete a save file"""
        save_file = os.path.join(self.save_dir, f"save_slot_{slot_number}.json")
        try:
            if os.path.exists(save_file):
                os.remove(save_file)
                return True, f"Save slot {slot_number} deleted successfully"
            return False, "Save file not found"
        except Exception as e:
            return False, f"Error deleting save: {str(e)}"