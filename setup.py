from distutils.core import setup, Extension

module1 = Extension('spiv2', sources = ['spi_v2.c'])

setup (
    name = 'spiv2',
    author='Jannik Beibl',
    url='',
    download_url='',
    version = '1.0',
    description = 'JetBoard SPI driver for NVIDIA Jetson in Python',
    license='GPL-v2',
    platforms=['Linux'],
    ext_modules = [module1]
)
