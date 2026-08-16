#!/data/data/com.termux/files/usr/bin/python3
"""
NATS Message Pipeline
Shell Script Producer → NATS Server → NATS Trigger → Consumer Function
Object Container for image/PDF storage
Based on NATS pipeline diagram
"""
import json
import time
import hashlib
import logging
import threading
from pathlib import Path
from datetime import datetime
from collections import deque

logging.basicConfig(level=logging.INFO, format='%(asctime)s [NATS-PIPELINE] %(message)s')
logger = logging.getLogger(__name__)

class ObjectContainer:
    """Object storage container for images and PDFs"""
    def __init__(self, container_name):
        self.container_name = container_name
        self.objects = {}
        self.storage_path = Path.home() / "constellation25" / "storage" / container_name
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def upload(self, object_name, content, content_type="application/octet-stream"):
        """Upload object to container"""
        obj_id = hashlib.sha256(f"{object_name}{time.time()}".encode()).hexdigest()[:16]
        
        obj_path = self.storage_path / obj_id
        with open(obj_path, 'wb') as f:
            if isinstance(content, str):
                f.write(content.encode('utf-8'))
            else:
                f.write(content)

        self.objects[obj_id] = {
            "name": object_name,
            "path": str(obj_path),
            "size": obj_path.stat().st_size,
            "content_type": content_type,
            "uploaded": datetime.now().isoformat(),
            "download_count": 0
        }

        logger.info(f"Object uploaded: {object_name} ({obj_id})")
        return obj_id

    def download(self, obj_id):
        """Download object from container"""
        if obj_id not in self.objects:
            return None

        obj = self.objects[obj_id]
        obj_path = Path(obj["path"])
        
        with open(obj_path, 'rb') as f:
            content = f.read()

        obj["download_count"] += 1
        logger.info(f"Object downloaded: {obj['name']}")
        return {
            "content": content,
            "name": obj["name"],
            "content_type": obj["content_type"]
        }

    def list_objects(self):
        return list(self.objects.values())

class NATSServer:
    """NATS message server"""
    def __init__(self, server_name="nats://localhost:4222"):
        self.server_name = server_name
        self.subjects = {}
        self.subscriptions = {}
        self.messages = deque(maxlen=10000)
        self.running = True

    def publish(self, subject, message):
        """Publish message to subject"""
        if subject not in self.subjects:
            self.subjects[subject] = []

        msg = {
            "subject": subject,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "seq": len(self.messages)
        }

        self.subjects[subject].append(msg)
        self.messages.append(msg)

        logger.info(f"Published to {subject}: {message}")
        return msg

    def subscribe(self, subject, callback):
        """Subscribe to subject"""
        if subject not in self.subscriptions:
            self.subscriptions[subject] = []

        self.subscriptions[subject].append(callback)
        logger.info(f"Subscribed to {subject}")

    def process_messages(self):
        """Process messages and trigger callbacks"""
        while self.running:
            if self.messages:
                msg = self.messages.popleft()
                subject = msg["subject"]

                if subject in self.subscriptions:
                    for callback in self.subscriptions[subject]:
                        try:
                            callback(msg)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")

            time.sleep(0.01)

    def stop(self):
        self.running = False

class NATSTrigger:
    """NATS Trigger that invokes consumer function on message"""
    def __init__(self, nats_server, consumer_function):
        self.nats_server = nats_server
        self.consumer_function = consumer_function
        self.triggered_count = 0

    def on_message(self, message):
        """Trigger consumer function on message"""
        self.triggered_count += 1
        logger.info(f"NATS Trigger invoked (count: {self.triggered_count})")
        
        # Invoke consumer function
        result = self.consumer_function.process(message)
        return result

class ConsumerFunction:
    """Consumer function that processes messages"""
    def __init__(self, object_container):
        self.object_container = object_container
        self.processed_count = 0
        self.results = []

    def process(self, message):
        """Process message (download image, convert to PDF, upload)"""
        self.processed_count += 1

        msg_data = message.get("message", {})
        action = msg_data.get("action")
        obj_id = msg_data.get("object_id")

        result = {
            "message_id": message.get("seq"),
            "action": action,
            "processed_at": datetime.now().isoformat(),
            "status": "success"
        }

        if action == "download_image":
            obj = self.object_container.download(obj_id)
            if obj:
                result["object_name"] = obj["name"]
                result["size"] = obj["size"]
                logger.info(f"Downloaded image: {obj['name']}")

        elif action == "upload_pdf":
            pdf_content = f"%PDF-1.4\nConverted from {obj_id}\n"
            new_obj_id = self.object_container.upload(
                f"converted_{obj_id}.pdf",
                pdf_content,
                "application/pdf"
            )
            result["pdf_object_id"] = new_obj_id
            logger.info(f"Uploaded PDF: {new_obj_id}")

        self.results.append(result)
        return result

class ShellScriptProducer:
    """Shell script that produces messages"""
    def __init__(self, nats_server):
        self.nats_server = nats_server
        self.messages_sent = 0

    def send_message(self, subject, message):
        """Send message to NATS server"""
        self.nats_server.publish(subject, message)
        self.messages_sent += 1
        logger.info(f"Shell script sent message to {subject}")

    def push_image(self, container, image_path):
        """Push image to object container and send message"""
        # Read image file
        with open(image_path, 'rb') as f:
            content = f.read()

        # Upload to container
        obj_id = container.upload(image_path, content, "image/jpeg")

        # Send message to NATS
        message = {
            "action": "download_image",
            "object_id": obj_id,
            "source": "shell_script"
        }

        self.send_message("image.processing", message)
        return obj_id

class NATSPipeline:
    """Complete NATS pipeline"""
    def __init__(self):
        self.nats_server = NATSServer()
        self.container = ObjectContainer("images")
        self.consumer = ConsumerFunction(self.container)
        self.trigger = NATSTrigger(self.nats_server, self.consumer)
        self.producer = ShellScriptProducer(self.nats_server)

        # Subscribe trigger to NATS
        self.nats_server.subscribe("image.processing", self.trigger.on_message)

        # Start message processor
        self.processor_thread = threading.Thread(target=self.nats_server.process_messages, daemon=True)
        self.processor_thread.start()

    def process_image(self, image_path):
        """Process image through pipeline"""
        # Shell script pushes image
        obj_id = self.producer.push_image(self.container, image_path)

        # Wait for processing
        time.sleep(0.1)

        return {
            "object_id": obj_id,
            "processed": self.consumer.processed_count,
            "results": self.consumer.results
        }

    def get_pipeline_status(self):
        return {
            "nats_server": self.nats_server.server_name,
            "subjects": len(self.nats_server.subjects),
            "subscriptions": len(self.nats_server.subscriptions),
            "objects": len(self.container.objects),
            "messages_processed": self.consumer.processed_count,
            "trigger_count": self.trigger.triggered_count
        }

if __name__ == "__main__":
    pipeline = NATSPipeline()

    print("=== NATS MESSAGE PIPELINE DEMO ===\n")

    # Create test image file
    test_image = Path.home() / "constellation25" / "test_image.jpg"
    with open(test_image, 'wb') as f:
        f.write(b"fake image content")

    print("1. Pipeline setup:")
    print(f"   NATS Server: {pipeline.nats_server.server_name}")
    print(f"   Object Container: {pipeline.container.container_name}")
    print(f"   Subscriptions: {list(pipeline.nats_server.subscriptions.keys())}\n")

    # Process image
    print("2. Processing image through pipeline:")
    print("   Shell Script Producer → Push Image → Object Container")
    print("   Shell Script Producer → Send Message → NATS Server")
    print("   NATS Trigger → Consumer Function → Download Image → Upload PDF\n")

    result = pipeline.process_image(str(test_image))
    print(f"   Object ID: {result['object_id']}")
    print(f"   Processed: {result['processed']} messages")
    print(f"   Results: {len(result['results'])}\n")

    # Pipeline status
    print("3. Pipeline status:")
    status = pipeline.get_pipeline_status()
    print(f"   Subjects: {status['subjects']}")
    print(f"   Subscriptions: {status['subscriptions']}")
    print(f"   Objects stored: {status['objects']}")
    print(f"   Messages processed: {status['messages_processed']}")
    print(f"   Trigger invocations: {status['trigger_count']}")

    print("\n=== NATS PIPELINE ARCHITECTURE ===")
    print("Shell Script Producer → NATS Server → NATS Trigger → Consumer Function")
    print("Object Container: Store images, download for processing, upload PDFs")
