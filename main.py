# -*- coding: utf-8 -*-

from urllib import request, parse, error
import http.cookiejar
import ssl
from jsonToTxt import *
import json
from bs4 import BeautifulSoup

context = ssl._create_unverified_context()
header = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'
}

def initOpener():
    cookie_file = 'cookie.txt'
    cookie = http.cookiejar.MozillaCookieJar()
    cookie.load(cookie_file, ignore_discard=True, ignore_expires=True)
    handler = request.HTTPCookieProcessor(cookie)
    opener = request.build_opener(handler)
    return opener

def saveJsonFile(content, fileName, rootPath='.'):
    path = rootPath + '/' + fileName

    with open(path, 'w', encoding = 'utf-8') as f:
        # 然后需要让ensure_ascii设置为False，则可以将中文以utf-8的格式写入
        json.dump(content, f, ensure_ascii = False)
    # f = open(path, 'w', encoding='utf-8')
    # if type(content) == type({}):
    #     content = json.dumps(content)
    # f.write(content)
    # f.close()

def readJsonFile(fileName, rootPath='.'):
    path = rootPath + '/' + fileName
    with open(path, encoding='utf-8') as file_object:
        contents = file_object.read()
        return contents

def requestQuestionInfo(opener, questionId):
    url = 'https://www.zhihu.com/question/{}'
    historyUrl = url.format(questionId)
    req = request.Request(url=historyUrl,headers=header)
    response = opener.open(req)

    content = response.read()
    soup = BeautifulSoup(content, 'lxml')

    for scroptTag in soup.find_all('script'):
        attrs = scroptTag.attrs
        id = attrs.get('id', None)
        if id == 'js-initialData':
            initialStateStr = scroptTag.string
            initialState = json.loads(initialStateStr)
            # print(initialState)
            initialStateObj = initialState['initialState']

            questionObj = initialStateObj['entities']['questions'][questionId]
            questionBody = {
                'questionBody': questionObj,
                'answerList': []
            }

            answerListUrl = initialStateObj['question']['answers'][questionId]['previous']

            return {
                'answerListUrl': answerListUrl,
                'questionBody': questionBody
            }


def answerListUrl(url='', limit=10, offset=0):
    # https://www.zhihu.com/api/v4/questions/35025502/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&sort_by=default
    # result = parse.urlparse(result)
    result = parse.urlparse(url)
    #url里的查询参数  
    query_dict = parse.parse_qs(result.query)
    newUrl = '{}://{}{}?include={}&limit={}&offset={}&sort_by=default'.format(result.scheme, result.netloc, result.path, query_dict['include'][0], limit, offset)
    
    return newUrl


def requestAnswerList(opener, url='', limit=10, offset=0):
    newUrl = answerListUrl(url, limit, offset)
    req = request.Request(url=newUrl,headers=header)
    response = opener.open(req)
    content = response.read().decode()
    return json.loads(content)


def getAllSymbol():
    jsonToTxt()
    opener = initOpener()
    with open('./cube_symbol.txt', encoding='utf-8') as file_object:
        line = file_object.readline()
        while line:
            res = requestQuestionInfo(opener, line)
            # {answerListUrl, questionBody}
            questionBody = res['questionBody']
            answerListUrl = res['answerListUrl']
            questionBody['answerList'] = requestAnswerList(opener, answerListUrl)['data']

            saveJsonFile(questionBody, '{}.json'.format(line), './jsonData')

            line = file_object.readline()

getAllSymbol()