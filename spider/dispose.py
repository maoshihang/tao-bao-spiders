import os


class TaoBaoException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Image(object):

    @staticmethod
    def save_(path, response):
        """

        :param path:
        :param response:
        :return:
        """
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

    @staticmethod
    def open_(path):
        """

        :param path:
        :return:
        """
        if os.name == "nt":
            a = os.system('start ' + path)  # for Windows
            print(a)
        else:
            if os.uname()[0] == "Linux":
                if "deepin" in os.uname()[2]:
                    os.system("deepin-image-viewer " + path)  # for deepin
                else:
                    os.system("eog " + path)  # for Linux
            else:
                os.system("open " + path)  # for Mac

    @staticmethod
    def remove(path):
        os.remove(path)
