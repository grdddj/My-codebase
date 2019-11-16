# Clipboard hacks
Are you already tired from copy-pasting loads of smaller text information from one location to the other? Why not just copying, and let all the processing and pasting to be done by the slave (computer)!

This project is focusing on increasing the speed and productivity of copy-pasting. Python is constantly monitoring the content of a clipboard, and when it finds a new value there, it will do what it is instructed to do (and you can really do whatever you want with it).

I found very big time and effort saver in transferring text information from PDF somewhere else. Reason being PDF documents are structured into rows, and if you want to copy text spanning multiple rows, there will be a newline at the end of each row, that needs getting rid of. I employed Python to do this processing, and also saving the content into a file for me, so I can completely focus on the content itself.

Usage: Run the script, and then just highlight desirable text, press CTRL+C and the text will be formatted and saved into a file. As a bonus, this formatted text will be stored in clipboard, ready to be pasted in case it is needed.

Other interesting use-cases:
- real-time translation of the text in clipboard (copy Czech, paste English)
- keeping track of all the values in clipboard (for personal or spying purposes)
