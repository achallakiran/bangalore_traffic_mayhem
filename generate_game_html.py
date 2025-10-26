import json
import os

def generate_html_file(template_filepath, config_filepath, output_filepath):
    """
    Reads a JSON config, extracts enemySpawnData, and replaces the
    <varEnemySpawn> placeholder in the HTML template with the formatted data,
    then writes the result to a new HTML file.
    """
    
    # 1. Load the Configuration Data
    try:
        with open(config_filepath, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_filepath}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {config_filepath}")
        return

    # Extract the necessary data field
    enemy_spawn_data = config_data.get("enemySpawnData")
    if enemy_spawn_data is None:
        print("Error: 'enemySpawnData' field not found in the config file.")
        return

    # 2. Convert the Python list to a JavaScript array string
    # We use json.dumps() to ensure the output is valid JSON (which is valid JS array syntax)
    # We use '    ' as indent for readability in the final HTML file
    data_as_js_string = json.dumps(enemy_spawn_data, indent=4)

    # 3. Load the HTML Template
    try:
        with open(template_filepath, 'r') as f:
            html_template = f.read()
    except FileNotFoundError:
        print(f"Error: HTML template file not found at {template_filepath}")
        return

    # 4. Perform the text replacement
    placeholder = "<varEnemySpawn>"
    if placeholder not in html_template:
        print(f"Warning: Placeholder '{placeholder}' not found in the HTML template. HTML file generated without replacement.")
    
    final_html = html_template.replace(placeholder, data_as_js_string)

    # 5. Write the final HTML file
    try:
        with open(output_filepath, 'w') as f:
            f.write(final_html)
        print(f"Success: HTML content generated and saved to {output_filepath}")
    except IOError as e:
        print(f"Error writing output file: {e}")

# --- Execution ---

# Define the file paths based on the files you provided
HTML_TEMPLATE_FILE = 'html_template.txt' 
GAME_CONFIG_FILE = 'game_config.json'
OUTPUT_HTML_FILE = 'output_game.html'

# Assuming all files are in the current working directory for simplicity
if __name__ == "__main__":
    generate_html_file(HTML_TEMPLATE_FILE, GAME_CONFIG_FILE, OUTPUT_HTML_FILE)
