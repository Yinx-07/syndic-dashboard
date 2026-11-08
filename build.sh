#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser automatically if it doesn't exist
python manage.py shell -c "
from core.models import User
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@syndic.ma', 'admin123')
    user.role = 'syndic'
    user.save()
    print('Superuser created!')
else:
    print('Superuser already exists.')
"

# Seed demo data
python manage.py seed_demo_data || echo 'Seed skipped or already done.'
