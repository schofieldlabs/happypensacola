
# This file contains the service catalog for Happy Pensacola.
# It defines the services offered, their owners, prices, durations, available hours, and booking lead times.

SERVICE_CATALOG = {
    
    # 🏛 Mediation Services
    'mediation-standard': {
        'name': 'Standard Two-Hour Mediation (Two Parties)',
        'owner': 'ralph',
        'price': 50000,  # $500
        'duration': 120,  # minutes
        'hours': range(12, 21),  # This allows limiting availability by service type.
        'days_ahead': 30,
        'buffer_before': 15,  # 15 min buffer for prep
    },
    'mediation-halfday': {
        'name': 'Half-Day Mediation (3-4 Hours)',
        'owner': 'ralph',
        'price': 100000,  # $1,000
        'duration': 240,
        'hours': range(9, 16),  # Full morning/afternoon blocks
        'days_ahead': 30,
        'buffer_before': 30,
    },
    'mediation-fullday': {
        'name': 'Full-Day Mediation (6-8 Hours)',
        'owner': 'ralph',
        'price': 180000,
        'duration': 480,
        'hours': range(8, 12),  # Full day bookings start AM
        'days_ahead': 45,
        'buffer_before': 60,
    },

    # 💍 Wedding Officiant Services
    'wedding-basic': {
        'name': 'Basic Elopement Ceremony (License Signing)',
        'owner': 'ralph',
        'price': 20000,  # $200
        'duration': 30,
        'hours': range(8, 18),  # 8 AM to 5 PM
        'days_ahead': 14,
        'buffer_before': 30,
    },
    'wedding-standard': {
        'name': 'Standard Wedding Ceremony',
        'owner': 'ralph',
        'price': 40000,
        'duration': 60,
        'hours': range(9, 20),  # Morning to evening slots
        'days_ahead': 60,
        'buffer_before': 60,  # Travel and prep time before
    },
    'wedding-premium': {
        'name': 'Premium Wedding Package (Custom + Rehearsal)',
        'owner': 'ralph',
        'price': 75000,
        'duration': 90,
        'hours': range(10, 20),
        'days_ahead': 90,
        'buffer_before': 90,
    },

    # 🧘 Wellness Services
    'wellness-pilates-private': {
        'name': 'Private Pilates / Gyrotonic Session',
        'owner': 'jessica',
        'price': 12000,
        'duration': 50,
        'hours': range(7, 15),
        'days_ahead': 14,
        'buffer_before': 10,
    },
    'wellness-package': {
        'name': '4-Session Pilates Package',
        'owner': 'jessica',
        'price': 40000,
        'duration': 50,
        'hours': range(7, 15),
        'days_ahead': 14,
        'buffer_before': 10,
    },

    # 🎓 LMS Course (Premarital)
    'premarital-online': {
        'name': 'Premarital Counseling Online Course',
        'owner': 'ralph',
        'price': 2499,
        'duration': 240,  # Full 4-hour course, but no live scheduling needed
        'hours': [],
        'days_ahead': 365,
        'buffer_before': 0,
        'self_paced': True,
    },
    'premarital-premium': {
        'name': 'Premarital Course + Private Counseling Session',
        'owner': 'ralph',
        'price': 24900,
        'duration': 60,  # live counseling add-on
        'hours': range(13, 19),  # afternoon/evening hours
        'days_ahead': 30,
        'buffer_before': 30,
    },
}

