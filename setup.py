from setuptools import setup
setup(name='jieba',  
      version='0.24',  
      description='Chinese Words Segementation Utilities',  
      author='Sun, Junyi',  
      author_email='ccnusjy@gmail.com',  
      url='http://github.com/fxsjy',  
      install_requires=["regex"],
      packages=["jieba"],
      package_dir={'jieba':'jieba'},
      package_data={'jieba':['*.*','finalseg/*','analyse/*','posseg/*']},
)  
