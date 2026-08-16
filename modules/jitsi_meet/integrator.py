#!/data/data/com.termux/files/usr/bin/python3
"""
Jitsi Meet Integrator
Creates and manages secure meeting rooms
Based on Jitsi Meet interface diagram with room name and start meeting button
"""
import json
import time
import hashlib
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [JITSI] %(message)s')
logger = logging.getLogger(__name__)

class MeetingRoom:
    """Represents a Jitsi meeting room"""
    def __init__(self, room_name, created_by):
        self.room_name = room_name
        self.room_id = hashlib.sha256(f"{room_name}{time.time()}".encode()).hexdigest()[:16]
        self.created_by = created_by
        self.created_at = datetime.now().isoformat()
        self.status = "created"
        self.participants = []
        self.max_participants = 100
        self.security = {
            "encrypted": True,
            "password_protected": False,
            "lobby_enabled": False,
            "waiting_room": False
        }
        self.settings = {
            "video_quality": "high",
            "audio_quality": "high",
            "recording_enabled": False,
            "live_streaming": False,
            "screen_sharing": True,
            "chat_enabled": True,
            "raise_hand": True
        }
        self.meeting_url = f"https://meet.jit.si/{room_name}"
        self.duration_seconds = 0
        self.started_at = None
        self.ended_at = None

    def start_meeting(self):
        """Start the meeting"""
        self.status = "active"
        self.started_at = datetime.now().isoformat()
        self.participants.append({
            "name": self.created_by,
            "role": "moderator",
            "joined_at": datetime.now().isoformat()
        })
        logger.info(f"Meeting started: {self.room_name} by {self.created_by}")
        return self.get_meeting_info()

    def join_participant(self, participant_name, role="participant"):
        """Add participant to meeting"""
        if self.status != "active":
            return {"error": "Meeting not active"}

        if len(self.participants) >= self.max_participants:
            return {"error": "Meeting full"}

        participant = {
            "name": participant_name,
            "role": role,
            "joined_at": datetime.now().isoformat()
        }
        self.participants.append(participant)
        logger.info(f"Participant joined: {participant_name}")
        return participant

    def leave_participant(self, participant_name):
        """Remove participant from meeting"""
        self.participants = [p for p in self.participants if p["name"] != participant_name]
        logger.info(f"Participant left: {participant_name}")

    def end_meeting(self):
        """End the meeting"""
        self.status = "ended"
        self.ended_at = datetime.now().isoformat()
        if self.started_at:
            start = datetime.fromisoformat(self.started_at)
            end = datetime.fromisoformat(self.ended_at)
            self.duration_seconds = int((end - start).total_seconds())
        logger.info(f"Meeting ended: {self.room_name} (duration: {self.duration_seconds}s)")

    def set_password(self, password):
        """Set meeting password"""
        self.security["password_protected"] = True
        self.security["password"] = hashlib.sha256(password.encode()).hexdigest()
        logger.info(f"Password set for {self.room_name}")

    def enable_lobby(self):
        """Enable lobby/waiting room"""
        self.security["lobby_enabled"] = True
        self.security["waiting_room"] = True
        logger.info(f"Lobby enabled for {self.room_name}")

    def get_meeting_info(self):
        return {
            "room_name": self.room_name,
            "room_id": self.room_id,
            "meeting_url": self.meeting_url,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "participants": len(self.participants),
            "max_participants": self.max_participants,
            "security": {k: v for k, v in self.security.items() if k != "password"},
            "settings": self.settings
        }

class JitsiMeetServer:
    """Jitsi Meet server managing multiple meetings"""
    def __init__(self, server_url="meet.jit.si"):
        self.server_url = server_url
        self.meetings = {}
        self.active_meetings = 0
        self.total_meetings = 0

    def create_meeting(self, room_name, created_by, security_options=None):
        """Create a new meeting room"""
        room = MeetingRoom(room_name, created_by)

        # Apply security options
        if security_options:
            if security_options.get("password"):
                room.set_password(security_options["password"])
            if security_options.get("lobby"):
                room.enable_lobby()

        self.meetings[room.room_id] = room
        self.total_meetings += 1

        logger.info(f"Meeting room created: {room_name}")
        return room

    def start_meeting(self, room_name):
        """Start a meeting by room name"""
        for room in self.meetings.values():
            if room.room_name == room_name:
                result = room.start_meeting()
                self.active_meetings += 1
                return result
        return {"error": f"Room {room_name} not found"}

    def get_room(self, room_name):
        """Get room by name"""
        for room in self.meetings.values():
            if room.room_name == room_name:
                return room
        return None

    def get_server_status(self):
        return {
            "server_url": self.server_url,
            "total_meetings": self.total_meetings,
            "active_meetings": self.active_meetings,
            "meetings": {rid: room.get_meeting_info() for rid, room in self.meetings.items()}
        }

class JitsiMeetUI:
    """Simulates the Jitsi Meet UI interaction"""
    def __init__(self, server):
        self.server = server
        self.current_room = None

    def enter_room_name(self, room_name):
        """User enters room name in UI"""
        self.current_room = room_name
        logger.info(f"UI: Room name entered: {room_name}")
        return room_name

    def click_start_meeting(self, created_by="Anonymous"):
        """User clicks 'Start meeting' button"""
        if not self.current_room:
            return {"error": "No room name entered"}

        # Check if room exists
        room = self.server.get_room(self.current_room)
        if not room:
            # Create new room
            room = self.server.create_meeting(self.current_room, created_by)

        # Start meeting
        result = self.server.start_meeting(self.current_room)
        return result

    def get_ui_state(self):
        return {
            "current_room": self.current_room,
            "server": self.server.server_url,
            "button_text": "Start meeting" if self.current_room else "Enter room name"
        }

if __name__ == "__main__":
    server = JitsiMeetServer("meet.jit.si")
    ui = JitsiMeetUI(server)

    print("=== JITSI MEET INTEGRATOR DEMO ===\n")

    # UI interaction (like the diagram)
    print("1. Jitsi Meet UI:")
    print("   Room name input: MiddleLossesEnableCons")
    room_name = ui.enter_room_name("MiddleLossesEnableCons")
    print(f"   Button: [Start meeting]\n")

    # Create meeting with security
    print("2. Creating secure meeting:")
    meeting = server.create_meeting(
        "MiddleLossesEnableCons",
        "CyGeL",
        security_options={
            "password": "sovereign2026",
            "lobby": True
        }
    )
    print(f"   Room: {meeting.room_name}")
    print(f"   URL: {meeting.meeting_url}")
    print(f"   Security: Encrypted={meeting.security['encrypted']}, Password={meeting.security['password_protected']}, Lobby={meeting.security['lobby_enabled']}\n")

    # Start meeting
    print("3. Starting meeting:")
    result = ui.click_start_meeting("CyGeL")
    print(f"   Status: {result['status']}")
    print(f"   Participants: {result['participants']}")
    print(f"   Started: {result['started_at']}\n")

    # Join participants
    print("4. Participants joining:")
    meeting = server.get_room("MiddleLossesEnableCons")
    meeting.join_participant("Agent-Earth", "moderator")
    meeting.join_participant("Agent-Mars", "participant")
    meeting.join_participant("Agent-Venus", "participant")
    print(f"   Total participants: {len(meeting.participants)}")
    for p in meeting.participants:
        print(f"     - {p['name']} ({p['role']})")
    print()

    # Meeting info
    print("5. Meeting info:")
    info = meeting.get_meeting_info()
    print(f"   Room: {info['room_name']}")
    print(f"   URL: {info['meeting_url']}")
    print(f"   Status: {info['status']}")
    print(f"   Participants: {info['participants']}/{info['max_participants']}")
    print(f"   Video quality: {info['settings']['video_quality']}")
    print(f"   Screen sharing: {info['settings']['screen_sharing']}")
    print(f"   Chat: {info['settings']['chat_enabled']}\n")

    # Server status
    print("6. Server status:")
    status = server.get_server_status()
    print(f"   Server: {status['server_url']}")
    print(f"   Total meetings: {status['total_meetings']}")
    print(f"   Active meetings: {status['active_meetings']}")

    print("\n=== JITSI MEET ARCHITECTURE ===")
    print("UI: Room name input + [Start meeting] button")
    print("Features: Encrypted, password protection, lobby, screen sharing, chat")
