from setuptools import setup

setup(
   name='valuation',
   version='1.0',
   description='Simple Valuation Module',
   author='Jairo Alves',
   author_email='jairo.luciano@gmail.com',
   packages=['valuation'],  #same as name
   install_requires=['pandas', 'numpy', 'matplotlib.pyplot', 'seaborn', 'IPython.core.display'], #external packages as dependencies
)
