// src/MyAccessibilityService.java
// Accessibility Service for dispatching gestures in the eye tracking app

package org.test.myapp;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.view.Display;
import android.graphics.Point;

public class MyAccessibilityService extends AccessibilityService {

    private static MyAccessibilityService instance;
    private static int screenWidth = 1080;  // Default, will be updated
    private static int screenHeight = 1920;

    @Override
    public void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        // Get screen size
        Display display = getSystemService(Display.class);
        Point size = new Point();
        display.getSize(size);
        screenWidth = size.x;
        screenHeight = size.y;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        instance = null;
    }

    public static void dispatchSwipeUp() {
        if (instance != null) {
            dispatchSwipe(500, 1500, 500, 500);  // From bottom to top
        }
    }

    public static void dispatchSwipeDown() {
        if (instance != null) {
            dispatchSwipe(500, 500, 500, 1500);  // From top to bottom
        }
    }

    private static void dispatchSwipe(float startX, float startY, float endX, float endY) {
        Path path = new Path();
        path.moveTo(startX, startY);
        path.lineTo(endX, endY);

        GestureDescription.StrokeDescription stroke = new GestureDescription.StrokeDescription(
            path, 0, 500  // 0 delay, 500ms duration
        );

        GestureDescription.Builder builder = new GestureDescription.Builder();
        builder.addStroke(stroke);

        instance.dispatchGesture(builder.build(), null, null);
    }
}