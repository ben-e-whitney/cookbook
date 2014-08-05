import xml.etree.ElementTree as ET
import re
import inflect

XML_NAME = 'recipebook.xml'
TEX_NAME = 'cookbook_content.tex'
UNIT_SUBSTITUTION_NAME = 'units.xml'
ENGINE = inflect.engine()

def None_to_empty(string):
    #TODO: test `input` directly?
    return '' if string is None else string

def get_unit_substitutions(unit_substitution_name):
    tree = ET.parse(unit_substitution_name)
    root = tree.getroot()
    substitutions = {}
    return {unit.find('longform').text: unit.find('abbreviation').text
            for unit in root}
#TODO: this is ugly.
UNIT_SUBSTITUTIONS = get_unit_substitutions(UNIT_SUBSTITUTION_NAME)

def fraction_substitute(string):
    pattern = r'Fraction\((?P<numerator>[0-9]+),\s*(?P<denominator>[0-9]+)\)'
    repl    = r'\(\\frac{\g<numerator>}{\g<denominator>}\)'
    return re.sub(pattern, repl, string)

def treat_cookbook(root, cookbook):
    for section in root:
        treat_section(section, cookbook)
    return None

def treat_section(section, cookbook):
    section_title = section.find('title').text
    cookbook.write('\n\chapter{{{sti}}}\n'.format(sti=section_title))
    for recipe in section.iter('recipe'):
        treat_recipe(recipe, cookbook)
    return None

def treat_recipe(recipe, cookbook):
    recipe_title = recipe.find('title').text
    cookbook.write('\section*{{{rti}}}\n'.format(rti=recipe_title))
    treaters = {
        'ingredientlist': treat_ingredientlist,
        'preparation': treat_preparation,
        'recipeinfo': treat_recipeinfo,
        #TODO: how to best to this? Maybe just chop off title bit?
        'title': lambda x, y: None,
    }
    for element in recipe:
        #title has already been taken care of.
        #TODO: use polymorphism here? Doesn't seem to merit a class.
        try:
            treaters[element.tag](element, cookbook)
        except KeyError:
            print(element.text)
            print(recipe.text)
            raise KeyError('Unrecognized element tag {tag}.'.format(
                tag=element.tag))
    return None

def treat_ingredientlist(ingredientlist, cookbook,
                         unit_substitutions=UNIT_SUBSTITUTIONS, engine=ENGINE):
    cookbook.write('\\begin{itemize}\n')
    #TODO: here and above, figure out what object to use to preserve order.
    ingred_keys = ('quantity', 'unit', 'fooditem', 'foodprep')
    for ingred in ingredientlist:
        #TODO: make this all cleaner.
        ingred_dict = {key: ingred.find(key).text for key in ingred_keys}
        #TODO: test `foodprep` directly?
        if ingred_dict['foodprep'] is not None:
            ingred_dict['foodprep'] = '({fpr})'.format(fpr=ingred_dict[
                'foodprep'])
        #TODO: also do plurals of unit, only if there isn't a substitution.
        ingred_dict['unit'] = unit_substitutions.get(ingred_dict['unit'],
                                                     ingred_dict['unit'])
        ingred_dict['quantity'] = fraction_substitute(None_to_empty(
            ingred_dict['quantity']))
        #TODO: figure out how to do this.
        if ingred_dict['unit'] is None:
            #TODO: do we need to use try/except here in case the comparison
            #fails? This will all be rewritten.
            if ingred_dict['quantity'] != 1:
                ingred_dict['fooditem'] = ENGINE.plural_noun(ingred_dict[
                    'fooditem'])
                print(ingred_dict['fooditem'])
        cookbook.write('\item {con}\n'.format(con=' '.join(
            None_to_empty(ingred_dict[key]) for key in ingred_keys)))
    cookbook.write('\\end{itemize}\n')
    return None

def treat_preparation(element, cookbook):
    cookbook.write('{elt}\n'.format(elt=fraction_substitute(element.text)))
    return None

def treat_recipeinfo(info, cookbook):
    keys = ('author', 'blurb', 'preptime', 'yield')
    pieces = {key: info.find(key).text for key in keys}
    #TODO: test the author directly?
    if pieces['author'] is not None:
        pieces['author'] = 'Author: {aut}.'.format(aut=pieces['author'])
    # Awkward way of maintaining order of the pieces.
    cookbook.write('\n'.join(None_to_empty(pieces[key]) for key in keys))
    return None

def main():
    tree = ET.parse(XML_NAME)
    root = tree.getroot()
    with open(TEX_NAME, 'w') as cookbook:
        cookbook.write(
            r'\documentclass{book}\usepackage{cookbook}\begin{document}'
        )
        treat_cookbook(root, cookbook)
        cookbook.write(r'\end{document}')
    return None

if __name__ == '__main__':
    main()
