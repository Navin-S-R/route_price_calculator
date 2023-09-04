from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in route_price_calculator/__init__.py
from route_price_calculator import __version__ as version

setup(
	name="route_price_calculator",
	version=version,
	description="Caluculate Minimum Travel Expense",
	author="Aerele",
	author_email="hello@aerele.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
