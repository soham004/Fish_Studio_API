import os
import json

def prompt_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")

def main():
    print("=== Fish Studio Account Setup ===")
    accounts_dir = "accounts"
    if not os.path.exists(accounts_dir):
        os.makedirs(accounts_dir)
        print(f"Created accounts directory: {accounts_dir}")

    # Ask for account name
    while True:
        account_name = input("Enter a name for this account (no spaces): ").strip()
        if not account_name:
            print("Account name cannot be empty.")
            continue
        if " " in account_name:
            print("Account name cannot contain spaces.")
            continue
        account_path = os.path.join(accounts_dir, account_name)
        if os.path.exists(account_path):
            print("An account with this name already exists. Please choose another name.")
            continue
        break

    os.makedirs(account_path)
    print(f"Created account folder: {account_path}")

    # Create inputFiles folder
    input_files_path = os.path.join(account_path, "inputFiles")
    os.makedirs(input_files_path)
    print(f"Created inputFiles folder: {input_files_path}")

    # Prompt for config fields
    print("\nPlease enter the following account details:")
    email = prompt_nonempty("Email: ")
    password = prompt_nonempty("Password: ")
    voice_name = prompt_nonempty("Voice Name: ")
    char_limit = None
    while True:
        char_limit = input("Character limit per chunk (e.g. 2000): ").strip()
        if char_limit.isdigit() and int(char_limit) > 0:
            char_limit = int(char_limit)
            break
        print("Please enter a positive integer.")

    # Optionally, allow user to paste a BearerToken if they have one
    bearer_token = input("BearerToken (leave blank if unknown): ").strip()

    config = {
        "Email": email,
        "Password": password,
        "Voice_Name": voice_name,
        "characterLimitPerChunk": char_limit
    }
    if bearer_token:
        config["BearerToken"] = bearer_token
    else:
        config["BearerToken"] = ""

    config_path = os.path.join(account_path, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    print(f"Created config file: {config_path}")

    print("\nAccount setup complete!")
    print(f"You can now add .txt files to {input_files_path} and use this account in the main script.")

if __name__ == "__main__":
    main()