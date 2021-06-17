import json
import os

class FileLock:
    """
    Handles file and verifies the file operations are executed

    :param file_path The path to the file to be handled
    """

    def __init__(self, file_path):
        self.__file_path = file_path

        self.__monitor = False

        if not os.path.exists(file_path):
            with open(file_path, 'w') as f: # Create a new empty file to prevent another monitor instance from being spun up
                self.__monitor = True # Set the monitor file to be true

    def is_monitor(self):
        """
        Determine if this file is the main monitor file

        :return The status of whether this is the main monitor file
        """

        return self.__monitor

    def __verify(self, func, *args, **kwargs):
        """
        Acts as a wrapper function for the read and write operation which makes sure it works before continuing

        :param func THe function that should be repeted until correct

        :return The result of the executed function
        """

        # Keep doing the operation until it works
        while True:
            try:
                result = func(*args, **kwargs)
                break

            except:
                pass

        return result

    def write(self, data_object):
        """
        Writes the data to the file

        :param data_object The dictionary to be written to the file
        """

        def func():
            # Save to the dump the data to the file
            with open(self.__file_path, 'w', encoding='utf-8') as f:
                json.dump(data_object, f)

        return self.__verify(func)

    def read(self):
        """
        Reads the data from the file

        :return The data in the file
        """

        def func():
            # Read the data from the file
            with open(self.__file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data
        
        return self.__verify(func)

    def __del__(self):
        if os.path.exists(self.__file_path):
            os.remove(self.__file_path)
            print(f"Deleted {self.__file_path}")