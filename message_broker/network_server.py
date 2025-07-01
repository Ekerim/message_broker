# Copyright (c) 2025 Fredrik Larsson
# 
# This file is part of the Message Broker library.
# 
# The Message Broker library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# The Message Broker library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library. If not, see <https://www.gnu.org/licenses/>.

import threading
import logging
import msgpack
from typing import Dict, Any, Optional

from twisted.internet import reactor, protocol, endpoints
from twisted.python import log


class _NetworkServer:
    """
    Handles network communication for the MessageBroker using Twisted.
    Runs the Twisted reactor in a separate thread to avoid blocking.
    """
    
    def __new__(cls, message_broker, config: Dict[str, Any]):
        # Check if networking is enabled before creating instance
        networking_enabled = config.get('network', {}).get('enabled', False)
        if not networking_enabled:
            return None
        
        # Create the instance normally if networking is enabled
        return super().__new__(cls)
    
    def __init__(self, message_broker, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        
        self.message_broker = message_broker
        
        # Store origin ID locally for efficient access
        self._origin_id = self.message_broker._origin_id
        
        self.logger.debug(f"Network Server Initializing. (Origin ID: {self._origin_id})")
        
        self.config = config.get('network', {})
        
        # Network configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 50000)
        self.secret = self.config.get('secret', '')
        
        # Validate that secret is provided for security
        if not self.secret:
            raise ValueError("Network secret is required for secure communication. "
                           "Please provide a secret in the network configuration.")
        
        # Threading
        self._reactor_thread = None
        self._running = False
        
        # Start the network server immediately
        self._reactor_thread = threading.Thread(target=self._run_reactor, daemon=True)
        self._reactor_thread.start()
        
        # Only set running to True after thread is started
        self._running = True
        
        self.logger.info(f"Network Server Initialized for {self.host}:{self.port} (Origin ID: {self._origin_id})")
    
    def stop(self):
        """Stop the network server"""
        self.logger.debug(f"Network Server stopping. (Origin ID: {self._origin_id})")
        
        if not self._running:
            return
            
        self._running = False
        if reactor.running:
            reactor.callFromThread(reactor.stop)
        
        if self._reactor_thread and self._reactor_thread.is_alive():
            self._reactor_thread.join(timeout=5.0)
            
        self.logger.info(f"Network Server stopped. (Origin ID: {self._origin_id})")
    
    def _run_reactor(self):
        """Run the Twisted reactor in this thread"""
        try:
            # TODO: Set up protocol factory and endpoint
            # TODO: Start monitoring outgoing message queue
            # TODO: Set up authentication
            
            self.logger.debug("Network Server reactor starting")
            reactor.run(installSignalHandlers=False)
            self.logger.debug("Network Server reactor stopped")
            
        except Exception as e:
            self.logger.error(f"Error in reactor thread: {e}")
        finally:
            self._running = False
