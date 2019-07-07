import pandas as pd 
import re
import string
import math

def repl_func(m):
    """process regular expression match groups for word upper-casing problem"""
    return m.group(1) + m.group(2).upper()

input_file = "savedrecs.txt"
data = pd.read_csv(input_file, skiprows=3)
data["Authors"] = data["Authors"].replace("Addicoat, Matthew;", "Addicoat, Matthew A.;") 
data["Source Title"] = data["Source Title"].str.title()
data.sort_values(by=["Publication Year"], ascending=False, inplace=True)
#print(data.dtypes)

#Journal abbreviation
journal_abbrev_file = "journal_abbrev.txt"
ja_dict = {}
translator = str.maketrans('', '', string.punctuation)
with open(journal_abbrev_file) as jafile:
    lines = jafile.readlines()
    for line in lines:
        journal,abbreviation = line.split('=')
        key = journal.lower().strip()
        key = key.translate(translator)
        key = key.translate({ord(c): None for c in string.whitespace})
        ja_dict[key] = abbreviation.strip()


journal_IF_file = "JournalHomeGrid.csv"
ifdata = pd.read_csv(journal_IF_file, skiprows=1)
ifdata["Full Journal Title"] = ifdata["Full Journal Title"].str.lower().str.replace(' ', '').str.replace('-,&','')
jif_dict = ifdata.set_index("Full Journal Title").to_dict()["Journal Impact Factor"]
#print(jif_dict)

output_file = "publist.html"

with open(output_file, 'w') as htmlout:
    # Headers
    print("<head>",file=htmlout)
    print("<meta http-equiv=Content-Type content=\"text/html; charset=utf-8\">",file=htmlout)
    print("<style>",file=htmlout)
    print("<!--",file=htmlout)
    print(" /* Font Definitions */",file=htmlout)
    print("@font-face",file=htmlout)
    print("    {font-family:\"Century Gothic\";",file=htmlout)
    print("    panose-1:2 11 5 2 2 2 2 2 2 4;",file=htmlout)
    print("    mso-font-charset:0;",file=htmlout)
    print("    mso-generic-font-family:swiss;",file=htmlout)
    print("    mso-font-pitch:variable;",file=htmlout)
    print("    mso-font-signature:647 0 0 0 159 0;}",file=htmlout)
    print("</head>",file=htmlout)
    print("",file=htmlout)
    print("<body>",file=htmlout)

    for rec in data.itertuples():
        print("<p><span style='font-size:10.0pt'>",file=htmlout)
        these_authors = rec.Authors.split(';')
        this_string = ""
        for author in these_authors:
            if "Addicoat" in author:
                this_string += " <b><i>Addicoat, M. A.</i></b>;"
            else:
                (lastname,othernames) = author.split(',')
                this_string += (lastname+', ')
                names = othernames.split()
                initials_string = ""
                for name in names[:-1]:
                    initials_string += (name[0].upper()+'. ')
                initials_string += (names[-1][0].upper()+'.')
                this_string += (initials_string+';')

        print(this_string[:-1], file=htmlout, end ='')
        print("<br>", file=htmlout)
        s = re.sub("(^|\s)(\S)", repl_func, rec.Title)
        s += "<br>"
        print(s, file=htmlout)

        #munge the journal title:
        #Because of the space, Journal Title becomes _6
        this_key = rec._6.lower().replace(' ', '').replace('-,&','')
        try:
            print(ja_dict[this_key], file=htmlout, end='')
        except KeyError:
            print(rec._6, file=htmlout, end='')
        
        #now make up a string with <b>vol/b>, first_page (year)
        #some things may not exist and first_page might be article_number
        #Publication Year => _8
        #Beginning Page => _14
        #Ending Page => _15
        #Article Number => _16
        this_string = ", <b>"
        try:
            this_string += str(int(rec.Volume))
        except ValueError:
            this_string += " "
        this_string += "</b>, "
        #print(rec._14, type(rec._14))
        try:
            if math.isnan(rec._14):
                this_string += str(rec._16)
        except TypeError:
            this_string += str(rec._14)
#        else:
#            print("Here!")
#            this_string += str(rec._16)
        this_string += " ("
        this_string += str(rec._8)
        this_string += ")<br>"
        print(this_string, file=htmlout)

        #Now, the small print
        print("<span style='font-size:8.0pt'>", file=htmlout)
        # DOI:
        this_string = "DOI: "+str(rec.DOI)+"<br>"
        print(this_string, file=htmlout)
        
        #Impact factor and citations
        #Total Citations => _20
        this_string = "Impact Factor: "
        try:
            this_string += str(jif_dict[this_key])
        except KeyError:
            print(this_key)
            this_string += "N/A"
        this_string += "<span style='mso-tab-count:2'> Citations: "
        this_string += str(rec._20)
        this_string += "</span></p>"
        print(this_string, file=htmlout)

    print("</body>", file=htmlout)

# Code graveyard

#jif_dict = {}
#with open(journal_IF_file) as jiffile:
#    lines = jiffile.readlines()
#    for line in lines:
#        journal,IF = line.split('\t')
#        key = journal.lower().strip()
#        key = key.translate(translator)
#        key = key.translate({ord(c): None for c in string.whitespace})
#        
#        try:
#            jif_dict[key[:30]] = float(IF)
#        except ValueError:
#            jif_dict[key[:30]] = "N/A"

#        this_key = rec._6.lower().strip()
#        this_key = this_key.translate(translator)
#        this_key = this_key.translate({ord(c): None for c in string.whitespace})
