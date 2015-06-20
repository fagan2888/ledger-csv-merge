from setuptools import setup

setup(

    name='ledger-csv-merge',

    version='0.0.1',

    install_requires=[
        'pyparsing',
        'click',
        'watchdog',
    ],

    entry_points={
        'console_scripts': [
            'ledger-csv-merge=ledger_csv_merge:main',
        ],
    }
)
