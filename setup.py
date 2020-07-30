from setuptools import setup, find_packages

setup(
   name='valuation',
   version='0.1.0',
   description='Simple Valuation Module',
   author='Jairo Alves',
   author_email='jairo.luciano@gmail.com',
   packages=find_packages("valuation"),
   install_requires=['pandas', 'numpy', 'matplotlib', 'seaborn', 'IPython'],
)
