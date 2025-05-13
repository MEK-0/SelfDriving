import pygame
import math
from collections import deque
import random

BLACK = (0, 0, 0)

class Car:
    def __init__(self, x, y):
        # Araç görselini yükle ve boyutlandır
        self.original_image = pygame.image.load("red_car.png")
        # Boyutu 60x45 piksel olarak ayarla
        self.original_image = pygame.transform.scale(self.original_image, (60, 45))
        # Y eksenine göre yansıma al
        self.original_image = pygame.transform.flip(self.original_image, False, True)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 2
        self.alive = True
        self.completed_lap = False
        self.lap_count = 0
        self.start_time = pygame.time.get_ticks()
        
        # Yanma efekti için özellikler
        self.is_burning = False
        self.burn_start_time = 0
        self.burn_duration = 500
        
        # Tur tamamlama için özellikler
        self.checkpoint_passed = False
        self.start_line_passed = False
        self.last_checkpoint_time = 0
        
        # Yeni özellikler
        self.following_path = True
        self.path_progress = 0
        self.max_follow_distance = 200
        
        # Dönme kontrolü için özellikler
        self.angle_history = deque(maxlen=30)
        self.position_history = deque(maxlen=30)
        self.spinning_threshold = 180
        self.stuck_threshold = 10
        
        # Dönüş kontrolü için yeni özellikler
        self.last_angle = 0
        self.angle_change_threshold = 45
        self.consecutive_rotations = 0
        self.max_consecutive_rotations = 3
        
        self.ray_length = 100
        self.ray_angles = [-60, -30, 0, 30, 60]
        self.distances = [0 for _ in range(5)]

    def start_burning(self):
        self.is_burning = True
        self.burn_start_time = pygame.time.get_ticks()
        # Yanma durumunda görseli kırmızıya çevir
        self.image = self.original_image.copy()
        self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def update_burning_effect(self):
        if self.is_burning:
            current_time = pygame.time.get_ticks()
            if current_time - self.burn_start_time >= self.burn_duration:
                self.is_burning = False
                self.alive = False
            else:
                # Yanma efekti için renk değişimi
                progress = (current_time - self.burn_start_time) / self.burn_duration
                red = int(255 * (1 - progress))
                self.image = self.original_image.copy()
                self.image.fill((red, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def check_lap_completion(self, track):
        # Başlangıç çizgisi kontrolü (x=150 civarı)
        if 145 <= self.x <= 155 and not self.start_line_passed:
            self.start_line_passed = True
            return True
        
        # Checkpoint kontrolü (pistin ortasında bir nokta)
        if 400 <= self.x <= 600 and 400 <= self.y <= 600 and not self.checkpoint_passed:
            self.checkpoint_passed = True
            self.last_checkpoint_time = pygame.time.get_ticks()
            return False
        
        # Tur tamamlama kontrolü
        if self.start_line_passed and self.checkpoint_passed:
            current_time = pygame.time.get_ticks()
            # Checkpoint'ten sonra en az 2 saniye geçmiş olmalı
            if current_time - self.last_checkpoint_time > 2000:
                self.lap_count += 1
                self.start_line_passed = False
                self.checkpoint_passed = False
                return True
        
        return False

    def move(self):
        if self.following_path:
            if self.path_progress < self.max_follow_distance:
                self.angle = 0
                self.x += self.speed
                self.path_progress += self.speed
            else:
                self.following_path = False
                rad = math.radians(self.angle)
                self.x += math.cos(rad) * self.speed
                self.y += math.sin(rad) * self.speed
        else:
            rad = math.radians(self.angle)
            self.x += math.cos(rad) * self.speed
            self.y += math.sin(rad) * self.speed
        
        # Pozisyon ve açı geçmişini güncelle
        self.position_history.append((self.x, self.y))
        self.angle_history.append(self.angle)
        
        # Dönme veya takılma kontrolü
        if not self.following_path and (self.is_spinning() or self.is_stuck()):
            if not self.is_burning:  # Eğer zaten yanmıyorsa
                self.start_burning()
        
        self.rect.center = (self.x, self.y)
        
        # Yanma efektini güncelle
        self.update_burning_effect()

    def is_spinning(self):
        if len(self.angle_history) < 30:
            return False
            
        total_angle_change = 0
        for i in range(1, len(self.angle_history)):
            angle_diff = abs(self.angle_history[i] - self.angle_history[i-1])
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            total_angle_change += angle_diff
            
        return total_angle_change > self.spinning_threshold

    def is_stuck(self):
        if len(self.position_history) < 30:
            return False
            
        total_movement = 0
        for i in range(1, len(self.position_history)):
            dx = self.position_history[i][0] - self.position_history[i-1][0]
            dy = self.position_history[i][1] - self.position_history[i-1][1]
            total_movement += math.sqrt(dx*dx + dy*dy)
            
        return total_movement < self.stuck_threshold

    def rotate(self, amount):
        if not self.following_path:
            # Dönüş miktarını sınırla
            if abs(amount) > self.angle_change_threshold:
                amount = self.angle_change_threshold if amount > 0 else -self.angle_change_threshold
            
            # Ardışık dönüşleri kontrol et
            if abs(amount) > 0:
                if (amount > 0 and self.last_angle > 0) or (amount < 0 and self.last_angle < 0):
                    self.consecutive_rotations += 1
                else:
                    self.consecutive_rotations = 0
            else:
                self.consecutive_rotations = 0
            
            # Ardışık dönüş sayısı limiti aşıldıysa dönüşü engelle
            if self.consecutive_rotations >= self.max_consecutive_rotations:
                amount = 0
                self.consecutive_rotations = 0
            
            self.angle += amount
            self.last_angle = amount

    def check_collision(self, track):
        if not (0 <= int(self.x) < track.get_width() and 0 <= int(self.y) < track.get_height()):
            self.alive = False
            return

        # Pist dışına çıkarsa (beyaz alana çarparsa)
        if track.get_at((int(self.x), int(self.y))) != BLACK:
            self.alive = False

    def cast_rays(self, track):
        self.distances = []

        for angle_offset in self.ray_angles:
            ray_angle = self.angle + angle_offset
            rad = math.radians(ray_angle)

            for i in range(1, self.ray_length):
                ray_x = int(self.x + math.cos(rad) * i)
                ray_y = int(self.y + math.sin(rad) * i)

                if 0 <= ray_x < track.get_width() and 0 <= ray_y < track.get_height():
                    if track.get_at((ray_x, ray_y)) != BLACK:
                        break
                else:
                    break

            self.distances.append(i / self.ray_length)  # normalleştir

    def draw(self, win):
        if self.is_burning:
            # Yanma efekti için parçacıklar
            for _ in range(5):
                particle_x = self.x + (random.random() - 0.5) * 20
                particle_y = self.y + (random.random() - 0.5) * 20
                pygame.draw.circle(win, (255, 100, 0), (int(particle_x), int(particle_y)), 2)
        
        # Görseli döndür
        rotated = pygame.transform.rotate(self.image, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        win.blit(rotated, rect)

    def draw_rays(self, win):
        for i, angle_offset in enumerate(self.ray_angles):
            ray_angle = self.angle + angle_offset
            rad = math.radians(ray_angle)
            end_x = self.x + math.cos(rad) * self.distances[i] * self.ray_length
            end_y = self.y + math.sin(rad) * self.distances[i] * self.ray_length
            pygame.draw.line(win, (255, 0, 0), (self.x, self.y), (end_x, end_y), 1)
            pygame.draw.circle(win, (0, 0, 255), (int(end_x), int(end_y)), 2)
