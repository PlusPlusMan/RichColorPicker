from setuptools import setup, find_packages

setup(
    name='rcp-colors',
    version='0.113',
    packages=find_packages(),
    description='A Rich Color Picker app',
    long_description='Terminal based rich color picker app. Type rcp-colors in your terminal to start.',
    long_description_content_type='text/markdown',
    url='https://github.com/PlusPlusMan/rcp',
    author='PlusPlusMan',
    author_email='contact@plusplusman.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='color picker, terminal app rgb hsl hex colors',
    python_requires='>=3.6, <4',
    install_requires=[
        'textual',
        'appdirs',
    ],
    entry_points={
        'console_scripts': [
            'rcp-colors=rcp_colors.rcp:main',
        ],
    },
    project_urls={
        'Source': 'https://github.com/PlusPlusMan/RichColorPicker',
        'Bug Reports': 'https://github.com/PlusPlusMan/RichColorPicker/issues'
    },
)
