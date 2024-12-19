"""
Real-time processing system.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import logging
import asyncio
from datetime import datetime

@dataclass
class UpdateEvent:
    id: str
    type: str
    content: Dict
    timestamp: datetime

class DocumentPreview:
    """Manages real-time document preview."""
    
    def __init__(self):
        self.content: str = ""
        self.version: int = 0
        self.last_update: datetime = datetime.now()
        self.observers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
    
    def update_content(self, content: str):
        """Update preview content."""
        self.content = content
        self.version += 1
        self.last_update = datetime.now()
        self._notify_observers()
    
    def add_observer(self, callback: Callable):
        """Add preview observer."""
        self.observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """Remove preview observer."""
        if callback in self.observers:
            self.observers.remove(callback)
    
    def _notify_observers(self):
        """Notify observers of content update."""
        for observer in self.observers:
            try:
                observer(self.content, self.version)
            except Exception as e:
                self.logger.error(f"Observer notification failed: {str(e)}")

class UpdateQueue:
    """Manages real-time update queue."""
    
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processors: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_processor(self, event_type: str, processor: Callable):
        """Register event processor."""
        self.processors[event_type] = processor
        self.logger.info(f"Registered processor for {event_type} events")
    
    async def push_event(self, event: UpdateEvent):
        """Push event to queue."""
        await self.queue.put(event)
        self.logger.debug(f"Pushed {event.type} event to queue")
    
    async def process_events(self):
        """Process events from queue."""
        while True:
            try:
                event = await self.queue.get()
                
                if event.type in self.processors:
                    processor = self.processors[event.type]
                    try:
                        await processor(event)
                        self.logger.debug(f"Processed {event.type} event")
                    except Exception as e:
                        self.logger.error(
                            f"Event processing failed for {event.type}: {str(e)}"
                        )
                else:
                    self.logger.warning(f"No processor for {event.type} events")
                
                self.queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Event processing error: {str(e)}")
                await asyncio.sleep(1)

class RealtimeSystem:
    """Manages real-time processing system."""
    
    def __init__(self):
        self.previews: Dict[str, DocumentPreview] = {}
        self.update_queue = UpdateQueue()
        self.logger = logging.getLogger(__name__)
        
        # Register default processors
        self.update_queue.register_processor(
            'content_update',
            self._handle_content_update
        )
        self.update_queue.register_processor(
            'preview_request',
            self._handle_preview_request
        )
    
    def create_preview(self, document_id: str) -> DocumentPreview:
        """Create new document preview."""
        if document_id in self.previews:
            raise ValueError(f"Preview already exists for {document_id}")
        
        preview = DocumentPreview()
        self.previews[document_id] = preview
        self.logger.info(f"Created preview for document {document_id}")
        return preview
    
    def get_preview(self, document_id: str) -> DocumentPreview:
        """Get existing preview."""
        if document_id not in self.previews:
            raise ValueError(f"No preview found for {document_id}")
        return self.previews[document_id]
    
    async def update_document(self, document_id: str, content: str):
        """Update document content."""
        event = UpdateEvent(
            id=document_id,
            type='content_update',
            content={'document_id': document_id, 'content': content},
            timestamp=datetime.now()
        )
        await self.update_queue.push_event(event)
    
    async def request_preview(self, document_id: str):
        """Request document preview."""
        event = UpdateEvent(
            id=document_id,
            type='preview_request',
            content={'document_id': document_id},
            timestamp=datetime.now()
        )
        await self.update_queue.push_event(event)
    
    async def _handle_content_update(self, event: UpdateEvent):
        """Handle content update event."""
        document_id = event.content['document_id']
        content = event.content['content']
        
        try:
            preview = self.get_preview(document_id)
            preview.update_content(content)
            self.logger.debug(f"Updated content for document {document_id}")
        except Exception as e:
            self.logger.error(f"Content update failed: {str(e)}")
    
    async def _handle_preview_request(self, event: UpdateEvent):
        """Handle preview request event."""
        document_id = event.content['document_id']
        
        try:
            preview = self.get_preview(document_id)
            self.logger.debug(f"Handled preview request for {document_id}")
            return preview.content
        except Exception as e:
            self.logger.error(f"Preview request failed: {str(e)}")
    
    async def start(self):
        """Start real-time processing system."""
        self.logger.info("Starting real-time processing system")
        await self.update_queue.process_events()
    
    def stop(self):
        """Stop real-time processing system."""
        self.logger.info("Stopping real-time processing system")
