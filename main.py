# main.py
# Android Eye Tracking App using Kivy and MediaPipe

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
import cv2
import mediapipe as mp
import numpy as np

# For Android specific features
try:
    from android.permissions import request_permissions, Permission
    from android import activity
    from jnius import autoclass
    MyAccessibilityService = autoclass('org.test.myapp.MyAccessibilityService')
except ImportError:
    # Not on Android
    MyAccessibilityService = None

class CalibrationScreen(Screen):
    """
    Screen for calibrating the eye tracking.
    User looks at four corners of the screen to record pupil positions.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Look at the red dot and press the button when ready", size_hint=(1, 0.8))
        self.btn_capture = Button(text="Capture", size_hint=(1, 0.2), on_press=self.capture_position)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.btn_capture)
        self.add_widget(self.layout)

        # Calibration setup
        self.calibration_points = []  # List of (pupil_x, pupil_y) for each corner
        self.step = 0
        self.positions = [
            (0.1, 0.9),  # Top-left
            (0.9, 0.9),  # Top-right
            (0.1, 0.1),  # Bottom-left
            (0.9, 0.1)   # Bottom-right
        ]
        self.dot = Label(text="•", color=(1, 0, 0, 1), font_size=100, pos_hint={'x': 0.1, 'y': 0.9})
        self.add_widget(self.dot)

        # Camera and MediaPipe
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.update_dot_position()

    def update_dot_position(self):
        """Update the dot position for the current calibration step."""
        if self.step < 4:
            x, y = self.positions[self.step]
            self.dot.pos_hint = {'x': x, 'y': y}
            self.label.text = f"Step {self.step + 1}/4: Look at the red dot"
        else:
            self.label.text = "Calibration complete. Go back to main screen."

    def capture_position(self, instance):
        """Capture the current pupil position."""
        if self.step >= 4:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.label.text = "Camera error"
            return

        # Process with MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            # Use left and right pupil landmarks (468 and 473)
            left_pupil = landmarks.landmark[468]
            right_pupil = landmarks.landmark[473]
            pupil_x = (left_pupil.x + right_pupil.x) / 2
            pupil_y = (left_pupil.y + right_pupil.y) / 2
            self.calibration_points.append((pupil_x, pupil_y))
            self.step += 1
            self.update_dot_position()
            if self.step >= 4:
                # Pass to main screen
                main_screen = self.manager.get_screen('main')
                main_screen.eye_tracker.calibration_points = self.calibration_points
                self.btn_capture.text = "Done"
        else:
            self.label.text = "No face detected. Try again."

class MainScreen(Screen):
    """
    Main screen with buttons for calibration and starting the service.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.btn_cal = Button(text="Start Calibration", size_hint=(1, 0.5), on_press=self.go_cal)
        self.btn_start = Button(text="Start Eye Tracking Service", size_hint=(1, 0.5), on_press=self.start_service)
        self.layout.add_widget(self.btn_cal)
        self.layout.add_widget(self.btn_start)
        self.add_widget(self.layout)

        self.eye_tracker = EyeTracker()

    def go_cal(self, instance):
        """Switch to calibration screen."""
        self.manager.current = 'cal'

    def start_service(self, instance):
        """Start the eye tracking in background and minimize app."""
        self.eye_tracker.start()
        # Minimize app on Android
        try:
            activity.moveTaskToBack(True)
        except:
            pass

class EyeTracker:
    """
    Handles eye tracking logic using camera and MediaPipe.
    Sends swipe gestures based on gaze direction.
    """
    def __init__(self):
        self.calibration_points = []  # [(x,y) for top-left, top-right, bottom-left, bottom-right]
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.last_direction = None
        self.running = False

    def start(self):
        """Start the tracking loop."""
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.track, 0.1)  # 10 FPS

    def stop(self):
        """Stop the tracking."""
        self.running = False
        Clock.unschedule(self.track)
        self.cap.release()

    def track(self, dt):
        """Main tracking loop."""
        if not self.running or not self.calibration_points:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            left_pupil = landmarks.landmark[468]
            right_pupil = landmarks.landmark[473]
            pupil_x = (left_pupil.x + right_pupil.x) / 2
            pupil_y = (left_pupil.y + right_pupil.y) / 2

            # Determine direction based on calibration
            # Simple threshold: if pupil_y < average y of top points, up; else down
            top_avg_y = (self.calibration_points[0][1] + self.calibration_points[1][1]) / 2
            bottom_avg_y = (self.calibration_points[2][1] + self.calibration_points[3][1]) / 2
            mid_y = (top_avg_y + bottom_avg_y) / 2

            if pupil_y < mid_y:
                direction = 'up'
            else:
                direction = 'down'

            # Only send if direction changed
            if direction != self.last_direction:
                self.send_swipe(direction)
                self.last_direction = direction

    def send_swipe(self, direction):
        """Send swipe gesture using Accessibility Service."""
        if MyAccessibilityService:
            try:
                if direction == 'up':
                    MyAccessibilityService.dispatchSwipeUp()
                elif direction == 'down':
                    MyAccessibilityService.dispatchSwipeDown()
            except Exception as e:
                print(f"Error dispatching gesture: {e}")
        else:
            # Fallback for non-Android
            print(f"Simulated swipe {direction}")

class MainApp(App):
    """
    Main Kivy application.
    """
    def build(self):
        # Request permissions on Android
        try:
            request_permissions([Permission.CAMERA])
        except:
            pass

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CalibrationScreen(name='cal'))
        return sm

    def on_stop(self):
        """Clean up on app stop."""
        main_screen = self.root.get_screen('main')
        main_screen.eye_tracker.stop()

if __name__ == '__main__':
    MainApp().run()