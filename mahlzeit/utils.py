"""
This file has some utils to work with files
"""
import sys, getopt
import pandas as pd
import json

ingredients = ['vegan', 'vegetarian', 'fish']

def print_array(list):
    for x in list:
        print(x)

def _create_ingredients(string):
    result = list()
    if string and len(string) > 2:
        for i in range(len(ingredients)):
            if ingredients[i] in string.lower():
                result.append(ingredients[i])
    return result

def _write_json(dst_file, json_obj):
    f = open(dst_file, 'w')
    f.write('const productsAux = \'')
    json.dump(json_obj, f, ensure_ascii=False, separators=(',\' +\n\'', ': '))
    f.write('\';\nconst products = JSON.parse(productsAux);\n')
    f.write('export default products;\n')

def csv_to_json(src_file, dst_file):
    # load json
    df = pd.read_csv(src_file, header=0, sep=';;;', engine='python')
    json_string = df.to_json(orient='records')
    # create value arrays for ingredients / type
    json_obj = json.loads(json_string)
    for x in json_obj:
        x['type'] = _create_ingredients(x['type'])
        x['name'] = x['name'].replace('"','')
    # write to file
    _write_json(dst_file, json_obj)


def make_json_pipeline_output_javascript_friendly(src_file, dst_file):
    """
    Convert an exported json formated file into a JS constant
    Parameters:
    src_file : string : path to source file
    dst_file : string : path to destination file
    """
    with open(src_file, "r") as src, open(dst_file, "w") as dst:
        output = src.read().replace('ingredients', 'type')
        output = output.replace('dish', 'name')
        output = output.replace('}]{', '},{')
        output = output.replace('},[{', '},{')
        output = output.replace('][', ',')
        output = output.replace('}{', '},{')
        output = output.replace(',[]{', ',{')
        output = output.replace('[,', '')
        # output = output.replace('&', 'und')
        dst.write('const productsAux = \'')
        dst.write(output)
        dst.write('\';\nconst products = JSON.parse(productsAux);\n')
        dst.write('export default products;\n')


#csv_to_json('./data.csv', './test.js')


def main(argv):
    scriptname = 'intro.py'
    inputfile = None
    outputfile = None

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('%s -i <inputfile> -o <outputfile>' % scriptname)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('%s -i <inputfile> -o <outputfile>' % scriptname)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if not inputfile or not outputfile:
        print('%s -i <inputfile> -o <outputfile>' % scriptname)
        sys.exit()

    print('Input file is "%s"' % inputfile)
    print('Output file is "%s"' % outputfile)
    make_json_pipeline_output_javascript_friendly(inputfile, outputfile)


if __name__ == "__main__":
   main(sys.argv[1:])
