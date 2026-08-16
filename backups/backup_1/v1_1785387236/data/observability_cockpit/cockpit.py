#!/data/data/com.termux/files/usr/bin/python3
"""
Observability Cockpit
Service A/B/C → Push traces → Agent → Collects and pushes traces → Observability Cockpit
Based on Observability Cockpit architecture diagram
"""
import json
import time
import uuid
import logging
import threading
from pathlib import Path
from datetime import datetime
from collections import deque

logging.basicConfig(level=logging.INFO, format='%(asctime)s [OBSERVABILITY] %(message)s')
logger = logging.getLogger(__name__)

class Trace:
    """Represents a distributed trace"""
    def __init__(self, trace_id, service_name, operation):
        self.trace_id = trace_id
        self.service_name = service_name
        self.operation = operation
        self.start_time = datetime.now()
        self.duration_ms = 0
        self.status = "ok"  # ok, error
        self.tags = {}
        self.logs = []
        self.spans = []

    def add_span(self, span_name, duration_ms):
        """Add a span to the trace"""
        span = {
            "span_id": str(uuid.uuid4())[:8],
            "name": span_name,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
        self.spans.append(span)
        self.duration_ms += duration_ms
        return span

    def add_tag(self, key, value):
        """Add tag to trace"""
        self.tags[key] = value

    def add_log(self, message, level="info"):
        """Add log entry"""
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "level": level
        })

    def complete(self, status="ok"):
        """Complete the trace"""
        self.status = status
        self.duration_ms = (datetime.now() - self.start_time).total_seconds() * 1000

    def get_trace_info(self):
        return {
            "trace_id": self.trace_id,
            "service": self.service_name,
            "operation": self.operation,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "spans": len(self.spans),
            "tags": self.tags,
            "logs": len(self.logs)
        }

class Service:
    """A service that generates traces"""
    def __init__(self, service_name):
        self.service_name = service_name
        self.traces_generated = 0
        self.agent = None

    def set_agent(self, agent):
        """Set the agent to push traces to"""
        self.agent = agent

    def generate_trace(self, operation):
        """Generate a trace for an operation"""
        trace_id = f"trace_{int(time.time())}_{self.traces_generated}"
        trace = Trace(trace_id, self.service_name, operation)

        # Simulate operation with spans
        trace.add_span(f"{operation}.init", random.uniform(1, 5))
        trace.add_span(f"{operation}.process", random.uniform(10, 100))
        trace.add_span(f"{operation}.complete", random.uniform(1, 5))

        trace.complete()
        self.traces_generated += 1

        # Push trace to agent
        if self.agent:
            self.agent.receive_trace(trace)

        return trace

class TraceAgent:
    """Agent that collects and pushes traces to Observability Cockpit"""
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.traces_collected = 0
        self.traces_pushed = 0
        self.trace_buffer = deque(maxlen=1000)
        self.cockpit = None

    def set_cockpit(self, cockpit):
        """Set the observability cockpit"""
        self.cockpit = cockpit

    def receive_trace(self, trace):
        """Receive trace from service"""
        self.trace_buffer.append(trace)
        self.traces_collected += 1
        logger.debug(f"Trace received: {trace.trace_id} from {trace.service_name}")

    def push_traces(self):
        """Push collected traces to cockpit"""
        while self.trace_buffer:
            trace = self.trace_buffer.popleft()
            if self.cockpit:
                self.cockpit.store_trace(trace)
            self.traces_pushed += 1

        logger.info(f"Traces pushed: {self.traces_pushed}")

    def get_agent_status(self):
        return {
            "agent_id": self.agent_id,
            "traces_collected": self.traces_collected,
            "traces_pushed": self.traces_pushed,
            "buffer_size": len(self.trace_buffer)
        }

class ObservabilityCockpit:
    """Observability Cockpit that stores and analyzes traces"""
    def __init__(self):
        self.traces = {}
        self.services = {}
        self.operations = {}
        self.created = datetime.now().isoformat()

    def store_trace(self, trace):
        """Store a trace"""
        self.traces[trace.trace_id] = trace

        # Index by service
        if trace.service_name not in self.services:
            self.services[trace.service_name] = []
        self.services[trace.service_name].append(trace.trace_id)

        # Index by operation
        if trace.operation not in self.operations:
            self.operations[trace.operation] = []
        self.operations[trace.operation].append(trace.trace_id)

    def query_traces(self, service_name=None, operation=None, status=None):
        """Query traces with filters"""
        results = []

        for trace_id, trace in self.traces.items():
            if service_name and trace.service_name != service_name:
                continue
            if operation and trace.operation != operation:
                continue
            if status and trace.status != status:
                continue
            results.append(trace.get_trace_info())

        return results

    def get_service_stats(self):
        """Get statistics per service"""
        stats = {}
        for service_name, trace_ids in self.services.items():
            traces = [self.traces[tid] for tid in trace_ids]
            avg_duration = sum(t.duration_ms for t in traces) / len(traces)
            error_count = len([t for t in traces if t.status == "error"])

            stats[service_name] = {
                "total_traces": len(traces),
                "avg_duration_ms": round(avg_duration, 2),
                "error_count": error_count,
                "error_rate": f"{(error_count / len(traces) * 100):.1f}%"
            }
        return stats

    def get_cockpit_status(self):
        return {
            "total_traces": len(self.traces),
            "services": len(self.services),
            "operations": len(self.operations),
            "service_stats": self.get_service_stats()
        }

class ObservabilityPipeline:
    """Complete observability pipeline"""
    def __init__(self):
        self.cockpit = ObservabilityCockpit()
        self.agent = TraceAgent("agent-01")
        self.agent.set_cockpit(self.cockpit)
        self.services = {}

    def add_service(self, service_name):
        """Add a service to the pipeline"""
        service = Service(service_name)
        service.set_agent(self.agent)
        self.services[service_name] = service
        logger.info(f"Service added: {service_name}")
        return service

    def simulate_traffic(self, operations_per_service=5):
        """Simulate traffic from all services"""
        for service_name, service in self.services.items():
            operations = ["handle_request", "process_data", "query_database", "send_response"]
            for i in range(operations_per_service):
                op = operations[i % len(operations)]
                service.generate_trace(op)

        # Push traces to cockpit
        self.agent.push_traces()

    def get_pipeline_status(self):
        return {
            "services": len(self.services),
            "agent": self.agent.get_agent_status(),
            "cockpit": self.cockpit.get_cockpit_status()
        }

# Import random for simulation
import random

if __name__ == "__main__":
    pipeline = ObservabilityPipeline()

    print("=== OBSERVABILITY COCKPIT DEMO ===\n")

    # Add services
    print("1. Adding services:")
    service_a = pipeline.add_service("Service A")
    service_b = pipeline.add_service("Service B")
    service_c = pipeline.add_service("Service C")
    print(f"   Services: {list(pipeline.services.keys())}\n")

    # Simulate traffic
    print("2. Simulating traffic:")
    print("   Service A/B/C → Push traces → Agent → Collects and pushes → Cockpit")
    pipeline.simulate_traffic(operations_per_service=10)
    print()

    # Query traces
    print("3. Querying traces:")
    all_traces = pipeline.cockpit.query_traces()
    print(f"   Total traces: {len(all_traces)}")
    for trace in all_traces[:5]:
        print(f"     - {trace['trace_id']}: {trace['service']}.{trace['operation']} ({trace['duration_ms']}ms)")
    print()

    # Service stats
    print("4. Service statistics:")
    stats = pipeline.cockpit.get_service_stats()
    for service, stat in stats.items():
        print(f"   {service}:")
        print(f"     Traces: {stat['total_traces']}")
        print(f"     Avg duration: {stat['avg_duration_ms']}ms")
        print(f"     Errors: {stat['error_count']} ({stat['error_rate']})")
    print()

    # Pipeline status
    print("5. Pipeline status:")
    status = pipeline.get_pipeline_status()
    print(f"   Services: {status['services']}")
    print(f"   Agent collected: {status['agent']['traces_collected']}")
    print(f"   Agent pushed: {status['agent']['traces_pushed']}")
    print(f"   Cockpit traces: {status['cockpit']['total_traces']}")

    print("\n=== OBSERVABILITY COCKPIT ARCHITECTURE ===")
    print("Service A/B/C → Push traces → Agent → Collects and pushes traces → Observability Cockpit")
    print("Features: Distributed tracing, service stats, error tracking")
