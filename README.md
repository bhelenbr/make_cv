### make\_cv

make\_cv is a program that uses Python and LaTex to make a faculty curriculum vitae.  For tenure and promotion, faculty need a c.v. that keeps track of everything they have done in their careers.  For most of the data (awards, service, grants, etc…), the basic methodology that make\_cv uses is to keep the data in its most natural format and then process it using Python’s pandas to create LaTeX tabularx tables which are then generated into a c.v.  For scholarship items the system uses a .bib file to store the data and then uses biber to create publications lists (journal articles, conferences, books, etc…).  make\_cv has several features built in to make managing this data easier.  For example, it interfaces with google scholar to update citation counts for each journal article and it uses the provided data on student advisees to mark student authors in the bibliography.   It will also use bibtexautocomplete to fill in missing DOI data for publications.  The following describes its set-up and use.  Other utilities are provided to make web pages from your data (make\_web), faculty activity reports (make\_far), and an NSF collaborator list (make\_nsfcoa).  make\_far offers a \-y flag to limit the number of years of data that are used to make the activity report and the formatting of the data is always chronological.  The default is 3 years of data.

### Installation & Quick Start:

This assumes you have LaTeX and Python installed on your system.  If not see Appendix A for how to install those programs.  To install, use pip:

`python pip install --upgrade pip`  
`pip install make_cv`

Once make\_cv is installed, you need to create the data directories and default files for adding data.  Choose a name for the root folder for keeping your c.v. related data.  To create this folder, execute the command

`make_cv -b <folder name>`

The `-b` flag tells make\_cv to create a new data directory.  For example “`make_cv -b myData”` creates the default data folders and files in a folder called `myData` in the current working directory.  The folder “`make_cv”`in the `myData` folder contains subfolders for several different outputs.  To make the example cv, cd to “`make_cv/CV”`. In this folder is a text file called “`make_cv.cfg”.` This is a text file that can be edited with any text editor.  To use the Google Scholar features, you have to enter your Google ID.  To find this go to [Google Scholar](https://scholar.google.com) and click on “My profile” in the top left.  (If you don't have a public Google Scholar profile, follow [these instructions](https://scholar.google.com/intl/en/scholar/citations.html)). If you examine the url for your profile page it should have a section that looks like: user=m\_of3wYAAAAJ\&hl=en.  Your user id is the string after the \= sign up to but not including the &.  So in this case it is “m\_of3wYAAAAJ”.  Put this value into the `make_cv.cfg` file under “googleid”.

Look through the folders and files created and add any additional data that you would like or leave it blank and that section will be ignored.  The format and usage of these files is described below.

Edit the personal data in the files in the folder “`PersonalData”.` At the top of the file “`ContactInfo.tex”` change the command \\boldname{Lastname}{F} to your last name and first initial to have your name bolded in the bibliography.  The files “`Education.tex”`  and “`Employment.tex”` are where you add your education and employment history.

Now use Google Scholar to get the bibliographic and citation information for your scholarly works:

`make_cv -g -1`

This will get everything and might take a while if you have a lot of publications.  There are other import options that might be faster (see below), but this is the easiest.  The flag “`-g -1”` tells make\_cv to get all years of citations using Google Scholar.   When it is finished it will create the file `CV/cv.pdf` that you should open to see the results.

### The Data

The files created within the `mydata/make_cv/` folder are  
`PersonalData/ContactInfo.tex` – personal info for cv creation *(fill in your data)*  
`PersonalData/Education.tex` – educational history  *(fill in your data)*  
`PersonalData/Employment.tex` – employment history  *(fill in your data)*  
`PersonalData/photo.jpg` – personal photo *(provide photo or set usePhoto to false in ContactInfo.tex)*  
`PersonalData/reference.tex` – file to include list of references

`CV/cv.tex` – document that gets compiled by `make_cv` to create cv  
`FAR/far.tex` – document that gets compiled `make_far` to create faculty activity report  
`Web/web.tex` – file to create web pages using `make_web`  
`Collaborator/` folder to create an NSF collaborator list using `make_nsfcoa`

`make_cv.cfg` – configuration file (in each folder).  The other files in the folders contain settings for XeLaTex that do not need to be modified.

The data files created within the `mydata` folder are  
`Awards/personal awards data.xlsx`  
`Awards/student awards data.xlsx`  
`Proposals & Grants/proposals & grants.xlsx`  
`Scholarship/scholarship.bib`  
`Scholarship/thesis data.xlsx`  
`Scholarship/current student data.xlsx`  
`Scholarship/professional development data.xlsx`  
`Service/undergraduate research data.xlsx`  
`Service/service data.xlsx`  
`Teaching/teaching evaluation data.xlsx`

The following describes how to maintain all of the data files in your data folder.  You do not need to use all components of make\_cv if you don’t want to.  See the section Customization to learn how to turn on and off components.  Most people will definitely want to use the Scholarship components, but it may be more convenient to keep other sections using your own personal system.  This is easy to accommodate with make\_cv.  (As an aside, a lot of this was designed to be used with PeopleSoft to get data directly from the University.)

Awards

1. There are two excel files, one for personal awards and one for student awards.  The files are `student awards.xlsx` and `personal awards.xlsx`.   The notes page of each excel sheet explains what data should be included.   If you receive the same award multiple times, make\_cv will create a single entry for that award with a date string such as: “πτσ Teaching Award 2007-2014”

Proposals & Grants

2. There is one excel file here `proposals & grants.xlsx`.  The only necessary fields for the cv are “Proposal\_ID”, “Sponsor”, “Allocated Amt”, “Total Cost”, “Funded?”, “Title”, and “Begin Date” .  The field “Principal Investigators” is necessary if you want to make a NSF collaborator list.   “Proposal” must be a unique identifier for each proposal.  “Sponsor” is the name of the funding agency.  “Allocated Amt” is the percent that should be allocated to you and “Total Cost” is the total dollar amount of the grant.  “Funded?” is a Y or N field that states whether the proposal was funded or not.  "Begin Date" is the start date for the proposed work.  The proposals are organized by proposal begin date in the c.v. and faculty activity report.   make\_cv will sum up your allocated and total grant dollars and put that at the bottom of the grant section of the c.v.  It will do the same for the proposal dollars. 

Scholarship

3. There are three files in this folder  
     
   1. `current student data.xlsx` contains a list of your currently active graduate students.  
        
   2. `thesis data.xlsx` contains a list of theses your students have produced.  If the student has not finished the degree yet they should be listed in the `current student data.xlsx` file not in this file.  If you co-advised a student, add that to the title in parentheses i.e. “Life, The Universe, and Everything (co-advised w/D. Adams)”  
        
   3. `scholarship.bib` is a bibliography file in a BibTex “.bib” format that contains all of your scholarly output.   make\_cv uses the keyword field to help categorize the entries (categorized as: journals, refereed conference papers, conference presentations, books and book chapters, technical reports, patents, invited talks, arXiv papers).   To view and manage a .bib file, download the free program “Jabref” [https://www.jabref.org](https://www.jabref.org/) (Mac & Windows) or on the Mac you can also use “Bibdesk” [https://bibdesk.sourceforge.io](https://bibdesk.sourceforge.io/).  (For the Mac I prefer BibDesk, as it is more stable, but Jabref has a few features that BibDesk does not. See Appendix F for Jabref hints).   Even if you already have a bibliography file,  it is recommended that you create a Google Scholar profile because make\_cv uses Google Scholar to get citation counts.  
        
      If you have a lot of publications it may be easier to use Google Scholar to get started making your scholarship.bib file rather than using `-g -1`.  To do this:  
        
      1. Go to [https://scholar.google.com](https://scholar.google.com)  
      2. Click “My Profile” on top left of page  
      3. Click the button above the publications to select all of them.  
      4. Click on export \-\> bibtex  
      5. Save the file –  right-click-\>save as  (depends a bit on your browser, might be File-\>save as).  Open the file you saved and the default file scholarship.bib created above using BibDesk/Jabref and drag the entries into the scholarship.bib file.

      

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

4. This folder contains 3 files  
     
   1. `undergraduate research data.xlsx`.  See the notes sheet in this file for an explanation of the categories.  
        
   2. `service data.xlsx`.   Use this file to keep track of your service data.   The categories are “Description”, “Type”-(University,Department,Professional,Community), “Position”-(Member,Chair), “Term”, “Calendar Year”, “Hours/Semester”.  “Hours/Semester” is not used when making the c.v..  If you have repeated service each term, you should copy and paste the lines from the previous term and make a new entry for each term that you are on an assignment.   make\_cv will gather all like entries into a single entry in the c.v. with a year sequence.  For example, “Science fair judge 2018-2021,2023”  
        
   3. `reviews data.xlsx`. I recommend that you let Web of Science keep your paper reviewing activity records for you.  To use the service do the following  
        
      1. Sign up for an account at [Web of Science](https://clarivate.com/products/scientific-and-academic-research/research-publishing-solutions/reviewer-recognition-service/)  
      2. Forward any email receipts you receive from journals when you review a paper to [reviews@webofscience.com](mailto:reviews@webofscience.com). Web of Science will store this information for you, providing a certified log of your reviewing activities. (Many journals are doing this for you automatically now).

      

      To get the most recent data from Web of Science for your c.v.

      

      1. Log in to web of science at the link above using your account information  
      2. Click “View My Researcher Profile”  
      3. Click on "Export CV "  
      4. Leave start and end dates as is.  Change format to JSON.  
      5. Unclick “List your papers published in selected period  
      6. Under Reviews click “List the manuscripts you reviewed in the selected period”  
      7. Click the Download Icon (down arrow thingy)  
      8. Rename the downloaded json file `reviews data.json` and put it in your `mydata/Service` folder on the s-drive.  The .json file will get converted to `reviews data.xlsx` when the cv is created.     
      9. If you have your own reviewing records from before you started using Web of Science you can add them to a separate file called `reviews_non-publons.xlsx`   Use the same format as the `reviews data.xlsx` file i.e. ”Journal, Date, Rounds” and that will automatically get added to the reviews data whenever your c.v. or FAR is generated.

      

      make\_cv will gather the reviews by journal and list the number reviews for each journal in the c.v.   it will also sum up the total number of reviews performed over the time period where records were kept and list that in the c.v. as well.

Teaching

5. `teaching data.xlsx`.  Every school has a different format for their teaching evaluation data.  make\_cv assumes there will be entries in this file under the column headings: ‘combined\_course\_num', 'STRM', 'term', 'course\_section', 'course\_title','question', ‘Weighted Average', 'enrollment', 'count\_evals'.  ‘Combined\_course\_num’ is the course catalog number i.e. something like “ME515/CE538” for a cross-listed class.  ‘STRM’ is an integer field which is an integer associated with the term the class was taught.  This is used to sort the teaching chronologically.  ‘term’ is the text name of the term i.e. ‘Summer 2024’.  ‘course\_section’ is a section number.  This is treated as text, but is commonly an integer.  ‘course\_title’ is the title i.e. “Intro. to Finite Element Methods”.  ‘Question’ is an integer associated with the question number on the teaching evaluation.  make\_cv is currently assuming that question 19 and 20 are the ones that ask how you rate this instructor and how you rate this course.  These are the responses that go into the cv.  ‘Weighted Average’ is the teaching evaluation times the number of evaluations.  ‘Enrollment’ is the total enrollment in the section, and ‘count\_evals’ is the number of teaching evaluations received for that class.  This format is likely to not be convenient for other Universities.  See the customization section below for how to change this.. There are two output formats for teaching a long format that lists every class taught and a short format which condenses the information.  This is controlled by a flag in the configuration file 'shortteachingtable \= true/false'.

### Configuration & Customization

To use all of the features of make\_cv, some additional information must be provided.  The file `CV/make_cv.cfg` contains all of the configuration information.  As discussed above, you should put your Google Scholar ID here.  You can also add your ORCID and use the ORCID data to find publications.

The other significant configuration that can be done with this file is to set the defaults for what sections of the cv make\_cv controls.  These are controlled by the entries under “CV”.  If a data file is empty or missing, make\_cv will automatically exclude it so you don’t need to turn off empty sections.  I often leave all the sections on, then use command line options (discussed below) to create a shorter c.v. when I need that.

Further configurations can be done by editing `cv.tex` and `settings.sty` files. These are normal LaTeX files so you can modify them as you like.

### Advanced Features & Command Line Options

The `make_cv` tool provides a range of command-line options to customize and automate CV generation. Below is a list of the most useful options. Run `make_cv -h` to see the full list.

| Option | Description |
| :---- | :---- |
| `-g {NUMBER OF YEARS}` | Search for and add new entries from Google Scholar to the `.bib` file for the past specified number of years. Use `-g -1` to search for all available entries. Defaults to `1` if `-g` is used without specifying a number. |
| `-G {GOOGLEID}` | Override `GoogleID` specified in config file |
| `-c {true,false}` | Update citation counts stored in the `.bib` file. |
| `-m {true,false}` | Update student author markers in the `.bib` file. |
| `-I {true,false}` | Use `bibtexautocomplete` to search for and add missing DOIs to the `.bib` file. |
| `-e {SECTION}` | Exclude a section from the CV. Sections include: `Grants`, `PersonalAwards`, `Conference`, `GradAdvisees`, `Proposals`, `UndergradResearch`, `Reviews`, `Refereed`, `Invited`, `Service`, `Teaching`, `Book`, `Patent`, `StudentAwards`, `Journal`. |
| `-d {PATH TO DATA DIRECTORY}` | Override the default data directory location specified in the config file. |
| `-f {PATH TO CONFIGURATION FILE}` | Specify a configuration file. Defaults to `make_cv.cfg`. |
| `-F {NAME}` | Override data file location in config file for specific sections.  Format is `-F NAME=<file name>` where NAME can be `Scholarship`, `PersonalAwards`, `StudentAwards`, `Service`, `Reviews`, `CurrentGradAdvisees`, `GradTheses`, `UndergradResearch`, `Teaching`, `Proposals`, `Grants`. |
| `-S {SCRAPERID}` | Specify the `ScraperID` (optional, but helps avoid Google blocking requests). |
| `-s {true,false}` | Use scraper to avoid Google blocking. |
| `-C {true,false}` | Include citation counts in the CV. |
| `-M {true,false}` | Include student author markers in the CV. |
| `-T`  | Include the last update timestamp at the bottom of the CV. If the flag is passed, it adds a timestamp to indicate the last update of the CV. |
| `-orc {NUMBER OF YEARS}` | Search for and add new entries from ORCID to the `.bib` file for the past specified number of years.  Use `-orc -1` to search for all available entries. Defaults to 1 if used without specifying a number. |
| `-orcid {ORCID}` | Override `ORCID` specified in config file. |
| `-y` | Set number of years of data to use in generating cv or far or collaborator list |
| `-n` | No clean up \- leave files generated by XeLaTeX (for debugging purposes) |

For example, the following will look for any new google scholar entries in the 4 last years, help you categorize them, then update the citation counts using google scholar, update the student markers, and exclude the proposals and conferences section when making a c.v.

`make_cv -g 4 -c true -m true -e Conference -e Proposals`

Most of the advanced features are by default off, but you can turn them on by default by editing the make\_cv.cfg file in your CV folder.  I usually only use the advanced features intermittently so I leave the advanced features off by default and then use the command line options when I need to use them.

The first time you run make\_cv it will find unclassified entries in your .bib file and ask you to classify them.  This will also happen if you add an entry from some other search source and it is not classified.  This modifies the keywords in the .bib file.  The categories determine in what sections that item will appear in the c.v.  If there is something appearing in the wrong section, use Bibdesk or Jabref to put the entry in the correct category.  (A drag and drop operation in BibDesk.  See Appendix F for Jabref instructions).  One of the categories is ignore, which should be chosen if you want to keep the entry in the .bib file but you don’t want it to appear in the c.v.

If you add `-g`, it will use Google Scholar to find any entries that have appeared in the last year and ask you if you want to add them.  Everything in google scholar has an id, so it keeps track of these in the .bib file and will never ask you to add an entry twice.  It also uses these id tags when it updates the number of citations an entry has.  It will use bibtexautocomplete to add doi information to the new entries.  The doi’s appear as hyperlinks in the c.v. so people can click on an entry in your c.v. and be taken to the corresponding web location for that item.

If you add `-m true`, it uses the files “undergraduate research data.xlsx”, “thesis data.xlsx” and “current student data.xlsx” to find the first initial and last names of all of your student advisees.  It then adds a marker after those names in the .bib file.  The two markers are \\us for undergraduate student and \\gs for graduate student.  The actual symbol that these commands create is defined in the `settings.sty` file.  Currently, make\_cv is configured to mark these authors in perpetuity, meaning that if you have a student who was an undergraduate advisee that became a graduate advisee, then you published with them 10 years later, that author will still receive both an undergraduate and a graduate advisee student marker.  On occasion, you may have students with the same last name & first initial.  To disambiguate these situations, you can append the latex command \\un{\<letter\>} to the last name wherever it appears (typically in the bib file & the above .xls files) where letter is just a unique letter.  This will disappear on typesetting but allows one to force a unique match i.e J Smith\\un{a} will only match to lastnames of Smith\\un{a} in the .bib file.

If you add `-M false`, it will redefine the \\us and \\gs markers so that no markers are produced in the file. This is also configurable in the `make_cv.cfg` file with the entry includestudentmarkers.

If you add `-c true`, it will use google scholar to update/add the field “citations” in the .bib file.  This is the number of times this article has been cited.  It will appear in brackets after the bibliographic entry in the c.v.  i.e.

19. N. Bagheri-Sadeghi+, B. T. Helenbrook, and K. D. Visser. “Ducted Wind Turbine Optimization and Sensitivity to Rotor Position”, Wind Energy Science 3, no. 1 (Apr. 2018), pp. 221–229. doi: 10.5194/wes-3-221-2018. \[42\]

This can also be turned on and off with `-C` flag or by using the entry includecitationcounts in the `make_cv.cfg` file.

`-I true` will use bibtexautocomplete to search for DOI’s that are missing from the .bib file.  It will add the doi then add a record btacqueried to the .bib file so it will never try to find the doi for that entry again.

### make\_nsfcoa \- NSF Collaborator List

When applying for grants from the National Science Foundation (NSF), faculty members are often required to submit information regarding their PhD Advisees and Collaborators.

- **PhD Advisees**: A list of doctoral students supervised by the faculty member, including names and start dates.  
    
- **Collaborators**: A list of researchers with whom the faculty member has collaborated on publications within a specified time frame.

make\_nsfcoa can generate these lists by using the following command.

`make_nsfcoa -y 4 -fmt xlsx`

- **`-y`**: Specifies the number of **years** for which collaborators are listed. The default is 4 years, but this can be adjusted to include collaborators from the last n years.  
    
- **`-fmt`**: Determines the output format, which can be either `xlsx` or `csv`. The default output format is `xlsx`.

### Appendix A: Python & LaTex Installation Instructions

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
`cat ~/.venv/bin/activate >> .zprofile`

##### Windows Installation

Install python from Windows App Store

Install LaTeX from [https://miktex.org/download](https://miktex.org/download).  When installing LaTeX change the default paper size to letter and also click “automatically install missing packages” (something like that anyway).  If you choose to only install for yourself you will have to open the MikTeX Console program and click “Settings” in the left side bar, then the “Directories” tab,  copy the “Link target directory” and add it to the path. (See below for modifying the Windows path).  Probably easier to install for all users but that has not been tested.

Add the python scripts path to your environment variables as well.  The path should have printed out when you installed make\_cv (at the end of the long spew of text. If you can’t find it, pip uninstall make\_cv and then pip install make\_cv and it should print again).  It should be something like: `C:\Users\<username>\AppData\Local\Programs\Python\Python38\Scripts`

 If you don’t want to do this, you can also just type `python -m make_cv.make_cv` or `python -m make_cv.make_far` etc... 

This is how to add to the path in Windows:

1. Type “Environment Variables” in the search bar (bottom left) and click on “Edit the system environment variables”  
2. Click the “Environment Variables” button  
3. In the list click on the “PATH” variable  
4. Click “Edit…”  
5. Click “New” and then paste the path you want to add

### Appendix B: Instructions for modifying your scholarship.bib file with Jabref

If you use the scholarship.bib template file, Jabref will show you the categorization of all entries in the left sidebar by default.  If it is not showing, under the “View” menu make sure “Groups” has a check mark next to it.  Right click on the “All Entries” group in the left side bar.  Choose “Add subgroup”, give the group the name “Categories”, Choose “Collect By” “Specified Keywords” dialog, then “Generate groups from keywords in the following field” and type “keywords” for the field to group by.  For the delimiter put a semicolon, then hit ok.   This should make your current categories show in the left side bar.  Save the file so you won’t have to do this again the next time you open it. 

To edit the category of an entry (journal,conference,refereed conference…), select the entry by left clicking on it, then right click on the category in the left hand side bar you would like to either add or remove the entry from. You will then see options to “Add selected entries to this group” or “Remove selected entries from this group”.

To change the bibtex type of an entry (This is different than the group, these are defined by bibtex and are things like “article,inproceedings,conference,miscellaneous, etc…  It tells bibtex what type of data to expect for this entry,) click on the intended entry and wait for the bottom window to update. On the left hand side of the bottom window you will see a small pencil symbol, click on that and hover over the words “BibTeX” or “IEEETran”. Under these two sections you will see the different types of entries show up, select the choose entry type by left clicking on the word.

To edit an entry itself, all you need to do is click on the entry, wait for the bottom window to update, and click through the different sections to edit them. Be sure to click on the “Generate” button next to the Citation Key section (under “Required Fields”) after updating an entry to ensure that the key is up to date.

Jabref can try to import entries from a text citation list.  It's a little sketchy but can save a lot of work if you have a list of invited talks you want converted.  There is a menu entry under the “Library” menu called “New entry from plain text”  Follow the instructions from there.

