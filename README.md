# Consul Service Finder
I got a problem when I try to simulate multiple service register on Consul server and the client can find one of the services to use the API.

I can use below URL to get all services but that is not what I want.
<pre><code>curl http://localhost:8500/v1/agent/services</code></pre>

# Ideas

### * Consul Query to search service by service name
### * Count the service be used
### * Return min count of services by same service name

# Example
<pre><code>
    csf = ConsulServiceFinder()
    
    # create query by service name
    csf.createQueryByServiceName("microweb_microtalk", "q_test")

    # find one service and compose it's url
    csf.composeServiceUrl(csf.requestOneServiceByServiceName("microweb_microtalk"))
    
</code></pre>

