import json
import requests

class CounterableData:
    def __init__(self, id=None, name=None):
        self.state = "init"
        self.used_count = 0
        self.id = id
        self.name = name
    def buildFail(self):
        self.state = "fail"
    def builded(self):
        self.state = "builded"
    def delete(self):
        self.state = "init"
    def isQueryAlive(self):
        return self.state == "builded"
    def used(self):
        self.used_count += 1
    def clearUsed(self):
        self.used_count = 0

class ConsulQuery(CounterableData):
    def __init__(self, query=None, id=None):
        super().__init__(id)
        self.query = query
        if self.query:
            self.name = self.query["Name"]

class ConsulNode(CounterableData):
    def __init__(self, node=None, id=None):
        super().__init__(id)
        self.node = node
        if self.node:
            self.name = self.node["Node"]

class ConsulService(CounterableData):
    def __init__(self, service=None, id=None):
        super().__init__(id)
        self.service = service
        if self.service:
            self.name = self.service["Service"]


class ConsulServiceFinder:
    def __init__(self, consul_ip="127.0.0.1", port=8500):
        self.consul_ip = consul_ip
        self.port = port
        self.consul_url = "http://" + consul_ip + ":" + str(port) + "/v1/"
        self.consul_query_dict = {}
        self.consul_service_dict = {}

    def queryLoadFromConsul(self):
        # curl http://localhost:8500/v1/query
        url = self.consul_url + "query"
        print("call API:", url)
        r = requests.get(url)
        query_rep = r.json()
        # print(query_rep)
        
        for q in query_rep:
            query_name = q["Name"]
            query = ConsulQuery(q, q["ID"])
            query.builded()
            self.consul_query_dict[query_name] = query
        
    def displayQuery(self):
        self.displayCounterableDatas(self.consul_query_dict, "Query")

    def displayService(self):
        self.displayCounterableDatas(self.consul_service_dict, "Service")

    def displayCounterableDatas(self, object_dict, object_type):
        for _, data in object_dict.items():
            self.displayCounterableData(data, object_type)
            # print(object_type, "[", data.id, ":", data.name, "] (", data.state, ",", data.used_count, ")")
    
    def displayCounterableData(self, data, object_type):
        print(object_type, "[", data.id, ":", data.name, "] (", data.state, ",", data.used_count, ")")

    def createQueryByServiceName(self, service_name, query_name=None):
        if not query_name:
            query_name = "query_" + service_name
        
        if query_name in self.consul_query_dict:
            consul_query = self.consul_query_dict[query_name]
        else:
            consul_query = ConsulQuery()

        query = {
            "Name": query_name,
            "Token": "",
            "Service": {
                "Service": service_name
            },
            "DNS": {
                "TTL": "10s"
            }
        }
        # print(query)
        consul_query.query = query

        # curl --request POST --data @query.json http://127.0.0.1:8500/v1/query
        url = self.consul_url + "query"
        print("call API:", url)
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(query), headers=headers)
        query_rep = r.json()
        # print(query_rep)
        if "ID" in query_rep:
            consul_query.id = query_rep["ID"]
            consul_query.builded()
        else:
            consul_query.buildFail()
        return consul_query

    def deleteQuery(self, query_name):
        if query_name not in self.consul_query_dict:
            print("[" + query_name + "] not in consul_query")
            return {}
        consul_query = self.consul_query_dict[query_name]
        if not consul_query.isQueryAlive():
            print("[" + query_name + "] not alive")
            return {}
        if not consul_query.id:
            print("[" + query_name + "] is is empty")
            return {}
        
        # curl --request DELETE http://127.0.0.1:8500/v1/query/faa52b08-a295-b20c-5d01-b237a46c9a2d
        url = self.consul_url + "query/" + consul_query.id
        print("call API:", url)
        # headers = {'Content-type': 'application/json'}
        r = requests.delete(url)
        query_rep = r.json()
        # print(query_rep)
        consul_query.delete()
        return query_rep

    def executeQuery(self, query_name):
        if query_name not in self.consul_query_dict:
            print("[" + query_name + "] not in consul_query")
            return {}
        consul_query = self.consul_query_dict[query_name]
        if not consul_query.isQueryAlive():
            print("[" + query_name + "] not alive")
            return {}

        # curl http://127.0.0.1:8500/v1/query/my-query-mt/execute?near=_agent
        url = self.consul_url + "query/" + query_name + "/execute?near=_agent"
        print("call API:", url)
        # headers = {'Content-type': 'application/json'}
        r = requests.get(url)
        query_rep = r.json()
        # print(query_rep)
        consul_query.used()
        return query_rep

    def requestOneService(self, query_name):
        query_rep = self.executeQuery(query_name)
        if "Nodes" in query_rep:
            nodes = query_rep["Nodes"]
            candidate_ids = []
            for node in nodes:
                if "Service" in node:
                    service = node["Service"]
                    id = service["ID"]
                    candidate_ids.append(id)
                    if id not in self.consul_service_dict:
                        consul_service = ConsulService(id=id, service=service)
                        consul_service.builded()
                        self.consul_service_dict[id] = consul_service
            
            if candidate_ids:
                candidate_ids_count = {id:self.consul_service_dict[id].used_count for id in candidate_ids}
                id = min(candidate_ids_count, key=candidate_ids_count.get)
                consul_service = self.consul_service_dict[id]
                print("-" * 40, id)
                self.displayCounterableData(consul_service, "Service")
                # print(self.composeServiceUrl(consul_service))
                return consul_service
        return {}

    def composeServiceUrl(self, consulService):
        return "http://" + consulService.service["Address"] + ":" + str(consulService.service["Port"])
                    

if __name__ == "__main__":
    cs = ConsulServiceFinder()
    cs.queryLoadFromConsul()
    cs.displayQuery()
    # query_name = "my-query-mt" 
    # cs.executeQuery(query_name)
    # consulService = cs.requestOneService(query_name)
    # print(cs.composeServiceUrl(consulService))
