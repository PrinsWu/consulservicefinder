import logging
import base64
from consul import Consul, ConsulException
from abc import abstractmethod

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class ConsulServiceFindStrategy:
    def __init__(self, name="ConsulServiceFindStrategy"):
        self.name = name
    @abstractmethod
    def find(self, csf, service_name):
        pass

class LessCountFindStrategy(ConsulServiceFindStrategy):
    def __init__(self, name="LessCountFindStrategy"):
        super().__init__(name)

    def find(self, csf, service_name):
        querys = csf.getQueryByServiceName(service_name)
        if not querys:
            return {"state": "fail", "message": "No query for the service_name."}
        
        # use first query
        query_name = querys[0]
        query_rep = csf.executeQuery(query_name)
        if "Nodes" in query_rep:
            nodes = query_rep["Nodes"]
            candidate_services = [] # tuple(service_id, service count)
            services = {} # {service_id: service json}
            for node in nodes:
                if "Service" in node:
                    service = node["Service"]
                    service_id = service["ID"]
                    candidate_services.append((service_id, csf.getServiceCount(service_id)))
                    services[service_id] = service
            
            if candidate_services:
                min_count_service = min(candidate_services, key = lambda service: service[1])
                service_id = min_count_service[0]
                service = services[service_id]
                # service["Address"] + ":" + str(service["Port"]
                # add service count
                csf.addServiceCount(service_id)
                return service
            else:
                log.info("candidate_services is empty!")
        else:
            log.info("Nodes is empty!")
        return {"state": "fail", "message": "Can't find a service by query."}


class ConsulServiceFinder:
    def __init__(self, consul:Consul=None, defaultFindStrategy=None):
        if not consul:
            consul = Consul()
        self.consul = consul
        if not defaultFindStrategy:
            self.defaultFindStrategy = LessCountFindStrategy()

    def listAgentServices(self):
        return self.consul.agent.services()

    def listCatalogServices(self):
        return self.consul.catalog.services()

    def listQuery(self):
        return self.consul.query.list()

    # kv: [query_name]: query_id,service_name
    # kv: [service_name]: query_name,..,...
    # kv: [service_id]: count
        
    def decodeValue(self, value):
        if type(value) is dict:
            return self.decodeValue(value["Value"])
        elif type(value) is bytes:
            return value.decode("utf-8")
        return value

    def createQueryByServiceName(self, service_name, query_name):
        # query = Consul.Query(self.consul)
        query = self.consul.query
        try:
            rep = query.create(service_name, query_name)
            log.debug("create Query:{}".format(query_name))

            if "ID" in rep:
                query_id = rep["ID"]
                # setup kv: [query_name]: query_id,service_name
                self.consul.kv.put(query_name, query_id + "," + service_name)
                # setup kv: [service_name]: query_name,..,...
                _, value = self.consul.kv.get(service_name)
                log.debug(value)
                if not value:
                    value = query_name
                else:
                    value = self.decodeValue(value) + "," + query_name
                self.consul.kv.put(service_name, value)
                
        except ConsulException as e:
            rep = query.explain(query_name)
            log.debug("explain Query:{}".format(query_name))
            return {"state": "fail", "message": str(e)}
        return rep

    def deleteQuery(self, query_name, clear=True):
        # delete kv: [query_name]: query_id,service_name
        _, value = self.consul.kv.get(query_name)
        if value:
            self.consul.kv.delete(query_name)
            value = self.decodeValue(value).split(",")
            query_id = value[0]
            try:
                # delete query
                self.consul.query.delete(query_id)
            except ConsulException as e:
                log.warn(str(e))
            
            if clear:
                service_name = value[1]
                # clear kv: [service_name]: query_name,..,...
                querys = self.getQueryByServiceName(service_name)
                querys.remove(query_name)
                if not querys:
                    self.consul.kv.delete(service_name)
                else:
                    value = ",".join(querys)
                    self.consul.kv.put(service_name, value)

    def deleteQueryByServiceName(self, service_name):
        querys = self.getQueryByServiceName(service_name)
        for query_name in querys:
            self.deleteQuery(query_name, clear=False)
        self.consul.kv.delete(service_name)

    def getQueryByServiceName(self, service_name):
        _, value = self.consul.kv.get(service_name)
        querys = self.decodeValue(value)
        if querys:
            return querys.split(",")
        else:
            return []

    def executeQuery(self, query_name):
        query = self.consul.query
        return query.execute(query_name)

    def executeQueryByServiceName(self, service_name, query_type="ALL"):
        querys = self.getQueryByServiceName(service_name)
        if "ALL" == query_type:
            rep = {}
            for query_name in querys:
                rep[query_name] = self.executeQuery(query_name)
        else:
            rep = self.executeQuery(querys[0])
        return rep

    def getServiceCount(self, service_id):
        _, value = self.consul.kv.get(service_id)
        if value:
            return int(self.decodeValue(value))
        
        self.consul.kv.put(service_id, str(0))
        return 0
    
    def addServiceCount(self, service_id):
        count = self.getServiceCount(service_id)
        count += 1
        self.consul.kv.put(service_id, str(count))
    
    def composeServiceUrl(self, service):
        return "http://" + service["Address"] + ":" + str(service["Port"])

    def requestOneServiceByServiceName(self, service_name, findStrategy=None):
        if not findStrategy:
            return self.defaultFindStrategy.find(self, service_name)
        return findStrategy.find(self, service_name)
    

if __name__ == "__main__":
    # pass
    log.setLevel(logging.DEBUG)
    csf = ConsulServiceFinder()
    # csf.deleteQueryByServiceName("microweb_microtalk")
    # log.debug(csf.createQueryByServiceName("microweb_microtalk", "q_test"))
    log.debug(csf.composeServiceUrl(csf.requestOneServiceByServiceName("microweb_microtalk")))
    # log.debug(csf.executeQuery("q_test"))
    # print(csf.listQuery())
    # print(csf.listAgentServices())
    # print(csf.executeQueryByServiceName("microweb_microtalk"))
