# Snipey the SnipeIT Commander

Snipey is a command-line tool to interact with the Snipe-IT asset management system. It provides functionalities for checking in, checking out, viewing the status, and watching the live status of assets.

## Features

- Show the status of all assets
- Check in an asset
- Check out an asset
- Watch for changes in asset status

## Pre-requisites 

- Python 3.x
- Snipe-IT API access with a generated access token (API Version v8.2.0)


## Installation

- Clone the repository to your local machine
- Install the required Python packages using pip:
  ```
  pip install -r requirements.txt
  ```
- Create a `.config` file in the root directory of the cloned repository with the following structure:
  ```
  [api]
  url = your_snipeit_api_url
  access_token = your_snipeit_api_token
  ```
- Replace `your_snipeit_api_url` and `your_snipeit_api_token` with your actual Snipe-IT instance's API URL and token.

## Configuration

- To check in and out by asset tag rather than asset id, set *asset_by_tag* to true under *preferences* section in `.config`. Default is false. Example:
  ```
  [preferences]
  asset_by_tag = true
  ```

## Usage

```
python snipey.py [command] [args]
```

### Available Commands

- `watch`: Monitor the status of assets in real-time
- `status`: Show the status of all assets
- `ci <asset_id>`: Check-in an asset
- `co <asset_id>`: Check-out an asset
- `getid <asset_tag>`: Show asset id belonging to asset_tag
- `getid <asset_id>`: Show asset information
- `user`: List all users

### Examples

Show the status of all assets:
```
python snipey.py status
```

Check in an asset:
```
python snipey.py ci 123
```

Check out an asset:
```
python snipey.py co 123
```

Watch for real-time changes in asset status:
```
python snipey.py watch
```

Show asset id belonging to asset_tag:
```
python snipey.py getid ABC0123
```

Show asset information:
```
python snipey.py show 123
```

List all users:
```
python snipey.py users
```

## License

This project is open-source and available under the [MIT License](LICENSE).

