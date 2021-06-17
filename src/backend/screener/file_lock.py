import json

class FileLock:
    """
    Handles file operations and locks file from being read when it is being written to

    :param file_path The path to the file to be handled
    """

    def __init__(self, file_path):
        self.__file_path = file_path
        self.__file_lock = [False] # Prevents read operation when write operation is happening

    def __wait(self, func, *args, **kwargs):
        """
        Acts as a wrapper function for the read and write which locks the file whenever an operation is being performed then unlocks the file and returns the result

        :param func THe function that should lock the file when called

        :return The result of the executed function
        """

        # Wait for the file to be unlocked
        while self.__file_lock[0]:
            pass

        self.__file_lock[0] = True

        # result = func(*args, **kwargs) # This is the alternative
        # Keep doing the operation until it works
        while True:
            try:
                result = func(*args, **kwargs)
                break

            except:
                pass

        self.__file_lock[0] = False

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

        return self.__wait(func)

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
        
        return self.__wait(func)