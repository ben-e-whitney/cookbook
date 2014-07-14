import xml.etree.ElementTree as ET

XML_NAME = 'recipebook.xml'
TEX_NAME = 'cookbook.tex'

def None_to_empty(string):
    #TODO: test `input` directly?
    return '' if string is None else string

def treat_cookbook(cookbook, cookbook_file):
    for section in cookbook:
        treat_section(section, cookbook_file)
    return None

def treat_section(section, cookbook_file):
    section_title = section.find('title').text
    cookbook_file.write('\n\chapter{{sti}}\n'.format(sti=section_title))
    for recipe in section.iter('recipe'):
        treat_recipe(recipe, cookbook_file)
    return None

def treat_recipe(recipe, cookbook_file):
    recipe_title = recipe.find('title').text
    cookbook_file.write('\section*{{rti}}\n'.format(rti=recipe_title))
    treaters = {
        'ingredientlist': treat_ingredientlist,
        'preparation': treat_preparation,
        'recipeinfo': treat_recipeinfo
    }
    for element in recipe:
        #title has already been taken care of.
        #TODO: use polymorphism here? Doesn't seem to merit a class.
        try:
            treaters[element.tag](element, cookbook_file)
        except KeyError:
            raise KeyError('Unrecognized element tag {tag}.'.format(
                tag=element.tag))
    return None

def treat_ingredientlist(ingredientlist, cookbook_file):
    cookbook_file.write('\\begin{itemize}\n')
    #TODO: here and above, figure out what object to use to preserve order.
    ingred_keys = ('quantity', 'unit', 'fooditem', 'prep')
    for ingred in ingredientlist:
        ingred_dict = {key: ingred.find(key).text for key in ingred_keys}
        #TODO: test `foodprep` directly?
        ingred_dict['foodprep'] = ingred_dict['foodprep'] if ingred_dict[
            'foodprep'] is None else '({fpr})'.format(fpr=ingred_dict[
            'foodprep'])
        cookbook_file.write('\item {con}\n'.format(con=' '.join(
            None_to_empty(ingred_dict[key]) for key in ingred_keys)))
    cookbook_file.write('\\end{itemize}\n')
    return None

def treat_preparation(element, cookbook_file):
    cookbook_file.write('{elt}\n'.format(elt=element.text))
    return None

def treat_recipeinfo(info, cookbook_file):
    keys = ('author', 'blurb', 'preptime', 'yield')
    pieces = {key: info.find(key).text for key in keys}
    #TODO: test the author directly?
    pieces['author'] = (pieces['author'] if pieces['author'] is None else
        'Author: {aut}.'.format(aut=pieces['author']))
    # Awkward way of maintaining order of the pieces.
    cookbook_file.write('\n'.join(pieces[key] for key in keys))
    return None

def main():
    cookbook_file = open(TEX_NAME, 'w')
    tree = ET.parse(XML_NAME)
    root = tree.getroot()
    treat_cookbook(root, cookbook_file)
    cookbook_file.close()
    return None

if __name__ == '__main__':
    main()
