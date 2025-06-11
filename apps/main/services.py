SERVICE_CATALOG = {
    'mediation': {
        'name': 'Mediation Session',
        'owner': 'ralph',
        'price': 20000,  # $200
        'duration': 60,  # minutes
        'hours': range(9, 17),  # 9AM to 4PM start
        'days_ahead': 30
    },
    'wedding-officiant': {
        'name': 'Wedding Officiant',
        'owner': 'ralph',
        'price': 30000,  # $300
        'duration': 90,
        'hours': range(10, 18),  # 10AM to 5PM start
        'days_ahead': 90
    },
    'arbitration': {
        'name': 'Arbitration Session',
        'owner': 'ralph',
        'price': 25000,  # $250
        'duration': 120,
        'hours': range(9, 15),  # 9AM to 2PM start
        'days_ahead': 60
    },
    'wellness': {
        'name': 'Pilates / Gyrotonic Session',
        'owner': 'jessica',
        'price': 12000,  # $120
        'duration': 50,
        'hours': range(7, 15),  # 7AM to 2PM start
        'days_ahead': 14
    }
}
