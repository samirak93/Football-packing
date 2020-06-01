from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='football_packing',
      version='0.2',
      description='Calculate the packing rate for a given pass in football (soccer)',
      long_description=readme(),
      url='https://github.com/samirak93/Football-packing',
      author='Samira Kumar',
      author_email='samirakumarv@gmail.com',
      license='LICENSE.txt',
      packages=['football_packing'],
      install_requires=[
          'numpy >= 1.18.1',
          'pandas >= 1.0.3',
          'bokeh >= 2.0.2',
          'scipy >= 1.4.1',
          'scikit-learn >= 0.23.1',
      ],
      keywords='soccer football analytics packing',
      include_package_data=True,
      zip_safe=False)
