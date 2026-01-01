"""
Element Bubble Arena - Python/Kivy Version
Main entry point for the bubble shooter game
"""

from kivy.config import Config

# Set fullscreen mode - works on Android, ignored on desktop if width/height are set
Config.set('graphics', 'fullscreen', 'auto')
# Disable borderless window mode which can interfere with fullscreen
Config.set('graphics', 'borderless', '0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window

from game import BubbleShooterGame
from levels.level1 import Level1


class BubbleShooterApp(App):
    """Main application class"""
    
    def build(self):
        """Build and return the game widget"""
        # Detect platform and configure accordingly
        try:
            from kivy.utils import platform
            if platform == 'android':
                # On Android: ensure fullscreen mode - use True instead of 'auto'
                Window.fullscreen = True
                # Hide system UI bars for immersive fullscreen using pyjnius
                try:
                    from jnius import autoclass
                    from jnius import cast
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    View = autoclass('android.view.View')
                    WindowManager = autoclass('android.view.WindowManager')
                    
                    # Get the window and set immersive sticky mode
                    window = activity.getWindow()
                    decorView = window.getDecorView()
                    systemUiVisibility = decorView.getSystemUiVisibility()
                    
                    # Set immersive sticky flags
                    SYSTEM_UI_FLAG_FULLSCREEN = 0x00000004
                    SYSTEM_UI_FLAG_HIDE_NAVIGATION = 0x00000002
                    SYSTEM_UI_FLAG_IMMERSIVE_STICKY = 0x00001000
                    SYSTEM_UI_FLAG_LAYOUT_STABLE = 0x00000100
                    SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN = 0x00000400
                    SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION = 0x00000200
                    
                    flags = (SYSTEM_UI_FLAG_FULLSCREEN |
                            SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                            SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                            SYSTEM_UI_FLAG_LAYOUT_STABLE |
                            SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                            SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION)
                    
                    decorView.setSystemUiVisibility(flags)
                except Exception as e:
                    # If pyjnius fails, try alternative method
                    try:
                        from android import hide_system_bars
                        hide_system_bars()
                    except:
                        pass
                # Don't set window size on Android - let it use full screen
            else:
                # On desktop: set fixed window size for testing (1080x2424 for testing)
                Window.size = (1080, 2424)
                Window.fullscreen = False
        except:
            # Fallback: set desktop window size
            Window.size = (1080, 2424)
            Window.fullscreen = False
        
        # Load Level 1 (start from beginning)
        level1 = Level1()
        
        # Create a FloatLayout to ensure full screen coverage
        root_layout = FloatLayout()
        root_layout.size = Window.size
        
        # Create game instance with level configuration
        game = BubbleShooterGame(level=level1)
        
        # Explicitly set game widget size to window size
        game.size = Window.size
        
        # Ensure game widget fills the entire layout
        game.size_hint = (1, 1)
        game.pos_hint = {'x': 0, 'y': 0}
        
        # Add game to layout
        root_layout.add_widget(game)
        
        # Store reference for size updates
        self.root_layout = root_layout
        self.game = game
        
        # Bind to window size changes to update layout and game
        def update_sizes(window, width, height):
            root_layout.size = (width, height)
            game.size = (width, height)
        Window.bind(size=update_sizes)
        
        # Schedule fullscreen setup after window is ready (Android)
        def setup_fullscreen(dt):
            try:
                from kivy.utils import platform
                if platform == 'android':
                    Window.fullscreen = True
                    # Hide system UI bars for immersive fullscreen using pyjnius
                    try:
                        from jnius import autoclass
                        PythonActivity = autoclass('org.kivy.android.PythonActivity')
                        activity = PythonActivity.mActivity
                        
                        # Get the window and set immersive sticky mode
                        window = activity.getWindow()
                        decorView = window.getDecorView()
                        
                        # Set immersive sticky flags
                        SYSTEM_UI_FLAG_FULLSCREEN = 0x00000004
                        SYSTEM_UI_FLAG_HIDE_NAVIGATION = 0x00000002
                        SYSTEM_UI_FLAG_IMMERSIVE_STICKY = 0x00001000
                        SYSTEM_UI_FLAG_LAYOUT_STABLE = 0x00000100
                        SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN = 0x00000400
                        SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION = 0x00000200
                        
                        flags = (SYSTEM_UI_FLAG_FULLSCREEN |
                                SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                                SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                                SYSTEM_UI_FLAG_LAYOUT_STABLE |
                                SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                                SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION)
                        
                        decorView.setSystemUiVisibility(flags)
                    except:
                        pass
            except:
                pass
        
        # Schedule fullscreen setup after a short delay to ensure window is ready
        Clock.schedule_once(setup_fullscreen, 0.1)
        
        # Schedule game update
        Clock.schedule_interval(game.update, 1.0 / 60.0)  # 60 FPS
        
        return root_layout


if __name__ == '__main__':
    BubbleShooterApp().run()

