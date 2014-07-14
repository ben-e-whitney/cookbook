import glob,sys,codecs,pickle

def get_argument(str):
#at this point doesn't recognize comments
#if the command was \command{argument}, str should be "argument}"
    lbracket_count,rbracket_count = 1,0
    char_index,argument = 0,""
    while lbracket_count != rbracket_count:
        character = str[char_index]
        if character == "{":
            lbracket_count = lbracket_count+1
        elif character == "}":
            rbracket_count = rbracket_count+1
        argument = argument+character
        char_index = char_index+1
    return argument[:-1]

def make_tag(tagname,tagtype,endline):
    str1,str2 = "<",">"
    if tagtype == "end":
        str1 += "/"
    if tagtype == "emptyelement":
        str2 = "/"+str2
    if endline:
        str2 += "\n"
    return str1+tagname+str2

def write_tag(tagname,tagtype,endline):
    XMLwrite(make_tag(tagname,tagtype,endline))
    LineWritten = True
    return None

def parse_line(line):
    global lbracket_count,rbracket_count,InElement,LineWritten,end_tags
    LineWritten = False
    if "\\recipe{" in line:
        return None
    lbracket_count += line.count("{")
    rbracket_count += line.count("}")
    #environment used loosely -- it's actually a TeX command,
    #but before I went with XML I planned to change it
    for environment,tag in zip(("ingredients","instructions"),\
("ingredientlist","preparation")):
        starter_str = "\\"+environment+"{"
        if starter_str in line:
            write_tag(tag,"start",True)
            InElement,LineWritten = True,True
            #LineWritten probably unneccesary because of the return None
            end_tags.append(make_tag(tag,"end",True))
            lbracket_count -= line.count("{")-1
            #-1 is because we should keep the "{" from e.g. "\\ingredients{"
            rbracket_count -= line.count("}")
            #This is necessary because we'll be recounting the piece of
            #the line we're passing recursively to parse_line.
            parse_line(line.partition(starter_str)[-1])
            return None
    for command,index in zip(("by","serves"),(0,3)):
        command = "\\"+command+"{"
        if command in line:
            command_tuple = line.partition(command)
            LineWritten = True
            recipe_info[index] = get_argument(command_tuple[-1])
            #argument = get_argument(command_tuple[-1])
            #if argument != "":
            #    recipe_info[index] = argument
            return None
    if lbracket_count == rbracket_count and InElement:
    #can InElement be replaced by end_tags? whether its length is
    #nonzero, but apparently [] has a specific True/False value, too
        index = line.rfind("}")
        XMLwrite(line[:index])
        LineWritten,InElement = True,False
        end_tags.reverse()#last in, first out
        if end_tags != []:
            xml.seek(-1+xml.seek(0,2))
            str = xml.read(1)
            if str != "\n":
                xml.write("\n")
            xml.seek(0,2)
        for end_tag in end_tags:
            XMLwrite(end_tag)
        XMLwrite(line[index+1:])
        end_tags = []
    if not LineWritten:
        XMLwrite(line)
        LineWritten = True
    return None

def deepest_environment(end_tags):
    if end_tags == []:
        return None
    else:
        tag = end_tags[-1]
        for i in ("<",">","/","\n"):
            tag = tag.replace(i,"")
        return tag

def XMLwrite(text):
    for str1,str2 in zip(commands,replacements):
        text = text.replace(str1,str2)
    if text == "%\n" or (text == "\n" and (not(InElement) or \
deepest_environment(end_tags) != "preparation")):
        pass
    elif "\\ingred{" in text:
        write_tag("ingredient","start",True)
        responses = []
        ResponseSuccess = False
        while not(ResponseSuccess):
            print("\n"*2+line.replace("\n",""))
            ResponseSuccess = True#innocent till proven guilty
            for tag in ("quantity","unit","fooditem","foodprep"):
                try:
                    response = input(tag+": ")
                except KeyboardInterrupt:
                    print("OK, just try again.")
                    ResponseSuccess = False
                    break
                else:
                    responses.append(response)
                    if response == "":
                        write_tag(tag,"emptyelement",True)
                    else:
                        write_tag(tag,"start",False)
                        XMLwrite(response)
                        write_tag(tag,"end",True)
        write_tag("ingredient","end",True)
        responses.insert(0,line)
        ingredients.append(responses)
    else:
        xml.write(text)
    return None

ingredients = []
commands = ("\\gal","gal.","\\lb","lb.","\\g","\C","\\mL","\\pt","pt.",\
"\\floz","fl. oz.","\\oz","oz.","\\half","\\third","\\twothirds","\\quarter",\
"\\threequarters","\\times","\\t","\\T","\\deg","\\ ","$","\\'e","\\~n",\
"\\c c","\\o ")
replacements = ("gallon","gallon","pound","pound","gram","cup","milliliter",\
"pint","pint","fluid ounce","fluid ounce","ounce","ounce","Fraction(1,2)",\
"Fraction(1,3)","Fraction(2,3)","Fraction(1,4)","Fraction(3,4)"," by ","teaspoon",\
"tablespoon","˚"," ","","é","ñ","ç","ø")
#the order of replacement is important so I can't use a dictionary
#e.g. don't want to replace "\\t" before "\\third"
cookbook_dir = "/Users/bew/Documents/Personal/Things/Cookbook/"
recipebook_xml = "/Users/bew/Documents/Personal/Things/recipebook.xml"
xml = open(recipebook_xml,encoding="utf-8",mode="w+")
XMLwrite("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE recipe PUBLIC "-//Happy-Monkey//DTD RecipeBook//EN"
"http://www.happy-monkey.net/recipebook/recipebook.dtd">\n""")
write_tag("cookbook","start",True)

recipe_info_tags = ("author","blurb","preptime","yield")
for folder in glob.glob(cookbook_dir+"*"):
    write_tag("section","start",True)
    folder_names = folder.split("/")
    write_tag("title","start",False)
    XMLwrite(folder_names[-1])
    write_tag("title","end",True)
    for file in glob.glob(folder+"/*"):
        write_tag("recipe","start",True)
        recipe = open(file,encoding="utf-8",mode="r")
        recipe_str  = recipe.read()
        if recipe_str.count("\\recipe") > 1:
            sys.exit("Too many recipe titles in "+recipe+".")
        title_tuple = recipe_str.partition("\\recipe{")
        write_tag("title","start",False)
        XMLwrite(get_argument(title_tuple[-1]))
        write_tag("title","end",True)
        lbracket_count,rbracket_count = 0,0
        InElement,LineWritten = False,False
        end_tags,recipe_info = [],["","","",""]
        #author, blurb, preptime, yield for recipe_info
        recipe.seek(0)
        for line in recipe:
            parse_line(line)
        if recipe_info == ["","","",""]:
            write_tag("recipeinfo","emptyelement",True)
        else:
            write_tag("recipeinfo","start",True)
            for info,tag in zip(recipe_info,recipe_info_tags):
                if info != "":
                    write_tag(tag,"start",False)
                    XMLwrite(info)
                    write_tag(tag,"end",True)
                else:
                    write_tag(tag,"emptyelement",True)
            write_tag("recipeinfo","end",True)
        write_tag("recipe","end",True)
    write_tag("section","end",True)

write_tag("cookbook","end",False)
xml.close()

file = open("/Users/bew/Desktop/ingredients","bw")
pickle.dump(ingredients,file)
file.close()
