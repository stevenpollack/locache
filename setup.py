from setuptools import setup

setup(name='locache',
      version='0.1.0',
      description='package to figure out UTC offsets for arbitrary locations using the google maps API.',
      url='http://github.com/stevenpollack/locache',
      author='Steven Pollack',
      author_email='steven@gnobel.com',
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      license='MIT',
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3"
      ],
      packages=['locache'],
      zip_safe=False)