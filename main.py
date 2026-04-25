# main.py
# Android Eye Tracking App using Kivy and MediaPipe

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
import cv2
import mediapipe as mp
import numpy as np
import time

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
    User looks at center, up, and down to record pupil positions.
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
        self.calibration_points = {}  # Dict: 'center', 'up', 'down' -> (pupil_x, pupil_y)
        self.step = 0
        self.positions = {
            'center': (0.5, 0.5),
            'up': (0.5, 0.9),
            'down': (0.5, 0.1)
        }
        self.dot = Label(text="•", color=(1, 0, 0, 1), font_size=100, pos_hint={'x': 0.5, 'y': 0.5})
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
        keys = list(self.positions.keys())
        if self.step < len(keys):
            key = keys[self.step]
            x, y = self.positions[key]
            self.dot.pos_hint = {'x': x, 'y': y}
            self.label.text = f"Step {self.step + 1}/{len(keys)}: Look at the red dot ({key})"
        else:
            self.label.text = "Calibration complete. Go back to main screen."

    def capture_position(self, instance):
        """Capture the current pupil position."""
        keys = list(self.positions.keys())
        if self.step >= len(keys):
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
            key = keys[self.step]
            self.calibration_points[key] = (pupil_x, pupil_y)
            self.step += 1
            self.update_dot_position()
            if self.step >= len(keys):
                # Pass to main screen
                main_screen = self.manager.get_screen('main')
                main_screen.eye_tracker.set_calibration(self.calibration_points)
                self.btn_capture.text = "Done"
        else:
            self.label.text = "No face detected. Try again."

class SettingsScreen(Screen):
    """
    Screen for adjusting settings: sensitivity and dwell time.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.sensitivity_label = Label(text="Sensitivity: 0.15")
        self.sensitivity_slider = Slider(min=0.05, max=0.5, value=0.15, step=0.01)
        self.sensitivity_slider.bind(value=self.on_sensitivity_change)
        self.dwell_label = Label(text="Dwell Time: 0.5s")
        self.dwell_slider = Slider(min=0.2, max=2.0, value=0.5, step=0.1)
        self.dwell_slider.bind(value=self.on_dwell_change)
        self.btn_back = Button(text="Back", size_hint=(1, 0.2), on_press=self.go_back)
        self.layout.add_widget(self.sensitivity_label)
        self.layout.add_widget(self.sensitivity_slider)
        self.layout.add_widget(self.dwell_label)
        self.layout.add_widget(self.dwell_slider)
        self.layout.add_widget(self.btn_back)
        self.add_widget(self.layout)

    def on_sensitivity_change(self, instance, value):
        self.sensitivity_label.text = f"Sensitivity: {value:.2f}"
        main_screen = self.manager.get_screen('main')
        main_screen.eye_tracker.sensitivity = value

    def on_dwell_change(self, instance, value):
        self.dwell_label.text = f"Dwell Time: {value:.1f}s"
        main_screen = self.manager.get_screen('main')
        main_screen.eye_tracker.dwell_time = value

    def go_back(self, instance):
        self.manager.current = 'main'

class PreviewWidget(Image):
    """
    Widget for camera preview with tracking points.
    """
    def __init__(self, eye_tracker, **kwargs):
        super().__init__(**kwargs)
        self.eye_tracker = eye_tracker
        self.size_hint = (0.5, 0.5)
        self.pos_hint = {'right': 1, 'top': 1}
        Clock.schedule_interval(self.update_preview, 0.1)

    def update_preview(self, dt):
        if hasattr(self.eye_tracker, 'last_frame') and self.eye_tracker.last_frame is not None:
            frame = self.eye_tracker.last_frame.copy()
            # Draw points if available
            if self.eye_tracker.last_landmarks:
                for lm in self.eye_tracker.last_landmarks:
                    x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            # Convert to texture
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = texture

class MainScreen(Screen):
    """
    Main screen with buttons, preview, and navigation.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        self.btn_cal = Button(text="Calibration", on_press=self.go_cal)
        self.btn_settings = Button(text="Settings", on_press=self.go_settings)
        self.btn_start = Button(text="Start Tracking", on_press=self.start_service)
        self.btn_stop = Button(text="Stop Tracking", on_press=self.stop_service)
        self.btn_layout.add_widget(self.btn_cal)
        self.btn_layout.add_widget(self.btn_settings)
        self.btn_layout.add_widget(self.btn_start)
        self.btn_layout.add_widget(self.btn_stop)
        self.layout.add_widget(self.btn_layout)

        self.eye_tracker = EyeTracker()
        self.preview = PreviewWidget(self.eye_tracker)
        self.layout.add_widget(self.preview)

        self.add_widget(self.layout)

    def go_cal(self, instance):
        """Switch to calibration screen."""
        self.manager.current = 'cal'

    def go_settings(self, instance):
        """Switch to settings screen."""
        self.manager.current = 'settings'

    def start_service(self, instance):
        """Start the eye tracking."""
        self.eye_tracker.start()

    def stop_service(self, instance):
        """Stop the eye tracking."""
        self.eye_tracker.stop()

class EyeTracker:
    """
    Handles eye tracking logic using camera and MediaPipe.
    Includes smoothing, dwell time, blink detection.
    """
    def __init__(self):
        self.calibration_points = {}  # 'center', 'up', 'down' -> (x, y)
        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.running = False
        self.sensitivity = 0.15  # Threshold for direction
        self.dwell_time = 0.5  # Seconds to hold gaze
        self.alpha = 0.8  # Smoothing factor
        self.smoothed_pupil = None
        self.last_direction = None
        self.dwell_start = None
        self.blinks = []  # List of blink timestamps
        self.paused = False
        self.last_frame = None
        self.last_landmarks = None

    def set_calibration(self, points):
        self.calibration_points = points

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

        self.last_frame = frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            self.last_landmarks = landmarks.landmark
            left_pupil = landmarks.landmark[468]
            right_pupil = landmarks.landmark[473]
            pupil_x = (left_pupil.x + right_pupil.x) / 2
            pupil_y = (left_pupil.y + right_pupil.y) / 2

            # Smoothing
            if self.smoothed_pupil is None:
                self.smoothed_pupil = (pupil_x, pupil_y)
            else:
                self.smoothed_pupil = (
                    self.alpha * self.smoothed_pupil[0] + (1 - self.alpha) * pupil_x,
                    self.alpha * self.smoothed_pupil[1] + (1 - self.alpha) * pupil_y
                )

            pupil_x, pupil_y = self.smoothed_pupil

            # Blink detection
            ear = self.eye_aspect_ratio(landmarks)
            if ear < 0.2:  # Blink threshold
                now = time.time()
                self.blinks.append(now)
                # Keep only recent blinks
                self.blinks = [b for b in self.blinks if now - b < 1.0]
                if len(self.blinks) >= 2 and self.blinks[-1] - self.blinks[-2] < 0.5:
                    self.toggle_pause()

            # Determine direction
            center_y = self.calibration_points['center'][1]
            if pupil_y < center_y - self.sensitivity:
                direction = 'up'
            elif pupil_y > center_y + self.sensitivity:
                direction = 'down'
            else:
                direction = 'center'

            # Dwell logic
            if direction in ['up', 'down'] and not self.paused:
                if self.last_direction != direction:
                    self.dwell_start = time.time()
                    self.last_direction = direction
                elif self.dwell_start and time.time() - self.dwell_start >= self.dwell_time:
                    self.send_swipe(direction)
                    self.dwell_start = None  # Reset
            else:
                self.dwell_start = None
                self.last_direction = None

    def eye_aspect_ratio(self, landmarks):
        """Calculate eye aspect ratio for blink detection."""
        # Left eye
        p1 = landmarks.landmark[33]
        p2 = landmarks.landmark[160]
        p3 = landmarks.landmark[158]
        p4 = landmarks.landmark[133]
        p5 = landmarks.landmark[153]
        p6 = landmarks.landmark[144]
        ear_left = (np.linalg.norm([p2.x - p6.x, p2.y - p6.y]) + np.linalg.norm([p3.x - p5.x, p3.y - p5.y])) / (2 * np.linalg.norm([p1.x - p4.x, p1.y - p4.y]))
        # Right eye
        p1 = landmarks.landmark[362]
        p2 = landmarks.landmark[385]
        p3 = landmarks.landmark[387]
        p4 = landmarks.landmark[263]
        p5 = landmarks.landmark[373]
        p6 = landmarks.landmark[380]
        ear_right = (np.linalg.norm([p2.x - p6.x, p2.y - p6.y]) + np.linalg.norm([p3.x - p5.x, p3.y - p5.y])) / (2 * np.linalg.norm([p1.x - p4.x, p1.y - p4.y]))
        return (ear_left + ear_right) / 2

    def toggle_pause(self):
        """Toggle pause/play."""
        self.paused = not self.paused
        print(f"Tracking {'paused' if self.paused else 'resumed'}")

    def send_swipe(self, direction):
        """Send swipe gesture using Accessibility Service."""
        if MyAccessibilityService and not self.paused:
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
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

    def on_stop(self):
        """Clean up on app stop."""
        main_screen = self.root.get_screen('main')
        main_screen.eye_tracker.stop()

if __name__ == '__main__':
    MainApp().run()