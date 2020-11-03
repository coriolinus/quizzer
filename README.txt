Quizzer is a general-purpose memorization aid written to help flight school students. As such, it includes data files for both the TH-67 and UH-60 helicopters.

I.   INSTALLATION
II.  USAGE
III. EXTENSION
IV.  ABOUT

I. INSTALLATION
I.A WINDOWS

1. Unzip the source file anywhere. It will create a directory: quizzer-0.8
2. Inside quizzer-0.8, there is a subfolder called win32. Move that folder somewhere memorable, and delete the quizzer-0.8 directory.
3. Rename the win32 directory to quizzer

I.B OS X/UNIX/LINUX

1. Install the Python programming language, available at http://python.org/download/releases/2.5.2/ . This version of quizzer requires Python 2.5.x
2. Unzip the source file anywhere memorable
3. Delete the win32 subdirectory

II. USAGE

Quizzer is a shell-based program: it runs in a "DOS box". Windows users, just double-click the 'Command Prompt' icon. Mac users will need to use the Terminal app; *nix users should know how to get a shell.

NOTE: All examples following assume a Windows user. For Mac/*nix, just substitute "python quizzer.py" for "quizzer.exe" in the example to make things work.

NOTE: Examples in this section start with the prompt character '>'. The command prompt will give you the prompt character. Type everything else from the example, then press ENTER to run the example.

The simplest way to run a quiz is to just give the quizzer a data file:

> quizzer.exe th67.data

This will run through the quiz, repeating questions that you get wrong until you get them right enough of the time. To use a different data file, just name the one you want:

> quizzer.exe uh60.data

There are several other options. For example, test mode never repeats a question, and tells you your score once the test is finished:

> quizzer.exe -t uh60.data

You can combine several options to get composite behavior. For example, to randomize the order of the questions while testing:

> quizzer.exe -rt uh60.data

Running the quizzer without a data file will display a help message listing all the available options and what they do.

III. EXTENSION

Data files are simple text files created using a text editor like Notepad. The data file has the following format:
#########################
Question Title
Fill in the blank: _____, correct answer

This is the title of the next question. It is denoted by the newline separating it from the previous question.
A question may have _____ of lines which must all be answered correctly to count the question as correct, any number
There can be _____ answers to fill in per line _____, as many, as you want
There don't even have to be any blanks in a given line at all.

Advanced Formatting
Blanks must always be represented in the question by _____ _____, five, underscores
Answers appear _____ the question and are separated by _____, after, commas
The number of commas in a line must equal the number of blanks. Otherwise, the question cannot be parsed properly.
#########################

See the included data files for longer examples.

If you create a data file for an aircraft not already included in the distribution, please send it to me so I can include it! I'd be happy to attribute it to you.

If you are a coder, the current source will always be available at https://svn.coriolinus.net/quizzer . I'd be happy to consider any patches or bugfixes you send.

IV. ABOUT

Quizzer was created by WO1 Peter Goodspeed in 2007 when he began flight school. It is free for the world, and the most recent distribution can always be found at https://trac.coriolinus.net/browser/quizzer/dist .

peter.goodspeed@us.army.mil