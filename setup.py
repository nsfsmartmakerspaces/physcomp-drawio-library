from setuptools import setup

setup(name='physcomp_drawio_library',
      version='1.0.0',
      description='Generate Draw.io schematic components for physcomp',
      url='https://github.com/nsfsmartmakerspaces/physcomp-drawio-library',
      author='NSF Smart Maker Spaces',
      packages=['physcomp_drawio_generate'],
      install_requires=[
          'PyYAML==5.4.1',
      ],
      zip_safe=False)
