"""
Settings package for family_app.
Automatically loads the appropriate settings based on environment.
"""

import os

# Determine which settings to use
ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'development':
    from .development import *
else:
    from .development import *  # Default to development
