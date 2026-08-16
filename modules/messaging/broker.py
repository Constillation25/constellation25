#!/data/data/com.termux/files/usr/bin/python3
"""
Kafka-Style Message Broker
Producer → Kafka Brokers → Consumer architecture with ZooKeeper coordination
Supports push/pull messaging pattern
"""
import json
import time
import threading
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [BROKER] %(message)s')
logger = logging.getLogger(__name__)

class ZooKeeper:
    """ZooKeeper coordination service for broker cluster"""
    def __init__(self):
        self.brokers = {}
        self.topics = {}
        self.consumers = {}
        self.leader_elections = {}

    def register_broker(self, broker_id, host, port):
        """Register a broker in the cluster"""
        self.brokers[broker_id] = {
            "id": broker_id,
            "host": host,
            "port": port,
            "status": "online",
            "registered": datetime.now().isoformat(),
            "topics": []
        }
        logger.info(f"Broker registered: {broker_id} ({host}:{port})")
        return self.brokers[broker_id]

    def create_topic(self, topic_name, partitions=3, replication_factor=2):
        """Create a topic with partitions"""
        self.topics[topic_name] = {
            "name": topic_name,
            "partitions": partitions,
            "replication_factor": replication_factor,
            "created": datetime.now().isoformat(),
            "messages": 0,
            "brokers": list(self.brokers.keys())[:replication_factor]
        }
        logger.info(f"Topic created: {topic_name} ({partitions} partitions)")
        return self.topics[topic_name]

    def register_consumer(self, consumer_id, group_id, topics):
        """Register a consumer group"""
        self.consumers[consumer_id] = {
            "id": consumer_id,
            "group_id": group_id,
            "topics": topics,
            "status": "active",
            "registered": datetime.now().isoformat(),
            "offsets": {}
        }
        logger.info(f"Consumer registered: {consumer_id} (group: {group_id})")
        return self.consumers[consumer_id]

    def get_cluster_status(self):
        return {
            "brokers": len(self.brokers),
            "topics": len(self.topics),
            "consumers": len(self.consumers),
            "broker_details": self.brokers,
            "topic_details": self.topics
        }

class KafkaBroker:
    """Individual Kafka broker"""
    def __init__(self, broker_id, zookeeper):
        self.broker_id = broker_id
        self.zk = zookeeper
        self.topics = defaultdict(list)  # topic -> [messages]
        self.message_log = []

    def receive_message(self, topic, message):
        """Receive message from producer (push)"""
        msg = {
            "offset": len(self.topics[topic]),
            "topic": topic,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "broker": self.broker_id
        }

        self.topics[topic].append(msg)
        self.message_log.append(msg)

        # Update ZooKeeper topic stats
        if topic in self.zk.topics:
            self.zk.topics[topic]["messages"] += 1

        logger.debug(f"Message received on {topic} (offset {msg['offset']})")
        return msg

    def serve_message(self, topic, consumer_id, offset=0):
        """Serve message to consumer (pull)"""
        messages = self.topics.get(topic, [])

        if offset >= len(messages):
            return None

        msg = messages[offset]

        # Update consumer offset in ZooKeeper
        if consumer_id in self.zk.consumers:
            self.zk.consumers[consumer_id]["offsets"][topic] = offset + 1

        return msg

    def get_topic_stats(self, topic):
        return {
            "topic": topic,
            "message_count": len(self.topics.get(topic, [])),
            "broker": self.broker_id
        }

class Producer:
    """Message producer (Front End, Service)"""
    def __init__(self, producer_id, brokers):
        self.producer_id = producer_id
        self.brokers = brokers  # List of KafkaBroker instances
        self.messages_sent = 0

    def push(self, topic, message):
        """Push message to Kafka brokers"""
        # Round-robin across brokers
        broker = self.brokers[self.messages_sent % len(self.brokers)]
        result = broker.receive_message(topic, message)
        self.messages_sent += 1

        logger.info(f"Producer {self.producer_id} → {topic} (broker {broker.broker_id})")
        return result

class Consumer:
    """Message consumer (Hadoop, Monitoring, Data Warehouse)"""
    def __init__(self, consumer_id, brokers, zookeeper):
        self.consumer_id = consumer_id
        self.brokers = brokers
        self.zk = zookeeper
        self.messages_consumed = 0
        self.offsets = defaultdict(int)

    def pull(self, topic):
        """Pull message from Kafka brokers"""
        # Try each broker
        for broker in self.brokers:
            msg = broker.serve_message(topic, self.consumer_id, self.offsets[topic])
            if msg:
                self.offsets[topic] += 1
                self.messages_consumed += 1
                logger.info(f"Consumer {self.consumer_id} ← {topic} (broker {broker.broker_id}, offset {msg['offset']})")
                return msg
        return None

    def get_stats(self):
        return {
            "consumer_id": self.consumer_id,
            "messages_consumed": self.messages_consumed,
            "offsets": dict(self.offsets)
        }

class MessageBrokerCluster:
    """Complete Kafka-style cluster"""
    def __init__(self):
        self.zk = ZooKeeper()
        self.brokers = []
        self.producers = []
        self.consumers = []

    def setup_cluster(self, num_brokers=3):
        """Setup broker cluster"""
        for i in range(num_brokers):
            broker_id = f"broker-{i+1}"
            broker = KafkaBroker(broker_id, self.zk)
            self.zk.register_broker(broker_id, "localhost", 9092 + i)
            self.brokers.append(broker)

        logger.info(f"Cluster setup: {num_brokers} brokers")

    def create_topic(self, name, partitions=3):
        return self.zk.create_topic(name, partitions)

    def add_producer(self, name):
        producer = Producer(name, self.brokers)
        self.producers.append(producer)
        return producer

    def add_consumer(self, name, group_id, topics):
        self.zk.register_consumer(name, group_id, topics)
        consumer = Consumer(name, self.brokers, self.zk)
        self.consumers.append(consumer)
        return consumer

    def get_cluster_status(self):
        return {
            "zookeeper": self.zk.get_cluster_status(),
            "producers": len(self.producers),
            "consumers": len(self.consumers),
            "total_messages": sum(len(b.message_log) for b in self.brokers)
        }

if __name__ == "__main__":
    cluster = MessageBrokerCluster()

    print("=== KAFKA-STYLE MESSAGE BROKER DEMO ===\n")

    # Setup cluster
    print("1. Setting up cluster:")
    cluster.setup_cluster(num_brokers=3)
    print(f"   Brokers: {len(cluster.brokers)}\n")

    # Create topics
    print("2. Creating topics:")
    cluster.create_topic("user-events", partitions=3)
    cluster.create_topic("system-logs", partitions=3)
    print(f"   Topics: {len(cluster.zk.topics)}\n")

    # Add producers (Front End, Service)
    print("3. Adding producers:")
    frontend1 = cluster.add_producer("Front-End-1")
    frontend2 = cluster.add_producer("Front-End-2")
    service1 = cluster.add_producer("Service-1")
    print(f"   Producers: {len(cluster.producers)}\n")

    # Add consumers (Hadoop, Monitoring, Data Warehouse)
    print("4. Adding consumers:")
    hadoop = cluster.add_consumer("Hadoop-Cluster", "analytics-group", ["user-events"])
    monitoring = cluster.add_consumer("Real-Time-Monitoring", "ops-group", ["system-logs"])
    warehouse = cluster.add_consumer("Data-Warehouse", "analytics-group", ["user-events", "system-logs"])
    print(f"   Consumers: {len(cluster.consumers)}\n")

    # Produce messages
    print("5. Producing messages:")
    for i in range(5):
        frontend1.push("user-events", {"event": "page_view", "user": f"user_{i}"})
        frontend2.push("user-events", {"event": "click", "user": f"user_{i}"})
        service1.push("system-logs", {"level": "INFO", "message": f"Log entry {i}"})

    print(f"   Messages sent: {frontend1.messages_sent + frontend2.messages_sent + service1.messages_sent}\n")

    # Consume messages
    print("6. Consuming messages:")
    for i in range(3):
        msg = hadoop.pull("user-events")
        if msg:
            print(f"   Hadoop: {msg['message']}")

    for i in range(3):
        msg = monitoring.pull("system-logs")
        if msg:
            print(f"   Monitoring: {msg['message']}")

    print()

    # Cluster status
    print("7. Cluster status:")
    status = cluster.get_cluster_status()
    print(f"   Brokers: {status['zookeeper']['brokers']}")
    print(f"   Topics: {status['zookeeper']['topics']}")
    print(f"   Producers: {status['producers']}")
    print(f"   Consumers: {status['consumers']}")
    print(f"   Total messages: {status['total_messages']}")

    print("\n=== KAFKA ARCHITECTURE ===")
    print("Producers (Front End, Service) → Push → Kafka Brokers → Pull → Consumers (Hadoop, Monitoring, Data Warehouse)")
    print("Coordinated by ZooKeeper")
