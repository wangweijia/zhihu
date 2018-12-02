import json

jsonFile = 'cookie.json'
textFile = 'cookie.txt'

def jsonToTxt():
    with open(jsonFile,'r') as load_f:
        load_dict = json.load(load_f)
        allText = '# Netscape HTTP Cookie File\n'
        for item in load_dict:
            domain = item['domain']

            path = item['path']
            secure = item['secure']
            name = item['name']
            value = item['value']

            secureStr = 'FALSE'
            if secure:
                secureStr = 'TRUE'

            domain_specified = 'FALSE'
            if domain.startswith("."):
                domain_specified = 'TRUE'

            txt = '{}\t{}\t{}\t{}\t''\t{}\t{}'.format(domain, domain_specified, path, secureStr, name, value)
            allText += '\n'
            allText += txt
        f = open(textFile, 'w', encoding='utf-8')
        f.write(allText)
        f.close()