from azure.storage.blob import ContainerClient

def create_container(name):
    # connection and contaneer name
    conn_str = "DefaultEndpointsProtocol=https;AccountName=sletmig;AccountKey=Pwg8lb5XsQrhB7rFln4LnPT46hIu9F4AMkW0SqR+CTcl7Uz9h26seTd77C0buJj771auAjvzSg8f+AStvyrV+Q==;EndpointSuffix=core.windows.net"
    container_name = name

    # create ContainerClient-object
    container_client = ContainerClient.from_connection_string(conn_str=conn_str, container_name=container_name)

    # exist?
    if not container_client.exists():
        # create if not
        container_client.create_container()
        print(f"container '{container_name}' created")
    else:
        print(f"container '{container_name}' exist")

create_container("nihilnovumsubsolen")