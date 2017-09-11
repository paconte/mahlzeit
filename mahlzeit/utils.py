"""
This file has some utils to work with files
"""
import getopt
import json
import os
import sys
import pandas as pd
import smtplib
import hashlib
from email.mime.text import MIMEText
from scrapy.utils.project import get_project_settings


settings = get_project_settings()
log_file = settings.get('LOG_FILE')
ingredients = ['vegan', 'vegetarian', 'fish']


def get_last_export_file(file_type='csv'):
    directory = settings['EXPORT_FILES']
    files = [f for f in os.listdir(directory) if 'mahlzeit' in f and file_type in f]
    last_file = files[0]
    for f in files[1:]:
        stat1 = os.stat(directory + last_file).st_mtime
        stat2 = os.stat(directory + f).st_mtime
        if stat2 > stat1:
            last_file = f
    return directory + last_file


def hash_file(filename):
    hash_func = hashlib.md5()
    with open(filename, 'rb') as f:
        buf = f.read()
        hash_func.update(buf)
    return hash_func.hexdigest()


def print_array(array):
    for x in array:
        print(x)


def get_file_size(filename):
    return os.stat(filename).st_size


def send_email(email_from, email_to):
    with open(log_file, 'rt') as fp:
        msg = MIMEText(fp.read())
    msg['Subject'] = 'Exceptions while crawling coolinarius.'
    msg['From'] = email_from
    msg['To'] = email_to
    server = smtplib.SMTP('localhost')
    server.sendmail(email_from, [email_to], msg.as_string())
    server.quit()


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
        x['name'] = x['name'].replace('"', '')
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
        output = output.replace(',,', ',')
        output = output.replace(',]{', ',{')
        output = output.replace('}][{', '},{')
        output = output.replace(',,,', ',')
        output = output.replace(',,', ',')

        # output = output.replace('&', 'und')
        dst.write('const productsAux = \'')
        dst.write(output)
        dst.write('\';\nconst products = JSON.parse(productsAux);\n')
        dst.write('export default products;\n')


def main(argv):
    script_name = 'intro.py'
    input_file = None
    output_file = None

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('%s -i <inputfile> -o <outputfile>' % script_name)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('%s -i <inputfile> -o <outputfile>' % script_name)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    if not input_file or not output_file:
        print('%s -i <inputfile> -o <outputfile>' % script_name)
        sys.exit()

    print('Input file is "%s"' % input_file)
    print('Output file is "%s"' % output_file)
    make_json_pipeline_output_javascript_friendly(input_file, output_file)


if __name__ == "__main__":
    main(sys.argv[1:])
