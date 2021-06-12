# Import csv library
import csv

# Models

from cride.circles.models import Circle


def load_circles(file_name):
    try:
        with open(file_name, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Circle.objects.create(**row)
        print('file imported correctly')
    except Exception as ex:
        raise ex
