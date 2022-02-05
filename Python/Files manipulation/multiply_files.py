import os
from shutil import copyfile

# # For each file which starts with "app" create two copies and append
# #   certain string to its name
# files = [f for f in os.listdir('.') if os.path.isfile(f)]
# for f in files:
#     if f.startswith("app"):
#         print(f)
#         contract_name = f.split(".")[0] + "ContractCode.html"
#         web3_name = f.split(".")[0] + "Web3Code.html"
#         print(contract_name)
#         print(web3_name)
#         copyfile(f, contract_name)
#         copyfile(f, web3_name)

# # For each file which starts with "app" create two empty files
# #   with the same name and .txt and .js extensions (if they do not already exist)
# files = [f for f in os.listdir('.') if os.path.isfile(f)]
# for f in files:
#     if f.startswith("app"):
#         filename = f.split(".")[0]
#         txt_filename = filename + ".txt"
#         js_filename = filename + ".js"
#         if txt_filename not in os.listdir('.'):
#             print(txt_filename)
#             with open(txt_filename, "w"):
#                 pass
#         if js_filename not in os.listdir('.'):
#             print(js_filename)
#             with open(js_filename, "w"):
#                 pass

# Transforming all the files with .txt extension into .sol extension
files = [f for f in os.listdir(".") if os.path.isfile(f)]
for f in files:
    filename, file_extension = os.path.splitext(f)
    if file_extension == ".txt":
        new_filename = filename + ".sol"
        os.remove(f)
        if new_filename not in os.listdir("."):
            with open(new_filename, "w"):
                pass
