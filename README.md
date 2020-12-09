# Dekode
A connector for using the Dekode API.

## Prerequisites
python3

## API Capabalities
Supports GET, POST
The POST route uses chaining in SESAM
    - batch size 1.

## How to:

*Run program in development*

This repo uses the file ```package.json``` and [yarn](https://yarnpkg.com/lang/en/) to run the required commands.

1. Make sure you have installed yarn.
2. Creata a file called ```helpers.json``` and set username, token and base_url in the following format:
```
{
    "dekode-password": "some password",
    "dekode-base-url": "some base_url",
    "active_users_base_url": "some potential extra needed base_url"
}
```
3. run:
    ```
        yarn install
    ```
4. execute to run the script:
    ```
        yarn swagger
    ```

*Run program in production*

Make sure the required env variables are defined.

*Use program as a SESAM connector*

#### System config :

```
    {
    "_id": "github",
    "type": "system:microservice",
    "docker": {
        "environment": {
            "dekode_password": "$SECRET(dekode-password)",
            "dekode_base_url": "$ENV(dekode-base-url)",
            "active_users_base_url": "$ENV(active_users_base_url)"
        },
        "image": "sesamcommunity/dekode:latest",
        "port": 5000
    },
    "verify_ssl": true
    }
```

#### Example Pipe config :

```
    {
        "_id": "dekode-users-outbound",
        "type": "pipe",
        "source": {
        "type": "dataset",
        "dataset": "dekode-users-preparation"
        },
        "sink": {
            "type": "json",
            "system": "dekode",
            "url": "/post"
        },
        "transform": {
            "type": "dtl",
            "rules": {
            "default": [
                ["add", "payload", "fancy_payload_goes_here"]
            ]
            }
        }
    }
```

## Routes
```
    /post
    /get_user_id
```