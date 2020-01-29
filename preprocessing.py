import pandas as pd
import re

def load_data():
    """
    reads the csv file.
    calls other functions, namely get_math_mark and standard_web_dev
    
    returns a clean dataframe 
    """

    df= pd.read_excel('data/Umuzi_Demographics_Aptitude_WebDevTest_(Responses)_short.xlsx', index_col='Timestamp')
    #get the clean digit for math level
    df['math_mark_clean']= df['math_mark'].apply(get_math_mark)
    #keep only one variation of web development
    df['department']= df.department.apply(standard_web_dev)

    df['Name']= df.Name.apply(cap_names)
    df['Surname']= df.Surname.apply(cap_names)
    return df

def cap_names(name):
    """
    this makes a word start with a capital letter

    parameters:
    name (string) : a name or a surname

    returns:
    name (string): first character of the name is a capital letter 
    
    """
    
    if name:
        return name.capitalize()

def standard_web_dev(department):
    """
    used to make coding/web development and web development one department.

    parameters:
    department (string): a department in umuzi
    
    returns:
    department (string): Web Development or department it got as input 
    if its not a code/web development
    """

    if department== 'Coding/Web Development':
        return 'Web Development'
    else:
        return department


def get_math_mark(code):
    """
    This just searches for a number and returns the fist one
    as it is the math code

    input:
    code (str): a string describing the level of their math results range
    returns:
    number (str): the first number
    """
    code= str(code)
    #reg= re.compile(r'\d+')
    matches= re.search(r'\d+', code)
    if matches:
        return matches.group() 
    
