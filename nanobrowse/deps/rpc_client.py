from nanorpc.client import NanoRpc, NodeVersion
import os

RPC_URL = os.getenv("RPC_URL")
AUTH_USERNAME = os.getenv("AUTH_USERNAME")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD")

# Single instance of NanoRpc client
nanorpc = NanoRpc(url=RPC_URL, username=AUTH_USERNAME,
                  password=AUTH_PASSWORD, node_version=NodeVersion.V25_0)
