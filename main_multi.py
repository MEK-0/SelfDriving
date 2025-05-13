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
pygame.display.set_caption("AI Self Driving Car - Multi Car Simulation")

# Font ayarları
FONT = pygame.font.SysFont('Arial', 40)
BIG_FONT = pygame.font.SysFont('Arial', 60)

# Harita dosyası
TRACK_PATH = "track.png"

def draw_stats(cars, attempt_number, best_time=None, total_time=0):
    # Sayaç kutusu
    counter_box = pygame.Surface((300, 250))
    counter_box.set_alpha(200)
    counter_box.fill((0, 0, 0))
    WIN.blit(counter_box, (10, 10))
    
    # Aktif araç sayısı
    active_cars = sum(1 for car in cars if car.alive)
    
    # İstatistikleri ekrana yazdır
    stats_text = [
        f"Deneme: {attempt_number}",
        f"Aktif Araç: {active_cars}",
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
    best_time = None
    
    # Genel zaman sayacı için
    program_start_time = pygame.time.get_ticks()
    
    # Araçları ve ağları tutacak listeler
    cars = []
    nets = []
    ge = []
    
    # Başlangıç pozisyonları
    start_positions = [
        (150, 150),  # Merkez
        (200, 150),  # Sağ
        (100, 150),  # Sol
        (150, 200),  # Alt
        (150, 100),  # Üst
    ]
    
    # Her genom için bir araç oluştur
    for i, (genome_id, genome) in enumerate(genomes):
        start_x, start_y = start_positions[i % len(start_positions)]
        car = Car(start_x, start_y)
        cars.append(car)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        ge.append(genome)
    
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
        
        # Tüm araçları güncelle
        for i, car in enumerate(cars):
            if car.alive:
                car.move()
                car.cast_rays(track)
                car.check_collision(track)
                
                # Sadece yol takibi bittiyse ve yanmıyorsa AI kararlarını kullan
                if not car.following_path and not car.is_burning:
                    output = nets[i].activate(car.distances)
                    steering = output[0] * 2 - 1
                    steering = max(min(steering, 0.3), -0.3)  # Dönüş aralığını daralt
                    car.rotate(steering * 2)  # Dönüş hızını azalt
                
                # Fitness artır
                if not car.is_burning:
                    ge[i].fitness += 0.1
                    if car.lap_count > 0:
                        ge[i].fitness += 0.5
                
                # Tur tamamlama kontrolü
                if car.check_lap_completion(track):
                    car.completed_lap = True
                    if car.lap_count >= 2:
                        car.image.fill((255, 0, 0))
                        finish_time = (pygame.time.get_ticks() - car.start_time) / 1000
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
                        car.alive = False
                
                car.draw(WIN)
                car.draw_rays(WIN)
        
        # Tüm araçlar öldüyse yeni nesil başlat
        if not any(car.alive for car in cars):
            attempt_number += 1
            for i, (genome_id, genome) in enumerate(genomes):
                start_x, start_y = start_positions[i % len(start_positions)]
                car = Car(start_x, start_y)
                cars[i] = car
                genome.fitness = 0
        
        draw_stats(cars, attempt_number, best_time, total_time)
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
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    population.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat_config.txt")
    run(config_path)