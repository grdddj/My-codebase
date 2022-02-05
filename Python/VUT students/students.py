"""
This script is making a statistic of current VUT students, according to their
ID number. The list of valid student ids is saved into CSV file.
"""

import time
from csv import writer

import requests

from bs4 import BeautifulSoup

prefix = "https://www.vutbr.cz/l/"

amount = 0

start_id = "170000"
end_id = "171000"

id_array = []

# We will be measuring the time it takes to fetch all the ids
start = time.time()

# Loop through all the ids and deciding their student status
for id in range(int(start_id), int(end_id)):
    try:
        link = prefix + str(id)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")

        try:
            # If id is a student, the page will contain "alert-success" class
            info = soup.find(class_="alert-success")
            if info is not None:
                amount += 1
                id_array.append(id)
        except:
            pass
    except Exception as e:
        print(f"Some problems occurred while processing {id}: {e}")

    # Printing semi-results every 10 id's
    if id % 10 == 0:
        print(f"{id} has so far {amount}")

end = time.time()

difference = str(round(end - start))

result = f"In the range from {start_id} to {end_id} we have found {amount} students. It took {difference} seconds"

# Printing the result to the terminal
print("-" * 50)
print(result)
print("-" * 50)

# Saving the result as an CSV file
file_name = f"StudentsOfVUT({start_id}-{end_id}).csv"
with open(file_name, "w") as csv_file:
    csv_writer = writer(csv_file)
    headers = ["ID"]
    csv_writer.writerow(headers)

    for id in id_array:
        csv_writer.writerow([id])
