"""
Text-to-Speech Module for BlindStick

This module provides text-to-speech functionality for announcing
detected objects and navigation instructions to the user.
"""

import os
import threading
from typing import Optional, List, Dict
from datetime import datetime
import queue


class TTSEngine:
    """
    Text-to-Speech engine for BlindStick.
    
    Supports multiple TTS backends (pyttsx3, gTTS) and provides
    asynchronous speech synthesis for real-time feedback.
    """
    
    def __init__(
        self,
        engine_type: str = 'pyttsx3',
        rate: int = 150,
        volume: float = 0.9,
        voice_id: Optional[int] = None
    ):
        """
        Initialize TTS engine.
        
        Args:
            engine_type: TTS backend ('pyttsx3' or 'gTTS')
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice ID (0 for male, 1 for female in pyttsx3)
        """
        self.engine_type = engine_type
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        
        # Speech queue for async processing
        self.speech_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
        # Initialize engine
        self._init_engine()
    
    def _init_engine(self):
        """Initialize the TTS engine."""
        if self.engine_type == 'pyttsx3':
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                
                # Set properties
                self.engine.setProperty('rate', self.rate)
                self.engine.setProperty('volume', self.volume)
                
                # Set voice
                voices = self.engine.getProperty('voices')
                if voices and self.voice_id is not None:
                    if 0 <= self.voice_id < len(voices):
                        self.engine.setProperty('voice', voices[self.voice_id].id)
                
                print(f"Initialized pyttsx3 engine")
                
            except ImportError:
                print("pyttsx3 not available, falling back to gTTS")
                self.engine_type = 'gTTS'
                self._init_engine()
                
        elif self.engine_type == 'gTTS':
            try:
                from gtts import gTTS
                self.gTTS_class = gTTS
                print(f"Initialized gTTS engine")
            except ImportError:
                print("gTTS not available!")
                raise ImportError("No TTS engine available. Install pyttsx3 or gTTS.")
    
    def speak(self, text: str, async_mode: bool = True, block: bool = False):
        """
        Speak a text message.
        
        Args:
            text: Text to speak
            async_mode: Whether to speak asynchronously
            block: Whether to block until speech completes (only if async_mode=False)
        """
        if async_mode:
            if not self.is_running:
                self.is_running = True
                self.worker_thread = threading.Thread(target=self._process_queue)
                self.worker_thread.daemon = True
                self.worker_thread.start()
            
            self.speech_queue.put(text)
        else:
            self._speak_text(text, block)
    
    def _process_queue(self):
        """Process speech queue."""
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=1.0)
                self._speak_text(text, block=True)
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS Error: {e}")
    
    def _speak_text(self, text: str, block: bool = False):
        """
        Actually speak the text.
        
        Args:
            text: Text to speak
            block: Whether to block until completion
        """
        try:
            if self.engine_type == 'pyttsx3':
                self.engine.say(text)
                if block:
                    self.engine.runAndWait()
                    
            elif self.engine_type == 'gTTS':
                tts = self.gTTS_class(text=text, lang='en', slow=False)
                
                # Save to temporary file
                temp_file = f"temp_speech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                tts.save(temp_file)
                
                # Play audio
                self._play_audio(temp_file, block)
                
                # Clean up
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def _play_audio(self, audio_file: str, block: bool = False):
        """Play audio file."""
        try:
            if self.engine_type == 'gTTS':
                try:
                    import playsound
                    if block:
                        playsound.playsound(audio_file)
                    else:
                        import threading
                        thread = threading.Thread(target=playsound.playsound, args=(audio_file,))
                        thread.daemon = True
                        thread.start()
                except ImportError:
                    # Fallback to system player
                    import subprocess
                    if os.name == 'nt':  # Windows
                        cmd = ['start', 'cmd', '/c', 'start', audio_file]
                    else:  # Linux/Mac
                        cmd = ['xdg-open', audio_file] if os.name == 'posix' else ['open', audio_file]
                    
                    if block:
                        subprocess.call(cmd)
                    else:
                        subprocess.Popen(cmd)
                        
        except Exception as e:
            print(f"Audio playback error: {e}")
    
    def stop(self):
        """Stop current speech and clear queue."""
        if self.engine_type == 'pyttsx3':
            try:
                self.engine.stop()
            except:
                pass
        
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
    
    def pause(self):
        """Pause speech (pyttsx3 only)."""
        if self.engine_type == 'pyttsx3':
            try:
                self.engine.setProperty('rate', 0)
            except:
                pass
    
    def resume(self):
        """Resume speech (pyttsx3 only)."""
        if self.engine_type == 'pyttsx3':
            try:
                self.engine.setProperty('rate', self.rate)
            except:
                pass
    
    def shutdown(self):
        """Shutdown TTS engine."""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        
        if self.engine_type == 'pyttsx3':
            try:
                self.engine.stop()
            except:
                pass


class SpeechAnnouncer:
    """
    High-level announcer for BlindStick.
    
    Provides methods for announcing detected objects,
    warnings, and navigation information.
    """
    
    def __init__(self, tts_config: Dict):
        """
        Initialize speech announcer.
        
        Args:
            tts_config: TTS configuration dictionary
        """
        self.tts = TTSEngine(
            engine_type=tts_config.get('engine', 'pyttsx3'),
            rate=tts_config.get('rate', 150),
            volume=tts_config.get('volume', 0.9),
            voice_id=tts_config.get('voice', 0)
        )
        
        # Announcement settings
        self.max_announcements = 5
        self.announcement_history = []
        self.min_interval = 2.0  # Minimum seconds between announcements
    
    def announce_objects(
        self,
        detections: List[Dict],
        priority_objects: Optional[List[str]] = None,
        max_objects: int = 3,
        include_distance: bool = True
    ):
        """
        Announce detected objects.
        
        Args:
            detections: List of detection dictionaries
            priority_objects: List of priority object names to announce first
            max_objects: Maximum number of objects to announce
            include_distance: Whether to include distance information
        """
        if not detections:
            return
        
        # Sort by confidence
        sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        # Prioritize important objects
        if priority_objects:
            priority_dets = []
            other_dets = []
            
            for det in sorted_dets:
                if det['name'].lower() in [obj.lower() for obj in priority_objects]:
                    priority_dets.append(det)
                else:
                    other_dets.append(det)
            
            sorted_dets = priority_dets + other_dets
        
        # Select top objects
        selected = sorted_dets[:max_objects]
        
        # Build announcement
        announcements = []
        for det in selected:
            msg = f"{det['name']}"
            if include_distance and det.get('distance', 0) > 0:
                msg += f" at {det['distance']} meters"
            announcements.append(msg)
        
        # Create final message
        if len(announcements) == 1:
            message = f"Detected {announcements[0]}"
        elif len(announcements) == 2:
            message = f"Detected {announcements[0]} and {announcements[1]}"
        else:
            message = f"Detected {', '.join(announcements[:-1])}, and {announcements[-1]}"
        
        self.speak(message)
    
    def announce_warning(self, warning_type: str, details: str = ""):
        """
        Announce a warning.
        
        Args:
            warning_type: Type of warning (e.g., "obstacle", "stairs")
            details: Additional details
        """
        if warning_type.lower() == 'obstacle':
            message = "Warning! Obstacle ahead!"
        elif warning_type.lower() == 'stairs':
            message = "Caution! Stairs detected!"
        elif warning_type.lower() == 'person':
            message = "Person nearby!"
        else:
            message = f"Warning! {warning_type}"
        
        if details:
            message += f" {details}"
        
        self.speak(message, urgent=True)
    
    def speak(self, text: str, urgent: bool = False):
        """
        Speak a message with duplicate prevention.
        
        Args:
            text: Text to speak
            urgent: If True, bypass duplicate checking
        """
        from datetime import datetime
        
        # Check for duplicates (unless urgent)
        if not urgent:
            now = datetime.now()
            
            # Remove old history
            self.announcement_history = [
                (msg, time) for msg, time in self.announcement_history
                if (now - time).total_seconds() < self.min_interval * 2
            ]
            
            # Check if same message was recently announced
            for msg, time in self.announcement_history:
                if msg == text:
                    return  # Skip duplicate
        
        # Add to history
        self.announcement_history.append((text, datetime.now()))
        
        # Limit history size
        if len(self.announcement_history) > self.max_announcements:
            self.announcement_history.pop(0)
        
        # Speak
        self.tts.speak(text, async_mode=True)
    
    def stop(self):
        """Stop current announcement."""
        self.tts.stop()
    
    def shutdown(self):
        """Shutdown the announcer."""
        self.tts.shutdown()


if __name__ == "__main__":
    # Test TTS
    import time
    
    print("Testing TTS Engine...")
    
    tts = TTSEngine(engine_type='pyttsx3', rate=150)
    
    test_messages = [
        "Hello, this is a test of the BlindStick text to speech system.",
        "Object detected: Chair at 2 meters.",
        "Warning! Obstacle ahead!",
        "Person detected at 3 meters."
    ]
    
    for msg in test_messages:
        print(f"Speaking: {msg}")
        tts.speak(msg, async_mode=False)
        time.sleep(0.5)
    
    print("\nTest complete!")
    tts.shutdown()
