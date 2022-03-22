import typer
from tabulate import tabulate
from web3 import Web3, contract
from web3.middleware import geth_poa
import socket
import re, uuid
from hexbytes import HexBytes
import pickle

full_mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
half_mac_server = full_mac_address[9:]

http_address = input("Enter the HTTP address of Geth node")
http_url = f"http://{http_address}:8545"

w3 = Web3(Web3.HTTPProvider(http_url))
if w3.isConnected() == False:
    exit(1)
w3.middleware_onion.inject(geth_poa.geth_poa_middleware, layer=0)

contract_address = Web3.toChecksumAddress("0xE9c9A012CFb1C870876Cc0b2938C142CC192E8DB")
contract_abi = [
    {
        "inputs": [],
        "name": "flag",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_M_ID", "type": "string"},
            {"internalType": "string", "name": "_D_ID", "type": "string"},
            {"internalType": "address", "name": "_D_addr", "type": "address"},
        ],
        "name": "setValueDevice",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_M_addr", "type": "address"},
            {"internalType": "string", "name": "_M_ID", "type": "string"},
        ],
        "name": "setValueMiner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "status_check",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
            {"internalType": "address", "name": "account", "type": "address"},
        ],
        "name": "verify",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

myContract = w3.eth.contract(address=contract_address, abi=contract_abi)

device_id_candidate = half_mac_server
device_address = "0xf031cb0b6c6C01c2eac9c63964249a46BE5EB275"
nonce = w3.eth.getTransactionCount(device_address)
hb_temp = HexBytes("7634f15d8280ee2efddee38b4f46375dcbd568cf967b7784e66b7bdf88cf632a")
private_key = bytes(hb_temp)

HOST = http_address
PORT = 7000

message1 = {
    "Status": "REQUESTING TOKEN",
    "Payload1": {"D_ID": device_id_candidate, "D_addr": device_address},
    "Payload2": None,
}
message1 = pickle.dumps(message1)


def send_token_request():
    auth_token = b""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(message1)
        auth_token = s.recv(1024)
        s.close()
        return auth_token


auth_token_temp = send_token_request()
auth_token_temp = pickle.loads(auth_token_temp)
token = bytes(
    Web3.solidityKeccak(
        ["bytes", "bytes", "address"],
        [
            bytes(auth_token_temp[0], "utf-8"),
            bytes(device_id_candidate, "utf-8"),
            Web3.toChecksumAddress(device_address),
        ],
    )
)
tx_hash = myContract.functions.verify(
    token,
    auth_token_temp[2],
    Web3.toChecksumAddress(auth_token_temp[1]),
).buildTransaction(
    {
        "chainId": 21090,
        "from": device_address,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(tx_hash, private_key=private_key)
wait_txn = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(wait_txn)
print(tx_receipt)

status = myContract.functions.status_check().call()
print(status)

# message2 = {"Status": "SENDING TOKEN", "Payload1": None, "Payload2": auth_token_temp}
# message2 = pickle.dumps(message2)


# def sending_token():
#     res = b""
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))
#         s.sendall(message2)
#         res = s.recv(1024)
#         s.close()
#         return res


# print(sending_token())


# Send a message
# Receiver_device = input(
#    "Specify the receiver device"
# )  Display a list of devices using tabulate
# message = input("Describe a message")
# Send the message with the token.


# TODO
# Get data and error messages from smart contract
# Fix the transaction format
# add typer commands
