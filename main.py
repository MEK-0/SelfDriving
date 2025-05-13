import pygame
import neat
import os
from car import Car
import time

# Pygame başlat
pygame.init()

# Ekran çözünürlüğü - TAM EKRAN ayarı
info = pygame.display.Info()
WIDTH, HEIGHT = 1536, 1020
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("AI Self Driving Car")

# Font ayarları
FONT = pygame.font.SysFont('Arial', 40)
BIG_FONT = pygame.font.SysFont('Arial', 60)

# Harita dosyası
TRACK_PATH = "track.png"

print("Çalışma dizini:", os.getcwd())

# neat_config.txt dosyasının mutlak yolunu ayarla
config_path = os.path.abspath("neat_config.txt")
print("Kullanılan neat_config yolu:", config_path)
print("Config dosyası var mı:", os.path.exists(config_path))

def draw_stats(car, attempt_number, best_time=None, total_time=0):
    # Sayaç kutusu
    counter_box = pygame.Surface((300, 200))  # Yüksekliği artırdık
    counter_box.set_alpha(200)
    counter_box.fill((0, 0, 0))
    WIN.blit(counter_box, (10, 10))
    
    # Süre hesaplama
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - car.start_time) / 1000  # saniye cinsinden
    
    # İstatistikleri ekrana yazdır
    stats_text = [
        f"Deneme: {attempt_number}",
        f"Süre: {elapsed_time:.2f} sn",
        f"Tur: {car.lap_count}",
        f"Toplam Süre: {total_time:.2f} sn"
    ]
    
    if best_time:
        stats_text.append(f"En İyi Süre: {best_time:.2f} sn")
    
    for i, text in enumerate(stats_text):
        text_surface = FONT.render(text, True, (255, 255, 255))
        WIN.blit(text_surface, (20, 20 + i * 35))

def eval_genomes(genomes, config):
    clock = pygame.time.Clock()
    track = pygame.image.load(TRACK_PATH).convert()
    
    attempt_number = 1
    current_car = None
    current_net = None
    current_genome = None
    best_time = None
    
    # Genel zaman sayacı için
    program_start_time = pygame.time.get_ticks()
    
    all_genomes = list(genomes)
    current_genome_index = 0
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                run = False
                pygame.quit()
                return
        
        WIN.blit(track, (0, 0))
        
        # Genel süreyi hesapla
        total_time = (pygame.time.get_ticks() - program_start_time) / 1000
        
        # Eğer araç yoksa veya öldüyse yeni araç oluştur
        if current_car is None or not current_car.alive:
            if current_genome_index < len(all_genomes):
                genome_id, genome = all_genomes[current_genome_index]
                current_net = neat.nn.FeedForwardNetwork.create(genome, config)
                current_car = Car(150, 150)
                current_genome = genome
                current_genome.fitness = 0
                attempt_number += 1
                current_genome_index += 1
            else:
                current_genome_index = 0
                genome_id, genome = all_genomes[current_genome_index]
                current_net = neat.nn.FeedForwardNetwork.create(genome, config)
                current_car = Car(150, 150)
                current_genome = genome
                current_genome.fitness = 0
                attempt_number += 1
                current_genome_index += 1
        
        if current_car and current_car.alive:
            current_car.move()
            current_car.cast_rays(track)
            current_car.check_collision(track)
            
            # Sadece yol takibi bittiyse ve yanmıyorsa AI kararlarını kullan
            if not current_car.following_path and not current_car.is_burning:
                output = current_net.activate(current_car.distances)
                steering = output[0] * 2 - 1
                steering = max(min(steering, 0.5), -0.5)
                current_car.rotate(steering * 3)
            
            # Fitness artır (yanma durumunda artırma)
            if not current_car.is_burning:
                current_genome.fitness += 0.1
            
            # Tur tamamlama kontrolü
            if current_car.check_lap_completion(track):
                current_car.completed_lap = True
                if current_car.lap_count >= 2:
                    current_car.image.fill((255, 0, 0))
                    
                    finish_time = (pygame.time.get_ticks() - current_car.start_time) / 1000
                    if best_time is None or finish_time < best_time:
                        best_time = finish_time
                    
                    success_box = pygame.Surface((400, 200))
                    success_box.set_alpha(230)
                    success_box.fill((0, 0, 0))
                    WIN.blit(success_box, (WIDTH//2 - 200, HEIGHT//2 - 100))
                    
                    success_text = BIG_FONT.render(f"Başarılı!", True, (0, 255, 0))
                    attempt_text = FONT.render(f"Deneme: {attempt_number}", True, (255, 255, 255))
                    time_text = FONT.render(f"Süre: {finish_time:.2f} sn", True, (255, 255, 255))
                    
                    WIN.blit(success_text, (WIDTH//2 - 100, HEIGHT//2 - 80))
                    WIN.blit(attempt_text, (WIDTH//2 - 80, HEIGHT//2 - 20))
                    WIN.blit(time_text, (WIDTH//2 - 80, HEIGHT//2 + 20))
                    
                    pygame.display.update()
                    pygame.time.wait(2000)
                    current_car.alive = False
            
            current_car.draw(WIN)
            current_car.draw_rays(WIN)
            draw_stats(current_car, attempt_number, best_time, total_time)
        
        pygame.display.update()
        clock.tick(60)

def run(config_file):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )

    population = neat.Population(config)

    # Gösterge çıktısı
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    population.run(eval_genomes, 500)  # 500 nesil eğit

if __name__ == "__main__":
    run(config_path)
