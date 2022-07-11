import os

from src.app import RayaApplication
from raya.entry_point import entry_point


def main():
    app_path = os.path.dirname(os.path.realpath(__file__))
    entry_point(app_path, RayaApplication)


if __name__ == "__main__":
    main()
