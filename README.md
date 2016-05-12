# ArcSight
Scripts for enhancing ArcSight


I adapted the Web Services API to a command line client.  It works with Python 3.4  To generate the service dict's for use in an interactive shell you first need to run the functions to grab the service URL's and then process the WSDL's.  This is not necessary for the command line use.

 

**Example Use:**
```bash
C:\Users\user\Documents\ArcSight\Dev>python ./ArcSight_ESM_WebServices_API_Client.py -m esm -u admin -s ActiveListService -c getEntries -o resourceId=H-gxUvkwBABCRvFGFq5Z0Ng==

Password:
```
```python
['resourceId=H-gxUvkwBABCRvFGFq5Z0Ng==']

{'authToken': 'PfDwZEGhFVADIwqKb78SsND5_fjnV3zJETKYt6460MQ.', 'resourceId': 'H-gxUvkwBABCRvFGFq5Z0Ng=='}
```
```javascript
https://esm:8443/www/manager-service/rest/ActiveListService/getEntries?&authToken=PfDwZEGhFVADIwqKb78SsND5_fjnV3zJETKYt6460MQ.&resourceId=H-gxUvkwBABCRvFGFq5Z0Ng==&alt=json
```
```python
{u'act.getEntriesResponse': {u'act.return': {u'columns': [u'name', u'targetAddress', u'targetZone']}}}
```
