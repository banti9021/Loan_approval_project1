from solcx import compile_standard, install_solc
from web3 import Web3
import json, os
from dotenv import load_dotenv

load_dotenv()

# Install Solidity compiler version
install_solc('0.8.17')

# Read the contract
with open("../contract/loanaudit.sol", "r") as f:
    source = f.read()

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {"LoanAudit.sol": {"content": source}},
    "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
}, solc_version="0.8.17")

# Extract bytecode & ABI
bytecode = compiled_sol["contracts"]["LoanAudit.sol"]["LoanAudit"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["LoanAudit.sol"]["LoanAudit"]["abi"]

# Connect to Ganache GUI
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER")))
acct = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
chain_id = int(os.getenv("CHAIN_ID"))

# Deploy contract
LoanAudit = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(acct.address)

tx = LoanAudit.constructor().build_transaction({
    "from": acct.address,
    "nonce": nonce,
    "gas": 5000000,
    "gasPrice": w3.to_wei('20', 'gwei'),
    "chainId": chain_id
})

signed_tx = acct.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract deployed at address:", tx_receipt.contractAddress)

# Save ABI and Address for future use
with open("contract_abi.json", "w") as f:
    json.dump(abi, f)
with open("contract_addr.txt", "w") as f:
    f.write(tx_receipt.contractAddress)
