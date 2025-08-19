import os
import django
import sys
from django.core.management import call_command
from io import open

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_interview.settings')
django.setup()

output_path = 'interview_app/fixtures/initial_data.json'

print(f"Starting to dump data to '{output_path}'...")

try:
    with open(output_path, 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata',
            'interview_app',
            format='json',
            indent=2,
            stdout=f
        )
    print(f"✅ Successfully created data fixture at '{output_path}'")

except Exception as e:
    print(f"❌ An error occurred: {e}")