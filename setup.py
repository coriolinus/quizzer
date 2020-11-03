from distutils.core import setup
try: 
	import py2exe
except ImportError:
	pass

from glob import glob
datafiles = [fn for fn in glob('*.xml') if fn not in ('test_questions.xml', 'uh60.xml')]
datafiles.append('Command Prompt.lnk')

from quizzer import VERSION
	
setup(name='quizzer',
      version=VERSION,
      description='Quizzer for Memorization',
      author='Peter Goodspeed',
      author_email='coriolinus@gmail.com',
      url='https://trac.coriolinus.net/browser/quizzer/dist',
      py_modules=['quizzer'],
      scripts=['quizzer.py'],
      data_files=[('.', datafiles)],
      console=['quizzer.py'],
      options={"py2exe":{'dist_dir':'win32'}})
