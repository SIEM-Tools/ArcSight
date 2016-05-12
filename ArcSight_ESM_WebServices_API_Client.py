import requests, httplib, re, json, getpass, argparse
from Dicts import service_dict
'''
copyright Jesse Marlon Bacon 05/06/2016
An ESM CLI
'''
requests.packages.urllib3.disable_warnings()

def stripOptions(Call, xml_data):
    strip_element = re.compile('\<xs:element name="{}"\>(.*?)\</xs\:element\>'.format(Call), re.DOTALL)
    match = strip_element.search(xml_data, re.DOTALL )
    raw_elements = match.group()
    if len(raw_elements)== 0:
        strip_element = re.compile('\<complexType name="{}"\>(.*?)\</\complexType\>'.format(Call), re.DOTALL)
        match = strip_element.search(xml_data, re.DOTALL )
        raw_elements = match.group()
    options_stripper = re.compile('name="(.*?)".*?type="(.*?)"')
    options = dict(options_stripper.findall(raw_elements))
    return options
def create_service_dict():
    for Service in service_dict.keys():
        print(Service)
        with open('./{}.xml'.format(Service), 'r') as f:
            print('Opened {}.xml for reading'.format(Service))
            xml_data = f.read()
        for Call in service_dict[Service].keys():
            service_dict[Service][Call] = stripOptions(Call, xml_data)
    return 'Updated service_dict to WSDL specs in current directory.'
def generateRestURLs(manager_host_name, service_dict):
    REST_URL_BASE = '/www/manager-service/services/'
    REST_URLs_dict = {}
    for service in service_dict.keys():
        REST_URLs_dict[service] = str('https://{}:8443'.format(manager_host_name) + REST_URL_BASE + \
                                    service + '?wsdl')
    return REST_URLs_dict
def grabWebServiceDescriptions(rest_URLs):
    for service in rest_URLs.keys():
        with open('{}.xml'.format(service), 'w') as f:
            data = requests.get(rest_URLs[service], verify=False).content
            f.write(data)
    return('Wrote WSDL files to current directory.')
def doLogin(manager_host_name, user_name):
    login_request_json = 'https://{}:8443/www/core-service/rest/LoginService/login?login={}&password={}&alt=json'\
    .format(manager_host_name, user_name, getpass.getpass())
    login_object_json = requests.get(login_request_json, verify=False)
    json_response = json.loads(login_object_json.content)
    token = json_response.values()[0]['log.return']
    return token
def doLogout(manager_host_name, user_name, token):
    logout_request = 'https://{}:8443/www/core-service/rest/LoginService/logout?login={}&authToken={}'\
    .format(manager_host_name, user_name, token)
    run_logout=requests.get(logout_request, verify=False)
    if run_logout.content == '':
        return 'Logged out user: {}'.format(user_name)
    else:
        return 'COuld not log out user: {}, consult manager log or client request log for further information.'
def getSession(manager_host_name, authToken):
    session_url = 'https://{}:8443/www/core-service/rest/LoginService/getSession?authToken={}'.format(manager_host_name, authToken)
    session_token_request = requests.get(session_url, authToken, verify=False)
    auth_token_stripper = re.compile('\<authToken\>(\S+)\</authToken\>')
    creationMillis_Stripper = re.compile('\<creationMillis\>(\d+)\</creationMillis\>')
    expirationMillis_Stripper = re.compile('\<expirationMillis\>(\d+)\</expirationMillis\>')
    userId_stripper = re.compile('\<userId\>(\d+)\</userId\>')
    authToken = auth_token_stripper.findall(session_token_request.content)[0]
    creationMillis = creationMillis_Stripper.findall(session_token_request.content)[0]
    expirationMillis = expirationMillis_Stripper.findall(session_token_request.content)[0]
    userId = userId_stripper.findall(session_token_request.content)[0]
    sessionToken = authToken + creationMillis + expirationMillis + userId
    return authToken, creationMillis, expirationMillis, userId, sessionToken
def queryCases(manager_host_name, authToken):
    '''Returns All Case IDs'''
    resource_request_json = 'https://{}:8443/www/manager-service/rest/CaseService/findAllIds?&authToken={}&alt=json'\
    .format(manager_host_name, authToken)
    print(resource_request_json)
    retrieve_list = requests.get(resource_request_json, verify=False)
    response = json.loads(retrieve_list.content)
    return response[u'cas.findAllIdsResponse']['cas.return']
def queryReports(manager_host_name, authToken):
    '''No error, no return'''
    resource_request_json = 'https://{}:8443/www/manager-service/rest/ReportService/findAllIds?&authToken={}&alt=json'\
    .format(manager_host_name, authToken)
    print(resource_request_json)
    retrieve_list = requests.get(resource_request_json, verify=False)
    response = json.loads(retrieve_list.content)
    return response[u'rep.findAllIdsResponse']['rep.return']
def queryActiveLists(manager_host_name, authToken):
    '''No error, no return'''
    resource_request_json = 'https://{}:8443/www/manager-service/rest/ActiveListService/findAllIds?&authToken={}&alt=json'\
    .format(manager_host_name, authToken)
    print(resource_request_json)
    retrieve_list = requests.get(resource_request_json, verify=False)
    response = json.loads(retrieve_list.content)
    return response['act.findAllIdsResponse']['act.return']
def queryActiveListByID(manager_host_name, authToken, resourceID):
    resource_request_json = 'https://{}:8443/www/manager-service/rest/ActiveListService/getResourceById?resourceId={}&authToken={}&alt=json'\
    .format(manager_host_name, resourceID, authToken)
    print(resource_request_json)
    retrieve_list = requests.get(resource_request_json, verify=False)
    response = json.loads(retrieve_list.content)
    return response['act.getResourceByIdResponse']['act.return']
def getListEntries(manager_host_name, authToken, resourceID):
    resource_request_json = \
    'https://{}:8443/www/manager-service/rest/ActiveListService/getEntries?resourceId={}&authToken={}&alt=json'\
    .format(manager_host_name, resourceID, authToken)
    print(resource_request_json)
    retrieve_list = requests.get(resource_request_json, verify=False)
    #return retrieve_list
    response = json.loads(retrieve_list.content)
    return response['act.getEntriesResponse']['act.return']
def GenericAPICall(manager_host_name, Service, Call, authToken, parameter_kv_pairs=None, json_return=True):
    if parameter_kv_pairs==None:
        resource_request_json = \
        'https://{}:8443/www/manager-service/rest/{}/{}?&authToken={}&alt=json'\
        .format(manager_host_name, Service, Call, authToken) 
    else:
        paramaters=''
        parameter_kv_pairs = parameter_kv_pairs.split(',')
        print(parameter_kv_pairs)
        kv_pairs = {}
        for pair in parameter_kv_pairs:
            k = pair.split('=', 1)
            kv_pairs[k[0]] = k[1]
        kv_pairs['authToken'] = authToken
        for entry in kv_pairs.keys():
            paramaters +='&' + entry + '=' + kv_pairs[entry]
        print(kv_pairs)
        resource_request_json = \
        'https://{}:8443/www/manager-service/rest/{}/{}?{}&alt=json'\
        .format(manager_host_name, Service, Call, paramaters)
    print(resource_request_json)
    retrieve_list = requests.get(resource_request_json, verify=False)
    if not json_return:
        return retrieve_list
    else:
        response = json.loads(retrieve_list.content)
        return response
def getRuleContent():
    pass
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI ArcSight ESM Access',prog='ESM_CLI', \
                                     usage='example: ArcSight_ESM_WebServices_API_Client.py -m esm -u admin -s ReportService -c findAll -j True')
    parser.add_argument('-m','--Manager-Host-Name', help='The Fully Qualified ESM Name', required=True)
    parser.add_argument('-u','--Manager-User-Name', help='The Credentialed ESM user name', required=True)
    parser.add_argument('-s','--API-Service-Name', help='The ESM Service with a corresponding WSDL', required=True)
    parser.add_argument('-c','--Service-Call-Name', help='The ESM API Call with a corresponding Web Service', required=True)
    parser.add_argument('-o','--Options-Dict', help='options such as resourceId=H-gxUvkwBABCRvFGFq5Z0Ng== in comma seperated format', required=False)
    parser.add_argument('-j', '--json', action='store_true')
    args = parser.parse_args()
    manager_host_name = args.Manager_Host_Name
    user_name = args.Manager_User_Name
    Service = args.API_Service_Name
    Call = args.Service_Call_Name
    options_pairs = args.Options_Dict
    json_return = args.json
    #print(generateRestURLs(manager_host_name, service_dict))
    authToken = doLogin(manager_host_name, user_name)
    authToken, creationMillis, expirationMillis, userId, sessionToken = getSession(manager_host_name, authToken)
    #options_dict = dict()
    response = GenericAPICall(manager_host_name, Service, Call, authToken, parameter_kv_pairs=options_pairs, json_return=True)
    print(response)
    doLogout(manager_host_name, user_name, authToken) 
###TODO###
#Dict of services, calls, and paramaters
#Command Line options
#Container Class
#Package Module
#__Main__ routine
#resource id's with + will not return