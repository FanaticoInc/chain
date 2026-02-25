import os
import sys
import anthropic

def get_api_key():
    """Fetches the Anthropic API key from environment variables."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)
    return api_key

def analyze_configuration(config_content):
    """Sends configuration content to Claude for analysis."""
    api_key = get_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    try:
        print("Sending configuration to Claude for analysis...")
        message = client.messages.create(
            model="claude-3-opus-20240229", # Or claude-3-sonnet, claude-3-haiku
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a helpful AI assistant specialized in system configurations.
                    Please analyze the following configuration content and provide feedback for developers
                    to consider for manual deployment. Focus on potential issues, improvements, or security concerns.

                    Configuration Content:
                    ---
                    {config_content}
                    ---

                    Provide your analysis:
                    """
                }
            ]
        ).content[0].text

        print("\nClaude's Analysis:")
        print("--------------------")
        print(message)
        print("--------------------")

    except anthropic.APIConnectionError as e:
        print(f"Claude API Connection Error: {e.__cause__}")
    except anthropic.RateLimitError as e:
        print(f"Claude API Rate Limit Error: {e.response.status_code}")
    except anthropic.APIStatusError as e:
        print(f"Claude API Status Error: {e.status_code} - {e.response}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_config.py <path_to_config_file>")
        sys.exit(1)

    config_file_path = sys.argv[1]

    try:
        with open(config_file_path, 'r') as f:
            configuration_data = f.read()
        analyze_configuration(configuration_data)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
