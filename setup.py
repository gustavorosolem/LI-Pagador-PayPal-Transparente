import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='li-pagador-paypal-transparente',
    version='2.2.3',
    url='https://github.com/lojaintegrada/LI-Pagador-PayPal-Transparente',
    license='MIT',
    description='Meio de pagamento usando o PayPal Plus (https://www.paypal.com)',
    author=u'Loja Integrada',
    author_email='suporte@lojaintegrada.com.br',
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['distribute', 'li-pagador'],
)
