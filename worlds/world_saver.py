"""
Class to handle saving and loading world properties.
"""

import os
import pickle


class WorldSaver:
    def save_world_properties(self, properties: dict, path: str) -> None:
        """Save the world properties to a pickle file.

        Args:
            properties (dict): The properties to save.
            path (str): The file path to save the world properties.
        """
        # Ensure the directory exists
        save_dir = os.path.join(".", "saved", "worlds")
        os.makedirs(save_dir, exist_ok=True)

        # Combine the directory with the provided path
        full_path = os.path.join(save_dir, path)

        # Save the properties directly using pickle
        with open(full_path, "wb") as f:
            pickle.dump(properties, f)

    def load_world_properties(self, path: str, additional_properties_keys: set) -> dict:
        """Load the world properties from a pickle file.

        Args:
            path (str): The file path to load the world properties from.
            additional_properties_keys: Keys of additional properties to load.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            KeyError: If the loaded file is missing required properties.
        """
        # Construct the full path
        full_path = os.path.join(".", "saved", "worlds", path)

        # Load the properties directly using pickle
        with open(full_path, "rb") as f:
            properties = pickle.load(f)

        # Get additional properties
        additional_properties = {
            key: properties[key] for key in additional_properties_keys
        }

        return {
            "minimum_actions": properties["minimum_actions"],
            "possible_states": properties["possible_states"],
            "min_action_transformation_matrix": properties[
                "min_action_transformation_matrix"
            ],
            **additional_properties,
        }
