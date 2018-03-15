from setuptools import setup

setup(name='snhlivedownloader',
        version='0.1',
        description='live.snh48.com视频下载',
        url='',
        author='KnightR',
        author_email='',
        license='MIT',
        packages=['snhlivedownloader'],
        install_requires=[
            'requests',
            'lxml',
            ],
        zip_safe=False)
