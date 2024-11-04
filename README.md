### make\_cv 

make\_cv is a program that uses Python and LaTex to make a faculty curriculum vitae.  For reasons that are not clear to me, faculty use a c.v. to keep track of everything they have done in their careers.  For most of the data (awards, service, grants, etc…), the basic methodology that make\_cv uses is to keep the data in its most natural format and then process it using Python’s pandas to create LaTeX tabularx tables which are then generated into a c.v.  For scholarship items the system uses a .bib file to store the data and then uses biber to create publications lists (journal articles, conferences, books, etc…).  make\_cv has several features built in to make managing this data easier.  For example, it interfaces with google scholar to update citation counts for each journal article and it uses the provided data on student advisees to mark student authors in the bibliography.   It will also use bibtexautocomplete to fill in missing DOI data for publications.  The following describes its set-up and use.  Other utilities are provided to make web pages from your data (make\_web) and faculty activity reports (make\_far).  These are basically the same except that make\_far offers a \-y flag to limit the number of years of data that are used to make the activity report and the formatting of the data is always chronological.  The default is 3 years of data.

### Installation & Startup:

This assumes you have LaTex and Python installed on your system.  If not see Appendix A for how to install those programs.  To install, use pip:

Mac  
`python pip install --upgrade pip`  
`pip install make_cv`   
Windows  
`python pip install --upgrade pip`  
`pip install make_cv` 

Once make\_cv is installed, you need to create the data directories and default files for adding data.  Choose a name for the root folder for keeping your c.v. related data.  In this example, this folder is called `mydata`.  To create this folder, execute the command

Mac  
`make_cv -b <path>/mydata`   
Windows  
`python -m make_cv.make_cv -b <path>\mydata` 

Where \<path\> is the path to the mydata folder.  This can be a relative or full path.  The \-b flag tells make\_cv to create a new data directory.  For example “`make_cv -b mydata”` creates the default data folders and files in a folder called `mydata` in  current working directory.   Later on, you can configure the locations of all files and folders, but to get started it is easiest to use the defaults.

The folders/files created within mydata are

Awards/personal awards data.xlsx	  
Awards/student awards data.xlsx  
CV/cv.cfg  
CV/cv.tex  
CV/cv\_header.tex  
CV/cv\_tables.tex  
CV/far.tex  
CV/nsf2page.tex  
CV/webpage.tex  
Proposals & Grants/proposals & grants.xlsx  
Scholarship/scholarship.bib  
Scholarship/thesis data.xlsx  
Scholarship/current student data.xlsx  
Scholarship/professional development data.xlsx  
Service/undergraduate research data.xlsx  
Service/service data.xlsx  
Teaching/teaching evaluation data.xlsx

To test that the installation is working, you can make the default c.v. by changing to the mydata/CV directory and executing the command

Mac  
`make_cv`   
Windows  
`python -m make_cv.make_cv` 

This will make the file `cv.pdf` in the CV folder which is just based on the small amount of default data provided.  If something goes wrong hit ctrl-c to stop things or you can just close the terminal window and open a new one.  If you try to do this while you have the file cv.pdf open, it will hang.  It may restart if you close the cv.pdf file, but sometimes you still need to restart the process.  

### The Data

The following describes how to maintain all of the data files in your data folder.  You do not need to use all components of make\_cv if you don’t want to.  See the section Customization to learn how to turn on and off components.  Most people will definitely want to use the Scholarship components, but it may be more convenient to keep other sections using your own personal system.  This is easy to accommodate with make\_cv.  

Awards

1. There are two excel files, one for personal awards and one for student awards.  The files are `student awards.xlsx` and `personal awards.xlsx`.   The notes page of each excel sheet explains what data should be included.   If you receive the same award multiple times, make\_cv will create a single entry for that award with a date string such as: “πτσ Teaching Award 2007-2014”  
   

Proposals & Grants

2. There is one excel file here `proposals & grants.xlsx`.  The only necessary fields are “Proposal”, “Name.1”, “Allocated Amt”, “Total Cost”, “Funded”, “Long Descr”, and “PRO\_BGN\_DT”.   “Proposal” must be a unique identifier for each proposal.  “Name.1” is the name of the funding agency.  “Allocated Amt” is the percent that should be allocated to you and “Total Cost” is the total dollar amount of the grant.  “Funded” is a Y or N field that states whether the proposal was funded or not.  PRO\_BGN\_DT is the start date for the proposed work.  “PRO\_SUB\_DT” is the submission date.   The proposals are organized by proposal start date in the c.v..  If you make a faculty activity report, then the proposals are organized by submission date.  make\_cv will sum up your allocated and total grant dollars and put that at the bottom of the grant section of the c.v.  It will do the same for the proposal dollars.

Scholarship

3. There are three files in this folder   
   1. `current student data.xlsx` contains a list of your currently active graduate students.    
   2. `thesis data.xlsx` contains a list of theses your students have produced.  If the student has not finished the degree yet they should be listed in the `current student data.xlsx` file not in this file.  If you co-advised a student, add that to the title in parentheses i.e. “Life, The Universe, and Everything (co-advised w/D. Adams)”  
   3. `scholarship.bib` is a bibliography file in a BibTex “.bib” format that contains all of your scholarly output.   make\_cv uses the keyword field to help categorize the entries (categorized as: journals, refereed conference papers, conference presentations, books and book chapters, technical reports, patents, invited talks, arXiv papers).   To view and manage a .bib file, download the free program “Jabref” [https://www.jabref.org](https://www.jabref.org/) (Mac & Windows) or on the Mac you can also use “Bibdesk” [https://bibdesk.sourceforge.io](https://bibdesk.sourceforge.io/).  (For the Mac I prefer BibDesk, as it is more stable, but Jabref has a few features that BibDesk does not. See Appendix F for Jabref hints).   Even if you already have a bibliography file,  it is recommended that you create a Google Scholar profile because make\_cv uses Google Scholar for some of its advanced features.   This only needs to be done once.  
      1. Go to [http://**scholar**.**google**.com](http://scholar.google.com/)  website.  
         2. Click the My Citations tab at the top of the page.  
         3.  Login using your university e-mail account.  
         4. Complete the required fields and Provide University Email  
         5.  Select your articles

		  
To use Google Scholar to get started making your scholarship.bib file

1. Go to [https://scholar.google.com](https://scholar.google.com)  
   2. Click “My Profile” on top left of page  
      3. Click the button above the publications to select all of them.   
         4. Click on export \-\> bibtex  
         5. Save the file –  right-click-\>save as  (depends a bit on your browser, might be File-\>save as).  Open the file you saved and the default file scholarship.bib created above using BibDesk/Jabref and drag the entries into the scholarship.bib file.  if you are starting from scratch, you can just overwrite the file.

      

      Other search engines (GoogleScholar, Web of Science, Scopus, etc..) will also allow BibTex records to be downloaded. 

      


Invited talks are generally not picked up by any searches so these must be entered manually.  These are stored using the “Misc” BibTex record type.  You can use BibDesk / Jabref to add these by creating a new entry.  The fields needed are the following:
	 
         @misc{Helenbrook:2009a,

         author \= {B. T. Helenbrook},

         booktitle \= {Clarkson University Physics Club Meeting},

         date \= {2009-11-22},

         keywords \= {invited},

         title \= {Why is Fluid Mechanics Interesting?}}
Patents use the “Misc” type as well.  These can be downloaded from Google Scholar.

Service  
This folder contains 3 files

4. `undergraduate research data.xlsx`.  See the notes sheet in this file for an explanation of the categories.    
5. `service data.xlsx`.   Use this file to keep track of your service data.   The categories are “Description”, “Type”-(University,Department,Professional,Community), “Position”-(Member,Chair), “Term”, “Calendar Year”, “Hours/Semester”.  “Hours/Semester” is not used when making the c.v..  If you have repeated service each term, you should copy and paste the lines from the previous term and make a new entry for each term that you are on an assignment.   make\_cv will gather all like entries into a single entry in the c.v. with a year sequence.  For example, “Science fair judge 2018-2021,2023”  
6. I recommend that you let Web of Science keep your paper reviewing activity records for you.  To use the service do the following  
   1.  Sign up for an account at [Web of Science](https://clarivate.com/products/scientific-and-academic-research/research-publishing-solutions/reviewer-recognition-service/)  
   2. Forward any email receipts you receive from journals when you review a paper to reviews@webofscience.com. Web of Science will store this information for you, providing a certified log of your reviewing activities. (Many journals are doing this for you automatically now).


   To get the most recent data from Web of Science for your c.v.

1. Log in to web of science at the link above using your account information  
2.  Click “View My Researcher Profile”  
3. Click on "Export CV "  
4. Leave start and end dates as is.  Change format to JSON.  
5.  Unclick “List your papers published in selected period  
6. Under Reviews click “List the manuscripts you reviewed in the selected period”  
7. Click the Download Icon (down arrow thingy)  
8. Rename the downloaded json file `reviews data.json` and put it in your `mydata/Service` folder on the s-drive.  The .json file will get converted to `reviews data.xlsx` when the cv is created.   If you have your own reviewing records from before you started using Web of Science you can add them to a separate file called `reviews_non-publons.xlsx`   Use the same format as the `reviews data.xlsx` file i.e. ”Journal, Date, Rounds” and that will automatically get added to the reviews data whenever your c.v. or FAR is generated.  
   make\_cv will gather the reviews by journal and list the number reviews for each journal in the c.v.   it will also sum up the total number of reviews performed over the time period where records were kept and list that in the c.v. as well.

Teaching

7. Every school has a different format for their teaching evaluation data.  make\_cv assumes there will be entries in this file under the column headings: ‘combined\_course\_num', 'STRM', 'term', 'course\_section', 'course\_title','question', ‘Weighted Average', 'enrollment', 'count\_evals'.  ‘Combined\_course\_num’ is the course catalog number i.e. something like “ME515/CE538” for a cross-listed class.  ‘STRM’ is an integer field which is an integer associated with the term the class was taught.  This is used to sort the teaching chronologically.  ‘term’ is the text name of the term i.e. ‘Summer 2024’.  ‘course\_section’ is a section number.  This is treated as text, but is commonly an integer.  ‘course\_title’ is the title i.e. “Intro. to Finite Element Methods”.  ‘Question’ is an integer associated with the question number on the teaching evaluation.  make\_cv is currently assuming that question 19 and 20 are the ones that ask how you rate this instructor and how you rate this course.  These are the responses that go into the cv.  ‘Weighted Average’ is the teaching evaluation times the number of evaluations.  ‘Enrollment’ is the total enrollment in the section, and ‘count\_evals’ is the number of teaching evaluations received for that class.  This format is likely to not be convenient for other Universities.  See the customization section below for how to change this.. 

### Configuration & Customization

To use all of the features of make\_cv, some additional information must be provided.  The file CV/cv.cfg contains all of the configuration information.  This is a text file that can be edited with any text editor.  To use any of the Google Scholar features, you have to enter your Google ID.  To find this go to [Google Scholar](https://scholar.google.com) and click on “My profile” in the top left.  If you examine the url for this page it should have a section that looks like: user=m\_of3wYAAAAJ\&hl=en.  Your user id is the string after the \= sign up to but not including the &.  So in this case it is “m\_of3wYAAAAJ”.  Put this value into the cv.cfg file under “googleid”.  

The other significant configuration that can be done with this file is to set the defaults for what sections of the cv make\_cv controls.  These are controlled by the entries under “CV”.  If a data file is empty or missing, make\_cv will automatically exclude it so you don’t need to turn off empty sections.  I often leave all the sections on, then use command line options (discussed below) to create a shorter c.v. when I need that.

Further configurations can be done by editing the file cv\_header.tex, cv.tex, and cv\_tables.tex. 

1. cv\_header.tex is the LaTex header file that gets imported into cv.tex.  If you are comfortable with Latex, you can customize things like, fonts, margins, etc… with this file.  
2. cv.tex is the first page information for the c.v.  This contains things like your name and contact information, employment and education history, etc…   You can format this how you like, but know that the \\section\* command should be used to create different sections within the c.v.  
3. cv\_tables.tex is included by cv.tex, and is responsible for including all of the automatically created tables in the c.v.   If you would like to use your own custom system for a particular section of the data, you can comment out the table that is being included by cv.tex, and import whatever LaTeX compatible file you want.


### Advanced Features & Command Line Options

The `make_cv` tool provides a range of command-line options to customize and automate CV generation. Below is a list of the most useful options. Run `make_cv -h` to see the full list.

| Option                   | Description                                                                                                                                                                                                                      |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-g {NUMBER OF YEARS}`   | Search for and add new entries from Google Scholar to the `.bib` file for the past specified number of years. Use `-g -1` to search for all available entries. Defaults to `1` if `-g` is used without specifying a number.       |
| `-c {true,false}`        | Update citation counts stored in the `.bib` file.                                                                                                                                                                               |
| `-m {true,false}`        | Update student author markers in the `.bib` file.                                                                                                                                                                               |
| `-I {true,false}`        | Use `bibtexautocomplete` to search for and add missing DOIs to the `.bib` file.                                                                                                                                                 |
| `-e {SECTION}`           | Exclude a section from the CV. Sections include: `Grants`, `PersonalAwards`, `Conference`, `GradAdvisees`, `Proposals`, `UndergradResearch`, `Reviews`, `Refereed`, `Invited`, `Service`, `Teaching`, `Book`, `Patent`, `StudentAwards`, `Journal`. |
| `-d {PATH TO DATA DIRECTORY}` | Override the default data directory location specified in the config file.                                                                                                                                                      |
| `-f {PATH TO CONFIGURATION FILE}` | Specify a configuration file. Defaults to `cv.cfg`.                                                                                                                                                                             |
| `-D {NAME}`              | Override data directory location in config file for specific sections. `NAME` can be `Scholarship`, `PersonalAwards`, `StudentAwards`, `Service`, `Reviews`, `CurrentGradAdvisees`, `GradTheses`, `UndergradResearch`, `Teaching`, `Proposals`, `Grants`. |
| `-F {NAME}`              | Override data file location in config file for specific sections. `NAME` can be `Scholarship`, `PersonalAwards`, `StudentAwards`, `Service`, `Reviews`, `CurrentGradAdvisees`, `GradTheses`, `UndergradResearch`, `Teaching`, `Proposals`, `Grants`. |
| `-J {NAME}`              | Specify the name of the reviews JSON file.                                                                                                                                                                                      |
| `-j {true,false}`        | Force conversion of a reviewing JSON file downloaded from Web of Science.                                                                                                                                                       |
| `-S {SCRAPERID}`         | Specify the `ScraperID` (optional, but helps avoid Google blocking requests).                                                                                                                                                   |
| `-s {true,false}`        | Use scraper to avoid Google blocking.                                                                                                                                                                                           |
| `-G {GOOGLEID}`          | Specify `GoogleID` (used for finding new publications).                                                                                                                                                                         |
| `-C {true,false}`        | Include citation counts in the CV.                                                                                                                                                                                              |
| `-M {true,false}`        | Include student author markers in the CV.                                                                                                                                                                                       |




For example, the following will look for any new google scholar entries in the 4 last years, help you categorize them, then update the citation counts using google scholar, update the student markers, and exclude the proposals and conferences section when making a c.v.

Mac  
`make_cv -g 4 -c true -m true -e Conference -e Proposals`

Windows  
`python -m make_cv.make_cv -g 4 -c true -m true -e Conference -e Proposals`

Most of the advanced features are by default off, but you can turn them on by default by editing the cv.cfg file in your CV folder.  I usually only use the advanced features intermittently so I leave the advanced features off by default and then use the command line options when I need to use them.

The first time you run make\_cv it will find unclassified entries in your .bib file and ask you to classify them.  This will also happen if you add an entry from some other search source and it is not classified.  This modifies the keywords in the .bib file.  The categories determine in what sections that item will appear in the c.v.  If there is something appearing in the wrong section, use Bibdesk or Jabref to put the entry in the correct category.  (A drag and drop operation in BibDesk.  See Appendix F for Jabref instructions).  One of the categories is ignore, which should be chosen if you want to keep the entry in the .bib file but you don’t want it to appear in the c.v. 

If you add \-g true, it will use Google Scholar to find any entries that have appeared in the last year and ask you if you want to add them.  Everything in google scholar has an id, so it keeps track of these in the .bib file and will never ask you to add an entry twice.  It also uses these id tags when it updates the number of citations an entry has.  It will use bibtexautocomplete to add doi information to the new entries.  The doi’s appear as hyperlinks in the c.v. so people can click on an entry in your c.v. and be taken to the corresponding web location for that item.

If you add \-m true, it uses the files “undergraduate research data.xlsx”, “thesis data.xlsx” and “current student data.xlsx” to find the first initial and last names of all of your student advisees.  It then adds a marker after those names in the .bib file.  The two markers are \\us for undergraduate student and \\gs for graduate student.  The actual symbol that these commands create is defined in the `cv_header.tex` file.  Currently, make\_cv is configured to mark these authors in perpetuity, meaning that if you have a student who was an undergraduate advisee that became a graduate advisee, then you published with them 10 years later, that author will still receive both an undergraduate and a graduate advisee student marker.  There is a way to set a time limit for when this terminates, but I haven’t exposed that functionality yet.

If you add `-M false`, it will redefine the \\us and \\gs markers so that no markers are produced in the file. This is also configurable in the cv.cfg file with the entry includestudentmarkers.

If you add `-c true`, it will use google scholar to update/add the field “citations” in the .bib file.  This is the number of times this article has been cited.  It will appear in brackets after the bibliographic entry in the c.v.  i.e.

19. N. Bagheri-Sadeghi\+, B. T. Helenbrook, and K. D. Visser. “Ducted Wind Turbine Optimization and Sensitivity to Rotor Position”, Wind Energy Science 3, no. 1 (Apr. 2018), pp. 221–229. doi: 10.5194/wes-3-221-2018. \[42\]

This can also be turned on and off with \-C flag or by using the entry includecitationcounts in the cv.cfg file.

\-I true will use bibtexautocomplete to search for DOI’s that are missing from the .bib file.  It will add the doi then add a record btacqueried to the .bib file so it will never try to find the doi for that entry again.  

Appendix A: Python & LaTex Installation Instructions

##### Mac Installation

To install LaTeX: [https://www.tug.org/mactex/](https://www.tug.org/mactex/)

Install python using homebrew, by entering the following two commands in a terminal.app window:  
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`  
`brew install python`

Make a virtual environment for python scripts so they can be separate from system stuff  
`mkdir ~/.venv`  
`python3 -m venv ~/.venv`  
`source ~/.venv/bin/activate`

To make this python installation work every time you open a new terminal window:  
`cat “source ~/.venv/bin/activate” >> .zprofile`

##### Windows Installation

Install python from Windows App Store   
and LaTeX from [https://miktex.org/download](https://miktex.org/download)  
when installing LaTeX change the default paper size to letter and also click “automatically install missing packages” (something like that anyway).

##### Appendix B: Instructions for Modifying Your scholarship.bib file with Jabref

(Warning: Jabref refuses to save a file to a network drive so I have to save it to the desktop and then drag it over to the network drive.) 

To get Jabref to show the categorization of the entries, under the “View” menu make sure “Groups” has a check mark next to it.  Right click on the “All Entries” group in the left side bar.  Choose “Add subgroup”, give the group the name “Categories”, Choose “Collect By” “Specified Keywords” dialog, then “Generate groups from keywords in the following field” and type “keywords” for the field to group by.  For delimiter put a semicolon, then hit ok.   This should make your current categories show in the left side bar.  Save the file so you won’t have to do this again, the next time you open it. 

To edit the category of an entry (journal,conference,refereed conference…), select the entry by left clicking on it, then right click on the category in the left hand side bar you would like to either add or remove the entry from. You will then see options to “Add selected entries to this group” or “Remove selected entries from this group”. 

To change the bibtex type of an entry (This is different than the group, these are defined by bibtex and are things like “article,inproceedings,conference,miscellaneous, etc…  It tells bibtex what type of data to expect for this entry,) click on the intended entry and wait for the bottom window to update. On the left hand side of the bottom window you will see a small pencil symbol, click on that and hover over the words “BibTeX” or “IEEETran”. Under these two sections you will see the different types of entries show up, select the choose entry type by left clicking on the word.

To edit an entry itself, all you need to do is click on the entry, wait for the bottom window to update, and click through the different sections to edit them. Be sure to click on the “Generate” button next to the Citation Key section (under “Required Fields”) after updating an entry to ensure that the key is up to date.

Jabref can try to import entries from a text citation list.  It's a little sketchy but can save a lot of work if you have a list of invited talks you want converted.  There is a menu entry under the “Library” menu called “New entry from plain text”  Follow the instructions from there.
