from nanorpc.client import NanoRpc, NodeVersion
import os

RPC_URL = os.getenv("RPC_URL")
AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")
NODE_VERSION = NodeVersion.V25_0


def get_nanorpc_client(rpc_url=None, auth_username=None, auth_password=None, node_version=None):
    # Set the environment variables if they don't exist and parameters are provided
    rpc_url = rpc_url or RPC_URL
    auth_username = auth_username or AUTH_USERNAME
    auth_password = auth_password or AUTH_PASSWORD
    node_version = node_version or NODE_VERSION

    # Initialize and return the NanoRpc client
    return NanoRpc(url=rpc_url,
                   username=auth_username,
                   password=auth_password,
                   node_version=node_version)


# Create a single instance of NanoRpc client
nanorpc = get_nanorpc_client()
