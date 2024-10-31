import subprocess

# Required packages
required_packages = [
    'google-auth-oauthlib',
    'google-api-python-client',
    'tkcalendar',
    'matplotlib',
    'Pillow'
]

# Install each package using pip
for package in required_packages:
    subprocess.run(['pip', 'install', package])

# Once all packages are installed, notify the user
print("All required packages have been successfully installed.")
