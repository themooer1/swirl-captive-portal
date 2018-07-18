from setuptools import setup

setup(
    name='radiusTest',
    version='1.0',
    url='https://github.com/themooer1/swirl-captive-portal',
    license='License :: OSI Approved :: MIT License',
    author='themooer1',
    author_email='fluffy1781@gmail.com',
    description='RADIUS server, which generates tokens using Alexa.',
    entry_points={
        'console_scripts':[
            'swirl = swirl.guest:main'
        ]
    }
)
