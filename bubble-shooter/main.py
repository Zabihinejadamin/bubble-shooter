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
from kivy.storage.jsonstore import JsonStore


def load_saved_level():
    """Load saved level from profile, or return Level 1 if no profile exists"""
    try:
        store = JsonStore('player_profile.json')
        if 'profile' in store:
            profile = store.get('profile')
            saved_level = profile.get('current_level', 1)
        else:
            saved_level = 1
    except Exception:
        saved_level = 1
    
    # Import all level classes
    from levels.level1 import Level1
    from levels.level2 import Level2
    from levels.level3 import Level3
    from levels.level4 import Level4
    from levels.level5 import Level5
    from levels.level6 import Level6
    from levels.level7 import Level7
    from levels.level8 import Level8
    from levels.level9 import Level9
    from levels.level10 import Level10
    from levels.level11 import Level11
    from levels.level12 import Level12
    from levels.level13 import Level13
    from levels.level14 import Level14
    from levels.level15 import Level15
    from levels.level16 import Level16
    from levels.level17 import Level17
    from levels.level18 import Level18
    from levels.level19 import Level19
    from levels.level20 import Level20
    from levels.level21 import Level21
    from levels.level22 import Level22
    from levels.level23 import Level23
    from levels.level24 import Level24
    from levels.level25 import Level25
    from levels.level26 import Level26
    from levels.level27 import Level27
    from levels.level28 import Level28
    from levels.level29 import Level29
    from levels.level30 import Level30
    from levels.level31 import Level31
    from levels.level32 import Level32
    from levels.level33 import Level33
    from levels.level34 import Level34
    from levels.level35 import Level35
    from levels.level36 import Level36
    from levels.level37 import Level37
    from levels.level38 import Level38
    from levels.level39 import Level39
    from levels.level40 import Level40
    
    # Map level numbers to classes
    level_classes = {
        1: Level1, 2: Level2, 3: Level3, 4: Level4, 5: Level5,
        6: Level6, 7: Level7, 8: Level8, 9: Level9, 10: Level10,
        11: Level11, 12: Level12, 13: Level13, 14: Level14, 15: Level15,
        16: Level16, 17: Level17, 18: Level18, 19: Level19, 20: Level20,
        21: Level21, 22: Level22, 23: Level23, 24: Level24, 25: Level25,
        26: Level26, 27: Level27, 28: Level28, 29: Level29, 30: Level30,
        31: Level31, 32: Level32, 33: Level33, 34: Level34, 35: Level35,
        36: Level36, 37: Level37, 38: Level38, 39: Level39, 40: Level40,
    }
    
    # Get the level class or default to Level1
    level_class = level_classes.get(saved_level, Level1)
    return level_class()


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
        
        # Load saved level or start from Level 1
        saved_level = load_saved_level()
        
        # Create a FloatLayout to ensure full screen coverage
        root_layout = FloatLayout()
        root_layout.size = Window.size
        
        # Create game instance with level configuration
        game = BubbleShooterGame(level=saved_level)
        
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

