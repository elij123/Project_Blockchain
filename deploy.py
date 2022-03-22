import json
from solcx.main import compile_files
from web3 import Web3
import solcx


with open("./CryptoProject.sol", "r") as file:
    test_file = file.read()

print("Installing...")
solcx.install_solc("0.8.9")

compiled_sol = compile_files(["CryptoProject.sol"], output_values=["metadata", "bin"])

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["CryptoProject.sol:CryptoProject"]["bin"]

abi = json.loads(compiled_sol["CryptoProject.sol:CryptoProject"]["metadata"])["output"][
    "abi"
]

w3 = Web3(Web3.HTTPProvider("http://192.168.0.212:8545"))
chain_id = 21090
my_address = "0x0C2575f023d9059596B6941f085fE71fE2b649dd"
with open(
    "../Ethereum Blockchain/data/keystore/UTC--2021-11-08T15-46-29.386813000Z--0c2575f023d9059596b6941f085fe71fe2b649dd"
) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, "Hj8BrLoXgPys")

CryptoProject = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(my_address)
print(w3.eth.gas_price)
transaction = CryptoProject.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "gasPrice": w3.eth.gas_price,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying Contract!")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")
print(f"ABI:{abi}")
