from setuptools import find_packages, setup
import waitress

setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', 'waitress', 'python-dotenv', 'mysql-connector-python', 'pandas',
    ],
)