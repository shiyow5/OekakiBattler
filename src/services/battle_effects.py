"""
Battle visual effects system
Handles all visual effects including particles, screen shake, and animations
"""

import pygame
import math
import random
from typing import Tuple, List, Optional
from dataclasses import dataclass

@dataclass
class Particle:
    """Particle for visual effects"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    gravity: float = 0.2
    fade: bool = True

    def update(self, dt: float = 1.0):
        """Update particle position and lifetime"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt

    def is_alive(self) -> bool:
        """Check if particle is still alive"""
        return self.life > 0

    def get_alpha(self) -> int:
        """Get alpha value based on lifetime"""
        if self.fade:
            return int(255 * (self.life / self.max_life))
        return 255

    def get_size(self) -> float:
        """Get current size"""
        return self.size * (self.life / self.max_life)


class BattleEffects:
    """Manages all battle visual effects"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.particles: List[Particle] = []
        self.screen_shake_intensity = 0.0
        self.screen_shake_duration = 0.0
        self.screen_offset = [0, 0]

    def add_particle(self, x: float, y: float, vx: float, vy: float,
                    life: float, color: Tuple[int, int, int],
                    size: float = 3.0, gravity: float = 0.2, fade: bool = True):
        """Add a new particle to the effect system"""
        particle = Particle(
            x=x, y=y, vx=vx, vy=vy,
            life=life, max_life=life,
            color=color, size=size,
            gravity=gravity, fade=fade
        )
        self.particles.append(particle)

    def create_explosion(self, x: float, y: float, particle_count: int = 20,
                        color: Tuple[int, int, int] = (255, 100, 0)):
        """Create an explosion effect"""
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 12)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(25, 50)
            size = random.uniform(4, 10)

            # Color variation
            r = max(0, min(255, color[0] + random.randint(-30, 30)))
            g = max(0, min(255, color[1] + random.randint(-30, 30)))
            b = max(0, min(255, color[2] + random.randint(-30, 30)))

            self.add_particle(x, y, vx, vy, life, (r, g, b), size)

    def create_slash_trail(self, start: Tuple[int, int], end: Tuple[int, int],
                          color: Tuple[int, int, int] = (255, 255, 200)):
        """Create a slash trail effect with particles"""
        steps = 25
        for i in range(steps):
            t = i / steps
            x = start[0] + (end[0] - start[0]) * t
            y = start[1] + (end[1] - start[1]) * t

            # Perpendicular offset for width
            dx = end[1] - start[1]
            dy = end[0] - start[0]
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx /= length
                dy /= length

            offset = random.uniform(-10, 10)
            px = x + dx * offset
            py = y + dy * offset

            vx = random.uniform(-2, 2)
            vy = random.uniform(-2, 2)
            life = random.uniform(15, 30)
            size = random.uniform(5, 12)

            self.add_particle(px, py, vx, vy, life, color, size, gravity=0.1)

    def create_magic_particles(self, x: float, y: float, particle_count: int = 30):
        """Create magical sparkle particles"""
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(40, 70)

            # Magic colors (blue, purple, white)
            colors = [
                (100, 100, 255),
                (200, 100, 255),
                (255, 255, 255),
                (150, 150, 255)
            ]
            color = random.choice(colors)
            size = random.uniform(4, 9)

            self.add_particle(x, y, vx, vy, life, color, size, gravity=-0.1)

    def create_impact_particles(self, x: float, y: float, direction: Tuple[float, float],
                               particle_count: int = 15):
        """Create impact particles that fly in a direction"""
        for _ in range(particle_count):
            angle_variation = random.uniform(-0.6, 0.6)
            speed = random.uniform(5, 15)

            # Base direction with variation
            angle = math.atan2(direction[1], direction[0]) + angle_variation
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            life = random.uniform(20, 40)
            color = (255, random.randint(50, 150), random.randint(50, 150))
            size = random.uniform(4, 9)

            self.add_particle(x, y, vx, vy, life, color, size)

    def create_charge_effect(self, x: float, y: float, particle_count: int = 10):
        """Create charging/gathering energy effect"""
        for _ in range(particle_count):
            # Particles start far and move toward center
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(60, 120)
            start_x = x + math.cos(angle) * distance
            start_y = y + math.sin(angle) * distance

            # Velocity toward center
            vx = (x - start_x) * 0.06
            vy = (y - start_y) * 0.06

            life = random.uniform(25, 45)
            color = (255, 255, random.randint(100, 255))
            size = random.uniform(4, 8)

            self.add_particle(start_x, start_y, vx, vy, life, color, size, gravity=0)

    def screen_shake(self, intensity: float = 10.0, duration: float = 15.0):
        """Trigger screen shake effect"""
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration

    def update(self, dt: float = 1.0):
        """Update all effects"""
        # Update particles
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update(dt)

        # Update screen shake
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= dt
            shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            self.screen_offset = [int(shake_x), int(shake_y)]
        else:
            self.screen_shake_intensity = 0
            self.screen_offset = [0, 0]

    def draw(self):
        """Draw all effects"""
        for particle in self.particles:
            if particle.is_alive():
                size = int(particle.get_size())
                if size > 0:
                    alpha = particle.get_alpha()

                    # Create surface with alpha
                    surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    # Ensure all color values are integers
                    color_with_alpha = (
                        int(particle.color[0]),
                        int(particle.color[1]),
                        int(particle.color[2]),
                        int(alpha)
                    )
                    pygame.draw.circle(surface, color_with_alpha, (size, size), size)

                    # Apply screen shake offset
                    pos = (
                        int(particle.x) - size + self.screen_offset[0],
                        int(particle.y) - size + self.screen_offset[1]
                    )
                    self.screen.blit(surface, pos)

    def clear(self):
        """Clear all effects"""
        self.particles.clear()
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0
        self.screen_offset = [0, 0]


class CharacterAnimator:
    """Handles character animation and movement"""

    def __init__(self):
        self.animations = {}
        self.current_time = 0

    def start_animation(self, character_id: str, animation_type: str,
                       duration: float, **params):
        """Start an animation for a character"""
        self.animations[character_id] = {
            'type': animation_type,
            'start_time': self.current_time,
            'duration': duration,
            'params': params
        }

    def update(self, dt: float = 1.0):
        """Update animations"""
        self.current_time += dt

        # Remove completed animations
        completed = []
        for char_id, anim in self.animations.items():
            elapsed = self.current_time - anim['start_time']
            if elapsed >= anim['duration']:
                completed.append(char_id)

        for char_id in completed:
            del self.animations[char_id]

    def get_offset(self, character_id: str) -> Tuple[float, float]:
        """Get current animation offset for character"""
        if character_id not in self.animations:
            return (0, 0)

        anim = self.animations[character_id]
        elapsed = self.current_time - anim['start_time']
        t = min(1.0, elapsed / anim['duration'])

        if anim['type'] == 'jump':
            # Jump animation: up then down
            height = anim['params'].get('height', 30)
            if t < 0.5:
                # Going up
                offset_y = -height * self.ease_out_quad(t * 2)
            else:
                # Coming down
                offset_y = -height * (1 - self.ease_in_quad((t - 0.5) * 2))
            return (0, offset_y)

        elif anim['type'] == 'move_to':
            # Smooth movement to target position
            start_pos = anim['params'].get('start', (0, 0))
            end_pos = anim['params'].get('end', (0, 0))
            progress = self.ease_in_out_quad(t)
            offset_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
            offset_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
            return (offset_x, offset_y)

        elif anim['type'] == 'bounce':
            # Bouncing animation
            bounces = anim['params'].get('bounces', 2)
            height = anim['params'].get('height', 15)
            offset_y = -abs(math.sin(t * math.pi * bounces)) * height
            return (0, offset_y)

        elif anim['type'] == 'shake':
            # Shaking animation
            intensity = anim['params'].get('intensity', 5)
            offset_x = random.uniform(-intensity, intensity)
            offset_y = random.uniform(-intensity, intensity)
            return (offset_x, offset_y)

        return (0, 0)

    @staticmethod
    def ease_in_quad(t: float) -> float:
        """Quadratic ease-in"""
        return t * t

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """Quadratic ease-out"""
        return 1 - (1 - t) * (1 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """Quadratic ease-in-out"""
        if t < 0.5:
            return 2 * t * t
        else:
            return 1 - (-2 * t + 2) ** 2 / 2

    def is_animating(self, character_id: str) -> bool:
        """Check if character is currently animating"""
        return character_id in self.animations

    def clear(self):
        """Clear all animations"""
        self.animations.clear()
        self.current_time = 0