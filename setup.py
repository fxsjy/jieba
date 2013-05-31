from distutils.core import setup  
setup(name='jieba',  
      version='0.28.4',  
      description='Chinese Words Segementation Utilities',  
      author='Sun, Junyi',  
      author_email='ccnusjy@gmail.com',  
      url='http://github.com/fxsjy',  
      packages=['jieba'],  
      package_dir={'jieba':'jieba'},
      package_data={'jieba':['*.*','finalseg/*','analyse/*','posseg/*']}
)  
