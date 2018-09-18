# Consul Service Finder
I got a problem when I try to simulate multiple service register on Consul server and the client can find one of the services to use the API.

I can use below URL to get all services but that is not what I want.
<pre><code>curl http://localhost:8500/v1/agent/services</code></pre>

# Ideas

### * Consul Query to search service by name
### * Counte the service be used
### * Return min count of services by same service name

# Example
<pre><code>
    cs = ConsulServiceFinder()
    # load query information from Consul
    cs.queryLoadFromConsul()
    cs.displayQuery()
    # create query by service name
    service_name = "my-service"
    cs.createQueryByServiceName(service_name)
    query_name = "query_" + service_name 
    cs.executeQuery(query_name)
    # request one service from query
    consulService = cs.requestOneService(query_name)
    # compose service url from consulService object
    print(cs.composeServiceUrl(consulService))
</code></pre>

