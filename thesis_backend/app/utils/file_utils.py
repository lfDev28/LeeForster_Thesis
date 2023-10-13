import os


def find_latest_file(path):
    most_recent_file = None
    most_recent_time = 0
    for entry in os.scandir(path):
        if entry.is_file():
            # get the modification time of the file using entry.stat().st_mtime_ns
            mod_time = entry.stat().st_mtime_ns
            if mod_time > most_recent_time:
                # update the most recent file and its modification time
                most_recent_file = entry.name
                most_recent_time = mod_time

    print(most_recent_file)
    return most_recent_file
