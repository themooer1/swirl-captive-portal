from setuptools import setup, find_packages

setup(
    name='swirl',
    version='1.0',
    url='https://github.com/themooer1/swirl-captive-portal',
    license='License :: OSI Approved :: MIT License',
    packages=find_packages(),
    author='themooer1',
    author_email='fluffy1781@gmail.com',
    description='RADIUS server, which generates tokens using Alexa.',
    include_package_data=True,
    data_files=[('swirl', ['swirl/dictionary', 'swirl/google-10000-english-no-swears.txt', 'swirl/templates.yaml', 'swirl/words.txt'])],
    zip_safe=False,
    entry_points={
        'console_scripts':[
            'swirl=swirl.guest:main'
        ]
    }
)
