"""
Element Bubble Arena - Python/Kivy Version
Main entry point for the bubble shooter game
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config

# Set window size (for desktop testing)
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

from game import BubbleShooterGame
from levels.level1 import Level1


class BubbleShooterApp(App):
    """Main application class"""
    
    def build(self):
        """Build and return the game widget"""
        # Load Level 1
        level1 = Level1()
        
        # Create game instance with level configuration
        game = BubbleShooterGame(level=level1)
        
        # Schedule game update
        Clock.schedule_interval(game.update, 1.0 / 60.0)  # 60 FPS
        
        return game


if __name__ == '__main__':
    BubbleShooterApp().run()

