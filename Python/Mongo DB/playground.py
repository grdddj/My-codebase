from datetime import datetime

# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case
print(datetime.now().strftime('%Y-%m-%d'))
