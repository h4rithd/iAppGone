from setuptools import setup, find_packages

setup(
    name='iAppGone',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'iappgone = iappgone.__main__:main',
        ],
    },
    install_requires=[
        'pandas',
        'tabulate',
        'colorama',
    ],
    author='Harith Dilshan (h4rithd)',
    author_email='info@h4rithd.com',
    url='https://github.com/h4rithd/iAppGone',
    download_url='https://github.com/h4rithd/iAppGone/archive/refs/tags/v0.1.tar.gz',
    description='Fully Functional Uninstaller for Mac OS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=['uninstaller', 'macos', 'applications'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/h4rithd/iAppGone/issues',
        'Source': 'https://github.com/h4rithd/iAppGone',
    },
)

