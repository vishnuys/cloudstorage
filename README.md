# Cloud Computing Project: Scalable Distributed Object Storage with Consistent Hashing
### Storage Node with Replication for Object Storage that recieves tasks from LoadBalancer and performs the operations Create/Delete Buckets and Create/Update/Delete Files.
Implementation of the characterstics of [Amazon Dynamo Paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) like Consistent Hashing, Sloppy Quorum and Hinted Handoff as REST based Object storage service. 
#### Requirements:
- Python 3
- [Cloud Load Balancer Repository](https://github.com/vishnuys/cloudloadbalancer)
- List of Neighboring/All Nodes and their addresses available in the system depending on the Replication Factor assigned in Load Balancer conf file.

#### Installation:
1) Clone the Storage repo into all the available Storage Nodes and follow the below instructions in each node
2) Create a virtualenv `StorageNode` and activate it. If you do not have virtualenv installed, install it. (Installation: [Windows](https://thinkdiff.net/python/how-to-install-python-virtualenv-in-windows/), [Linux & MAC OS](https://medium.com/@garimajdamani/https-medium-com-garimajdamani-installing-virtualenv-on-ubuntu-16-04-108c366e4430))
3) In the project home folder, Install the necessary packages using the command `pip install -r requirements` .
4) Create `conf.py` in `cloud` folder.
5) Add the following code to `conf.py`
    ```python
    NODE_NAME = <Name of the Storage Node>
    AVAILABLE_NODES = [{<Each neighboor node name as key and its corresponding address as its value>}]
    ```
6) Execute the following command to apply migrations: `python manage.py migrate`.
7) To run the server on local IP assigned with default port, execute the command `python manage.py runserver 0.0.0.0:8000`. 

#### Usage:
This REST API doesn't have any authentication. To access this API, send a **POST** request using any request managers like Postman to specified address given below to the loadbalancer's address.

- **Create Bucket:** 
        - *URL*: `/create/bucket/`
        - *Request Body*: 'name' = <Bucket name>
        - *Result*:  `{status: <Success/Failure>, node: <Node at which the bucket was created>}`
- **Delete Bucket:** 
        - *URL*: `/delete/bucket/`
        - *Request Body*: 'name' = <Bucket name>
        - *Result*:  `{status: <Success/Failure>, node: <Node at which the bucket was deleted>}`
- **Create File:** 
        - *URL*: `/create/file/`
        - *Request Body*: 'name' = <File name>, 'bucket' = <Bucket name>, 'file' = <File to be Stored>
        - *Result*:  `{status: <Success/Failure>, node: <Node at which the file was created>, vector_clocks: {<Vector Clock of each node after file creation>}}`
- **Update File:** 
        - *URL*: `/update/file/`
        - *Request Body*: 'name' = <File name>, 'bucket' = <Bucket name>, 'file' = <File to be Updated>
        - *Result*:  `{status: <Success/Failure>, node: <Node at which the file was updated>, vector_clocks: {<Vector Clock of each node after file updation>}}`
- **Delete File:** 
        - *URL*: `/delete/file/`
        - *Request Body*: 'name' = <File name>, 'bucket' = <Bucket name>
        - *Result*:  `{status: <Success/Failure>, node: <Node at which the file was deleted>}`

You can learn more about APIs and how to use them [here](https://schoolofdata.org/2013/11/18/web-apis-for-non-programmers/).
