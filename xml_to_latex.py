import xml.etree.ElementTree as ET
import time
xml_name = 'recipebook.xml'
tex_name = 'cookbook.tex'

def cookbook_treatment(cookbook):
    for section in root:
        section_treatment(section)
    return

def section_treatment(section):
    section_title = section.find('title').text
    file.write('\n\chapter{'+section_title+'}\n')
    for recipe in section.iter('recipe'):
        recipe_treatment(recipe)
    return

def recipe_treatment(recipe):
    recipe_title = recipe.find('title').text
    file.write('\section*{'+recipe_title+'}\n');
    for element in recipe:
        #title has already been taken care of.
        tag = element.tag
        if tag == 'ingredientlist':
            ingredientlist_treatment(element)
        elif tag == 'preparation':
            preparation_treatment(element)
        elif tag == 'recipeinfo':
            recipeinfo_treatment(element)
    return

def ingredientlist_treatment(ingredientlist):
    file.write('\\begin{itemize}\n')
    for ingred in ingredientlist:
        quantity = ingred.find('quantity').text
        unit     = ingred.find('unit').text
        fooditem = ingred.find('fooditem').text
        foodprep = ingred.find('foodprep').text
        foodprep = foodprep if (foodprep == None) else '('+foodprep+')'
        file.write('\item '+strNone(quantity)+strNone(unit)\
                +strNone(fooditem)+strNone(foodprep)+'\n')
    file.write('\\end{itemize}\n')
    return

def strNone(input):
    if input == None:
        return ''
    else:
        # Extra spaces don't hurt in TeX so I'll just add them willy-nilly.
        return ' '+input+' '

def preparation_treatment(element):
    file.write(element.text+'\n')
    return

def recipeinfo_treatment(info):
    author    = info.find('author').text
    author    = author if (author == None) else 'Author: '+author+'.'
    blurb     = info.find('blurb').text
    preptime  = info.find('preptime').text
    # Different variable name because 'yield' is a Python keyword.
    the_yield = info.find('yield').text
    file.write(strNone(author)+strNone(blurb)+strNone(preptime)+\
            strNone(the_yield)+'\n')
    return

file = open(tex_name,'w')
tree = ET.parse(xml_name)
root = tree.getroot()
cookbook_treatment(root)
file.close()
