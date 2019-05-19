import os
from shutil import copyfile

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if f.startswith("app"):
        print(f)
        contract_name = f.split(".")[0] + "ContractCode.html"
        web3_name = f.split(".")[0] + "Web3Code.html"
        print(contract_name)
        print(web3_name)
        copyfile(f, contract_name)
        copyfile(f, web3_name)
