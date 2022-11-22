from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    current_date = datetime.datetime.now()

    return {
        'year': current_date.year
    }
