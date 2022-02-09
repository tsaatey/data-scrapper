from datetime import datetime


def convert_date(arg):
    date = datetime.fromisoformat(arg)
    return date.strftime('%d/%m/%Y')
