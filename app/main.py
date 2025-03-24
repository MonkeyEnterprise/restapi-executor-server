##
# Copyright (c) 2025, Lorenzo Pouw.
# All rights reserved.
##

from server import App

app = App().flask

if __name__ == "__main__":
    App().run()