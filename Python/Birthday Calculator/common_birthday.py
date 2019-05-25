"""
This script is supposed to calculate the date when more people have
"common birthday" - when their ages combined will reach a certain
milestone.

Example: One person was born in 1990, the second one in 2000.
         In the year 2020 they will celebrate 50th birthday together.
         (One will be 30, second one 20. 30 + 20 = 50).

Input in the array of birthdays is in format "DAY. MONTH. YEAR".
The jubileum can be either integer or double, it accounts for that.

NOTE: We are not being completely precise in the calculation of the
      exact date. We do not use any external libraries to handle dates
      (like datetime or dateutil), and all our months have 30.5 days.
      To simplify the code, we also assume that all the people are already
      alive when the chosen birthday is to be determined - in opposite case
      there will be a small mistake in the result date.

Logic overview: We first calculate the right year by taking only the birth-years
    of each person (assuming they were born 1st January). Then we sum up all the
    days differences between 1st January and the born-dates of all the people.
    In the end we will divide this sum by the amount of people, and it will give
    us the amount of days from the beginning of the year, when these people will
    have "common birthday". Then we just parse it and display the result.
"""

# Changeable input
COMMON_BIRTHDAY = 100
BIRTHDAYS_ARRAY = ["27. 1. 1995", "2. 8. 1993", "23. 7. 1969"]

# The main part of the script
def main():
    # Finding the amount of people
    people_amount = len(BIRTHDAYS_ARRAY)

    # Preparing the lists to store all years, months and days each
    # BEWARE: years = months = days = [] canot be done - it takes everything as one array
    birth_years_array = []
    birth_months_array = []
    birth_days_array = []

    # Extracting days, months and years from the array
    # If it cannot be done, user probably used a bad date format in the array
    try:
        for birth_date in BIRTHDAYS_ARRAY:
            birth_days_array.append(int(birth_date.split(".")[0].strip()))
            birth_months_array.append(int(birth_date.split(".")[1].strip()))
            birth_years_array.append(int(birth_date.split(".")[2].strip()))
    except IndexError:
        print("ERROR: Make sure all the dates are in format 'DAY. MONTH. YEAR'!")
        return

    # Sorting the birth-year values to find out the oldest date
    birth_years_array.sort()

    # Assigning the oldest date as a first year in the loop
    loop_current_year = birth_years_array[0]

    # Variable to store the combined age in the loop
    # It is a increment-list, the current value is always the last one
    #   (with the index -1)
    loop_combined_age = [0]

    # Helper variable being a stopper in a loop to easily recognise when
    #   the loop should end (more readable way of "break" statements)
    loop_keep_going = True

    # Running through the years forward in a loop, each year incrementing
    #   one year for each person that was already alive that year.
    # Stop iterating when the combined age will be higher than the chosen
    #   anniversary. Then we know the common birthday is probably in the previous year.
    while loop_keep_going:
        loop_current_year += 1
        amount_of_alive_people = 0
        # Looping through the array of birth-years and for each birth-year
        #   that is smaller than the current year incrementing the combined age
        #   by one year - because that person was already alive.
        for birth_year in birth_years_array:
            if birth_year < loop_current_year:
                amount_of_alive_people += 1
            # Appending always the last count incremented by the people who
            #   are now 1 year older.
        loop_combined_age.append(loop_combined_age[-1] + amount_of_alive_people)

        if loop_combined_age[-1] > COMMON_BIRTHDAY:
            loop_keep_going = False

    # Because in current year the combined_age is already bigger than we want,
    #   the most probable year will be chosen as the previous one.
    birthday_year = loop_current_year - 1

    # Taking the difference between our chosen birthday and the last combined-age
    #   that was less than this number. Then multiplying it by 365 to get the
    #   amount of days we need to add to reach the real birthday date.
    extra_days = (COMMON_BIRTHDAY - loop_combined_age[-2]) * 365.25

    # Finding out the number of months and days of all the people
    count_of_months = 0
    count_of_days = 0

    for month_count in birth_months_array:
        count_of_months += (month_count - 1)

    for day_count in birth_days_array:
        count_of_days += day_count

    # Summing up all the months and days
    days_altogether_from_bday = count_of_months * 30.5 + count_of_days

    # Getting the amount of days that should be added on top of the
    #   1st January of the birthday_year that was chosen
    days_to_be_added = (days_altogether_from_bday + extra_days) / people_amount

    # Until days_to_be_added are smaller than a year, transfer
    #   every 365 days into a year, to allow for date parsing
    while int(days_to_be_added / 365.25) > 0:
        days_to_be_added -= 365.25
        birthday_year += 1

    # Parsing the resulting month and day
    birthday_month = int(days_to_be_added / 30.5) + 1
    birthday_day = int(days_to_be_added % 30.5) + 1

    # Printing the result:
    print("These {} people have {} years together on the {}. {}. {}. Happy birthday!"
         .format(people_amount, COMMON_BIRTHDAY, birthday_day, birthday_month, birthday_year))

# Helper function to quickly print out the value of a variable
# I did not find a way to omit the variable_name, and print the variable
#   name as a string without it
def _printvar(variable, variable_name="variable_name"):
    print("{}: {}".format(variable_name, variable))


if __name__ == '__main__':
    main()
