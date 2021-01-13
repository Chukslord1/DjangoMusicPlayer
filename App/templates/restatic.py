import codecs
import sys
import os
from bs4 import BeautifulSoup as Soup

def parse_html(file_name, output_file, framework="flask", supported_tags=["link", "script", "img", "video"]):
    # accounting for cases where someone enters a different casing
    framework = framework.lower()

    def parse_tags(tag):
        # parse every tag and return the restatic format
        def parse_doc(doc):
            # parse the actual document and format as either flask or django
            # if no document is found, return back unformatted
            if doc == None:
                return doc
            else:
                if framework == "flask":
                    doc = "{{ url_for('static', filename = '" + doc + "') }}"
                elif framework == "django":
                    doc = "{% static '" + doc + "' %}"
                else:
                    print("Unknown framework {} passed".format(framework))
                return doc

        # account for different tags having different source locations
        try:
            if tag.name == "link":
                doc_link = tag["href"]
            elif tag.name in ["script", "img", "video"]:
                doc_link = tag["src"]
            else:
                doc_link = None
        except:
            doc_link = None

        if doc_link == None:
            return str(tag)
        else:
            return str(tag).replace(doc_link, parse_doc(doc_link))

    # read and parse the html to beautiful soup
    html = open(file_name, "r").read()
    html_soup = Soup(html, "html.parser")

    # iterate through every occurence of the tags and replace with the formatted values
    for i in html_soup.find_all(supported_tags):
        i.replace_with(Soup(parse_tags(i), "html.parser"))

    # write back the file
    clean_html = html_soup.prettify()
    if framework == "django":
        # account for django compulsory 'load static'
        clean_html = "{% load static %}\n\n" + clean_html

    codecs.open(output_file, "w", "utf-8").write(clean_html)
    print("Successfully formatted '{}' to {} template".format(file_name, framework))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("""python restatic.py <file.html> <flask|django>""")
        print("""python restatic.py . <flask|django>""")
        print("""python restatic.py <file.html> <flask|django> <output.html>""")
    else:
        # support to convert all files in current folder
        if sys.argv[1] == ".":
            all_html = [file for file in os.listdir(".") if file.split(".")[-1] == "html"]
            for html in all_html:
                parse_html(html, html, sys.argv[2])
        else:
            try:
                output_file = sys.argv[3]
            except:
                output_file = sys.argv[1]
            parse_html(sys.argv[1], output_file, sys.argv[2])
