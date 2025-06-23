# Message Broker

A simple in-app publish/subscribe (pub/sub) message broker module for Python. This library allows you to easily implement a message-based communication system within your Python application.

## Features

- Singleton design pattern ensures a single instance across the application.
- Publish messages to specific topics.
- Subscribe to topics with callback functions.
- Support for wildcard topic patterns.
- Thread-safe and lightweight.

## Installation

You can install the module directly from the public repository:

```bash
pip install git+https://github.com/Ekerim/message_broker.git
```

## Usage

### Singleton Design

The `MessageBroker` class is implemented as a singleton, meaning that all parts of your application will share the same instance. This makes it ideal for modular applications where different modules need to communicate with each other.

```python
from message_broker import MessageBroker

# Module A
broker_a = MessageBroker()
broker_a.subscribe("module_event", lambda msg: print(f"Module A received: {msg}"))

# Module B
broker_b = MessageBroker()
broker_b.publish({"topic": "module_event", "data": "Hello from Module B!"})

# Output: Module A received: Hello from Module B!
```

### Basic Example

```python
from message_broker import MessageBroker

# Create a MessageBroker instance
broker = MessageBroker()

# Define a callback function
def my_callback(message):
    print(f"Received message: {message}")

# Subscribe to a topic
broker.subscribe("my_topic", my_callback)

# Publish a message to the topic
broker.publish({"topic": "my_topic", "data": "Hello, World!"})

# Output: Received message: Hello, World!
```

### Using Wildcard Topics

You can use wildcard patterns (`*`) to subscribe to multiple topics:

```python
# Subscribe to all topics starting with "my_"
broker.subscribe("my_*", lambda msg: print(f"Wildcard received: {msg}"))

# Publish messages
broker.publish({"topic": "my_topic1", "data": "Message 1"})
broker.publish({"topic": "my_topic2", "data": "Message 2"})

# Output:
# Wildcard received: Message 1
# Wildcard received: Message 2
```

### Unsubscribing

To unsubscribe from a topic:

```python
broker.unsubscribe("my_topic")
```

### Stopping the Broker

To stop the message broker and clean up resources:

```python
broker.stop()
```

## License

This project is licensed under the GNU Lesser General Public License v3 (LGPLv3). See the [LICENSE](./LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Contact

For questions or support, please contact [ekerim@gmail.com](mailto:ekerim@gmail.com).
