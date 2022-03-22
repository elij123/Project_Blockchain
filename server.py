import types

# from getpass import getpass
# import typer
# from tabulate import tabulate
from web3 import Web3
import web3
from web3.middleware import geth_poa
import socket
import selectors
import re, uuid
import pickle
from hexbytes import HexBytes

# from brownie import *

full_mac_address = ":".join(re.findall("..", "%012x" % uuid.getnode()))
half_mac_server = full_mac_address[9:]

sel = selectors.DefaultSelector()

sol_verify_mapping = {}
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

with open(
    "../Ethereum Blockchain/data/keystore/UTC--2021-11-08T15-46-29.386813000Z--0c2575f023d9059596b6941f085fe71fe2b649dd"
) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, "Hj8BrLoXgPys")

temp1_id = half_mac_server
temp2_addrpuk = "0x0C2575f023d9059596B6941f085fE71fE2b649dd"
nonce = w3.eth.getTransactionCount(temp2_addrpuk)
tx_hash = myContract.functions.setValueMiner(temp2_addrpuk, temp1_id).buildTransaction(
    {
        "chainId": 21090,
        "from": temp2_addrpuk,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(tx_hash, private_key=private_key)
wait_txn = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(wait_txn)
print(tx_receipt)
miner_id_candidate = temp1_id
miner_address = temp2_addrpuk


def device_tuple_registration(M_ID, D_ID, D_addr):
    nonce = w3.eth.getTransactionCount(miner_address)
    tx_hash = myContract.functions.setValueDevice(
        M_ID, D_ID, Web3.toChecksumAddress(D_addr)
    ).buildTransaction(
        {
            "chainId": 21090,
            "from": temp2_addrpuk,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(tx_hash, private_key=private_key)
    wait_txn = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(wait_txn)
    token = bytes(
        Web3.solidityKeccak(
            ["bytes", "bytes", "address"],
            [
                bytes(M_ID, "utf-8"),
                bytes(D_ID, "utf-8"),
                Web3.toChecksumAddress(D_addr),
            ],
        )
    )
    signed_token = bytes(w3.eth.sign(Web3.toChecksumAddress(miner_address), data=token))
    sol_verify_mapping[signed_token] = {"Token": token, "isActive": True}
    result_token = [M_ID, miner_address, signed_token]
    result_token = pickle.dumps(result_token)
    return result_token


HOST = http_address
PORT = 7000


# def sol_verify(sig_token):
#     test_check = myContract.functions.verify(
#         sol_verify_mapping[sig_token]["Token"],
#         sig_token,
#         Web3.toChecksumAddress(miner_address),
#     ).
#     test_check2 = sol_verify_mapping[sig_token]["isActive"]
#     if test_check and test_check2:
#         return True
#     else:
#         return False


def convert_bytes_to_message(bytes_message):
    string_from_bytes_message = pickle.loads(bytes_message)
    return string_from_bytes_message


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        print(recv_data)
        if recv_data:
            message_result = convert_bytes_to_message(recv_data)
            if message_result["Status"] == "REQUESTING TOKEN":
                data.outb = device_tuple_registration(
                    miner_id_candidate,
                    message_result["Payload1"]["D_ID"],
                    message_result["Payload1"]["D_addr"],
                )
                print(data.outb)
                print("Done!!!")

            # elif message_result["Status"] == "SENDING TOKEN":
            #     if sol_verify(message_result["Payload2"]):
            #         data.outb = bytes("Verified", "utf-8")
            #     else:
            #         data.outb = bytes("Not Verified", "utf-8")

        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print("listening on", (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
