# nanoBrowse: A Simple Nano Network Block Explorer


[nanoBrowse](https://nanobrowse.com) is a lightweight, easy-to-use block explorer for the Nano cryptocurrency network. 
Simplistic UI. Unique overview of sends and matching receives.


## Installation & Setup

Self hosting nanoBrowse:
- Clone this repository.
- Navigate to the project root and create a `.env` file. Populate it with the necessary RPC configurations:
```
RPC_URL=your_rpc_url_here
AUTH_USERNAME=your_rpc_username_here
AUTH_PASSWORD=your_rpc_password_here
NANO_TO_AUTH_KEY=optional access key for rpc.nano.to
```

Fire it up
```
docker-compose up -d
```

### Rpc commands in use
The following rpc commands are required to run the block explorer :
```
account_info
account_history
account_weight
blocks_info
confirmation_history
confirmation_quorum
delegators
receivable
representatives_online
telemetry
```


## Features

**Search by Account or Block Hash**: Just type in a Nano account starting with `xrb_` or `nano_`, or input a block hash (64 characters long), and dive right into the data.
**Detailed Views**: Get comprehensive details on specific blocks or account data.
**Responsive UI**: Built with TailwindCSS, the UI is clean and works great on both desktop and mobile browsers.

## Contribution
Feel free to fork this project, make improvements, and create pull requests. We appreciate any contribution to make `nanoBrowse` even better!

Copy the above and paste it directly into your README.md. Remember to replace placeholders like your_rpc_url_here with actual data if needed.
