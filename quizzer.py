#!/usr/env/python
"""
quizzer is a flexible program to aid in memorizing certain facts by rote. 
It was conceived as an aid to memorizing large volumes of data quickly for flight school.
"""
#Peter Goodspeed, 2007

from __future__ import division
from random import shuffle, random, randint
from xml.etree.cElementTree import parse

import re

VERSION="0.9.3"
KNOWNRATIO = .65
EXTENDRATIO = .5

nonwhitespace = re.compile(r'\S+')
punctuation = re.compile(r'[^\w\s%]+')

def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

class InstantiationError(Exception):
	def __init__(self, value, instantiated=None):
		self.value = value
		self.instantiated = instantiated
	
	def __str__(self):
		return self.value

class Line(object):
	"""
	A line within a question.
	"""
	def __init__(self, lineElement):
		self.fragments = [] #text interspersed with None where blank(s) should go
		self.answers = [] #the correct answers to fill the blanks
		if lineElement.text is not None:
			self.fragments.append(lineElement.text)
		for q in lineElement:
			self.fragments.append(None)
			self.answers.append(q.text.strip().lower())
			if q.tail is not None:
				self.fragments.append(q.tail)
			
		#normalize the answers then save to self
		self.answersNormSP = nonwhitespace.findall(' '.join(self.answers))
		self.answersNormNSP = [punctuation.sub('', ans) for ans in self.answersNormSP]
	
		
	def __str__(self):
		return self.toStr()
		
	def toStr(self, lengthHint=False, wordHint=False, showAnswers=False, correctThis=None, showPunctuation=True):
		ret = []
		ans = list(self.answers) # create a shallow copy
		
		for frag in self.fragments:
			if frag is None:
				if not showAnswers:
					ret.append(self.formblanks(ans.pop(0), lengthHint, wordHint))
				else:
					if not showPunctuation:
						ans[0] = punctuation.sub('', ans[0])
					if correctThis is None:
						ret.append(ans.pop(0))
					else:
						answords = nonwhitespace.findall(ans.pop(0))
						for word in answords:
							try:
								if word == correctThis.pop(0):
									ret.append(word)
								else:
									ret.append('*%s*' % word)
							except IndexError:
								ret.append('*%s*' % word)
			else:
				# always show punctuation here
#				if not showPunctuation:
#					frag = punctuation.sub('', frag)
				ret.append(frag)
		
		return ' '.join(ret)
	
	def formblanks(self, answer, lengthHint=False, wordHint=False, showPunctuation=False):
		if wordHint:
			answer = answer.split(' ')
		else:
			answer = [answer]
		
		if lengthHint:
			mul = lambda word: len(word)
		else:
			mul = lambda word: 5
			
		return ' '.join(('_' * mul(word) for word in answer))
	
	def ask(self, options):
		"Quizzes this line. Repeats it until it is answered correctly."
		lengthHint = options['lengthHint']
		wordHint = options['wordHint']
		print wrap(self.toStr(lengthHint=lengthHint, wordHint=wordHint, showPunctuation=options['showPunctuation']), 79)
		iters = 0
		ok = True
		while iters == 0 or not ok:
			iters += 1
			ok = True
			try:
				ans = raw_input(': ')
			except EOFError: #this try/except shouldn't be necessary, but things break every once in a while without it
				raise KeyboardInterrupt
			ans = ans.lower()
#			import pdb; pdb.set_trace()
			if not options['strictPunctuation']:
				ans = punctuation.sub('', ans)
			studentAnswers = nonwhitespace.findall(ans)
			if options['strictPunctuation']:
				ok = ok and (studentAnswers == self.answersNormSP)
			else:
				ok = ok and (studentAnswers == self.answersNormNSP)
			if not ok:
				print
				print "The correct answer follows:"
				print wrap(self.correct(studentAnswers), 79)
				print
			if options['test']: break
		if iters == 1 and ok:
			return True
		return False
		
	def correct(self, studentAnswers=None):
		return self.toStr(showAnswers=True, correctThis=studentAnswers)
	
		# sqr = self.question.replace('%', ']@[')
		# if studentAnswers is None:
			# return (sqr.replace('_____', '%s') % tuple(['*' + i + '*' for i in self.answers])).replace(']@[', '%')
		# ans = []
		# for a in xrange(self.portions):
			# try:
				# if studentAnswers[a] == self.answers[a]: ans.append(self.answers[a])
				# else: ans.append('*%s*' % self.answers[a])
			# except IndexError:
				# ans.append('*%s*' % self.answers[a])
		# return (sqr.replace('_____', '%s') % tuple(ans)).replace(']@[', '%')
		

class Question(object):
	"""
	A Question
	"""
	def __init__(self, questionElement):
		try:
			self.title = [c for c in questionElement if c.tag=='title'][0].text
		except IndexError:
			raise InstantiationError("Malformed Question: no Title present!", self)
			
		self.lines = [Line(c) for c in questionElement if c.tag=='line']
		
		self.tries = 0		 #the number of times the interrogatee has been asked this question
		self.corrects = 0  #the number of times the interrogatee has answered this question correctly the first time
		self.attempts = [] #the full record of interrogatee successes and failures at answering this question
	
	def writexml(self, fp):
		fp.write('<question><title>')
		fp.write(self.title)
		fp.write('</title>\n')
		for line in self.lines:
			line.writexml(fp)
		fp.write('</question>\n\n')
	
	def __str__(self):
		return self.title
	
	def ask(self, options):
		"""
		Asks this question. 
		Assuming not test, any error in any of the lines will result in the entire question being repeated.
		The interrogatee gets to move on to the next question only after they have completely correctly answered this one.
		
		If istest, the interrogatee gets only one chance to answer the question
		"""
		self.tries += 1
		iters = 0
		ok = True
		while iters == 0 or not ok:
#			print "Question.ask(): (iters, ok) = (%s, %s)" % (str(iters), str(ok))
			print
			print self.title
			iters += 1
			ok = True
			for line in self.lines:
				if len(line.answers) > 0:
					ok = line.ask(options) and ok
				else:
					print str(line)
			if options['test']: break #testers only get one shot at each line
		if iters == 1 and ok: 
			self.corrects += 1
			self.attempts.append(True)
			return True
		self.attempts.append(False)
		return False
	
	def ratio(self):
		"""
		Return the ratio of correct / attempted answers over the lifetime of this question.
		"""
		try:
			return self.corrects / self.tries
		except ZeroDivisionError:
			return 0
			
	def recentRatio(self, span=3):
		"""
		Return the ratio of correct / attempted answers to this question, counting only span most recent.
		"""
		try:
			return len([i for i in self.attempts[-span:] if i]) / len(self.attempts[-span:])
		except ZeroDivisionError:
			return 0
		

class Quizzer(object):
	def __init__(self, datafile, options):
		self.datafile = datafile
		
		self.options = options
		
		self.questions = []
		
		root = parse(datafile).getroot()
		for node in root:
			if node.tag == 'question':
				self.questions.append(Question(node))

	def ask(self, question):
		return question.ask(self.options)
	
	def run(self):
		questions = list(self.questions)
		if self.options['randomized']:
			shuffle(questions)
		if self.options['reversed']:
			questions.reverse()
				
		if self.options['test']:
			correct = 0
			attempt = 0
			
			try:
				for question in questions:
					attempt += 1
					if self.ask(question): correct += 1
			finally:
				print
				print
				print "You scored %i / %i: %.1f%% " % (correct, attempt, 100.0*(correct / attempt))
				print
				print "You need work in the following areas:"
				for question in questions:
					if question.corrects < question.tries: print question

		else:
			known = []
			working = [questions.pop(0)]
			
			lqa = None #last question asked
			rolqa = None #repetitions of last question asked: how many times we've repeated the one
			
			try:
				while True:
#					print "Quizzer.run(): begin interation through the working set"
					for q in working:
						self.ask(q)
						
						if lqa == q:
							rolqa += 1
						else:
							rolqa = 1
						lqa = q
					
					#move questions from Working to Known if their ratio is good
					known.extend((q for q in working if q.recentRatio() >= KNOWNRATIO))
					working = [q for q in working if q.recentRatio() < KNOWNRATIO]

					try:
						# if we can extend the working set because we've got a good enough ratio, great!
						if self.avg(working, lambda q: q.recentRatio()) >= EXTENDRATIO:
							working.insert(0, questions.pop(0))
						# or, if we've repeated the same question a few times, extend anyway
						# (but avoid adding two in a single cycle)
						elif rolqa >= 2: # adhd: repeat a question at most twice
							working.insert(0, questions.pop(0))
					except IndexError:
						pass
					
					try:
						if len(working) == 0: working.append(questions.pop(0))
					except IndexError:
						break #when we're through with the working set, get out of here
					
					
					if random() < (.1 * len(known) / (len(known) + len(working))):
						working.append(known.pop(randint(0, len(known) - 1)))
						# randint's range includes both end points, so we must subtract 1 from len(known)
						# to ensure a valid index to pop.
						
			finally:
				print
				print
				print "There are %i Questions Known. They took an average of %.2f attempts to learn." % (len(known), self.avg(known, lambda q: q.corrects / q.tries))
				if len(working) > 0: print "There are %i Questions in the Working Group with an average success rate of %.2f" % (len(working), self.avg(working, lambda q: q.ratio()))
				if len(questions) > 0: print "There are %i Questions Unasked this round." % len(questions)
				
				testedquestions = []
				testedquestions.extend(known)
				testedquestions.extend(working)
				testedquestions.sort(key=lambda q: q.ratio())
				testedquestions = [q for q in testedquestions[:5] if q.ratio() < 1]
				if len(testedquestions) > 0:
					print
					print "Your worst Questions:"
					for q in testedquestions:
						print q
				
	def avg(self, qs, lamda= lambda q: q):
		try:
			return sum((lamda(q) for q in qs)) / len(qs)
		except ZeroDivisionError:
			return 0



def main(quizzer_init_args):
	"""
	Call this to run the quizzer program.
	
	quizzer_init_args: a tuple of arguments to initialize the Quizzer object with
	"""
	#I'd say @see Quizzer.__init__ but I seem to have left out any sort of documentation for that function
	
	q = Quizzer(*quizzer_init_args)
	
	try:
		q.run()
	except KeyboardInterrupt:
		pass

def writexml(fn):
	q = Quizzer(fn, False, False, False)
	fname = fn.rsplit('.', 1)[0] + '.xml'
	
	with file(fname, 'wb') as fp:
		q.writexml(fp)
	
	with file(fname, 'rb') as fp:
		fd = fp.read()
	
	with file(fname, 'wb') as fp:
		fp.write(re.sub(' </q>', '</q> ', fd))

if __name__ == '__main__':
	#handle the command-line options
	from optparse import OptionParser
	parser = OptionParser(usage="usage: %prog [options] datafile", version="%prog " + VERSION)
	parser.set_defaults(test=False, randomized=False, reversed=False, lengthHint=False, wordHint=False, strictPunctuation=False, showPunctuation=False)
	parser.add_option('-t', '--test', action="store_true", dest="test",
	                  help='Give only one chance per question, and generate a score after.')
	parser.add_option('-q', '--quiz', action="store_false", dest="test",
	                  help='Re-ask questions to aid memory formation [default]')
	parser.add_option('-r', '--randomized', action="store_true", 
	                  dest="randomized", help='Randomize the order in which the questions are asked')
	parser.add_option('-s', '--sequential', action="store_false", dest="randomized",
	                  help='Ask questions in the same order as in the datafile [default]')
	parser.add_option('-v', '--reversed', action="store_true", dest="reversed",
	                  help='Reverse the order in which the questions are asked')
	parser.add_option('-l', '--lengthhint', action="store_true", dest="lengthHint",
	                  help='Question field length is proportional to answer length')
	parser.add_option('-L', '--nolengthhint', action="store_false", dest="lengthHint",
	                  help='Question field length is a fixed value [default]')
	parser.add_option('-w', '--wordhint', action="store_true", dest="wordHint",
	                  help='Question field is broken into the appropriate number of words')
	parser.add_option('-W', '--nowordhint', action="store_false", dest="wordHint",
	                  help='Question field is uniform regardless of number of words [default]')
	parser.add_option('-p', '--strictpunctuation', action="store_true", dest="strictPunctuation",
	                  help='Punctuation is treated strictly and must be replicated exactly')
	parser.add_option('-P', '--laxpunctuation', action="store_false", dest="strictPunctuation",
	                  help='Punctuation is ignored in answers [default]')
	parser.add_option('-u', '--showpunctuation', action="store_true", dest="showPunctuation",
	                  help='Punctuation within the question is displayed to prompt the user')
	parser.add_option('-U', '--hidepunctuation', action="store_false", dest="showPunctuation",
	                  help='Punctuation within the question is hidden [default]')
							
	(options, args) = parser.parse_args()
	if len(args) != 1:
		parser.print_help()
		parser.exit()
		
	main((args[0], eval(str(options))))
