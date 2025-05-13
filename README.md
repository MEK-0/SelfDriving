# Self Driving Car - NEAT ile Yapay Zeka Destekli Otonom Araç Simülasyonu

## Proje Hakkında
Bu proje, NEAT (NeuroEvolution of Augmenting Topologies) algoritması ile eğitilen yapay zeka destekli bir otonom araç simülasyonudur. Araçlar, bir pist üzerinde sensör verilerini kullanarak kendi başlarına sürüş yapmayı öğrenirler. Proje, Python ve Pygame kütüphanesi ile geliştirilmiştir ve çoklu araç (multi-agent) desteği ile evrimsel öğrenme sürecini hızlandırır.

## İçindekiler
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Kod Yapısı](#kod-yapısı)
- [NEAT Konfigürasyonu](#neat-konfigürasyonu)
- [Sensör Sistemi](#sensör-sistemi)
- [Fitness Fonksiyonu](#fitness-fonksiyonu)
- [Geliştirme ve İpuçları](#geliştirme-ve-ipuçları)
- [Kaynaklar](#kaynaklar)

---

## Kurulum

1. **Python 3.8+** yüklü olmalıdır.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install pygame neat-python
   ```
3. Proje dosyalarını aynı klasöre yerleştirin:
   - `main.py` veya `main_multi.py`
   - `car.py`
   - `track.png` (pist görseli)
   - `red_car.png` (araç görseli)
   - `neat_config.txt` (NEAT ayar dosyası)

> **Not:** `main.py` tek araç, `main_multi.py` ise çoklu araç simülasyonu başlatır.

---

## Kullanım

### Tekli Araç Simülasyonu
```bash
python main.py
```

### Çoklu Araç Simülasyonu
```bash
python main_multi.py
```

- **Tam ekran** başlar, çıkmak için `ESC` tuşuna basabilirsiniz.
- Simülasyon sırasında araçlar pistte otomatik olarak sürüş yapar ve öğrenir.

---

## Kod Yapısı

### 1. `main.py` / `main_multi.py`
- Simülasyonun ana döngüsünü ve NEAT ile evrimsel öğrenmeyi yönetir.
- `main_multi.py` çoklu araç desteği ile her nesilde birden fazla aracı aynı anda eğitir.
- Ekranda deneme sayısı, aktif araç sayısı, toplam süre ve en iyi süre gibi istatistikler gösterilir.

### 2. `car.py`
- `Car` sınıfı, aracın fiziksel özelliklerini, hareketini, sensörlerini ve pistteki durumunu yönetir.
- Araç görseli olarak `red_car.png` kullanılır ve boyutu 60x45 piksel olarak ayarlanmıştır.
- Sensörler (ray casting) ile pistin sınırlarını algılar.
- Araç, kendi etrafında dönmeye başlarsa veya pist dışına çıkarsa "yanar" ve simülasyondan çıkar.

### 3. `neat_config.txt`
- NEAT algoritmasının tüm parametrelerini içerir.
- Giriş/çıkış sayısı, aktivasyon fonksiyonu, popülasyon büyüklüğü, mutasyon oranları gibi ayarlar burada yapılır.

### 4. `track.png`
- Pist haritası. Siyah alanlar pist, beyaz alanlar dış alan olarak kabul edilir.

### 5. `red_car.png`
- Araç görseli. Şeffaf arka planlı, tercihen üstten görünüşlü bir araba resmi olmalıdır.

---

## NEAT Konfigürasyonu

`neat_config.txt` dosyasında önemli parametreler:
- **num_inputs = 5**: Araçta 5 sensör (ışın) bulunur.
- **num_outputs = 1**: Tek çıkış (direksiyon açısı).
- **feed_forward = True**: Ağ ileri beslemelidir.
- **activation_default = tanh**: Aktivasyon fonksiyonu.
- **pop_size = 10/50**: Popülasyon büyüklüğü (daha hızlı eğitim için düşük tutulabilir).
- **mutation ve crossover oranları**: Ağın evrimleşme hızını ve çeşitliliğini belirler.

> **Not:** NEAT parametreleri ile oynamak, öğrenme başarısını ve hızını ciddi şekilde etkiler.

---

## Sensör Sistemi

- Araçta 5 adet sensör (ışın) bulunur: `[-60, -30, 0, 30, 60]` derece.
- Her sensör, pistin sınırına olan mesafeyi normalleştirilmiş olarak ölçer.
- Sensör verileri, NEAT ağına giriş olarak verilir.

---

## Fitness Fonksiyonu

- Araç pistte ne kadar uzun süre hayatta kalırsa fitness puanı artar.
- Tur tamamlayan araçlar ekstra fitness puanı alır.
- Başlangıç düz mesafesini geçen araçlara küçük ödüller verilir.
- Araç pist dışına çıkarsa veya kendi etrafında dönmeye başlarsa "yanar" ve fitness artışı durur.

---

## Geliştirme ve İpuçları

- **Sensör Sayısı ve Açısı:** Daha fazla/daha az sensör veya farklı açılar ile denemeler yapabilirsiniz.
- **Fitness Fonksiyonu:** Daha karmaşık ödül/ceza sistemleri ile daha iyi sonuçlar alınabilir.
- **NEAT Parametreleri:** Popülasyon büyüklüğü, mutasyon oranları, aktivasyon fonksiyonu gibi ayarlarla oynayarak farklı öğrenme dinamikleri elde edebilirsiniz.
- **Pist Tasarımı:** Farklı pist görselleri ile aracı farklı zorluklarda test edebilirsiniz.
- **Görsel ve Performans:** Araç görselini ve pist çözünürlüğünü değiştirerek simülasyonun görselliğini ve hızını etkileyebilirsiniz.
- **Çoklu Araç:** `main_multi.py` ile aynı anda birden fazla aracı eğitmek, evrimsel süreci hızlandırır.

---

## Kaynaklar
- [NEAT-Python Belgeleri](https://neat-python.readthedocs.io/en/latest/)
- [Pygame Belgeleri](https://www.pygame.org/docs/)
- [NEAT Algoritması (Wikipedia)](https://en.wikipedia.org/wiki/Neuroevolution_of_augmenting_topologies)

---

Her türlü soru ve katkı için iletişime geçebilirsiniz! 

https://www.linkedin.com/in/mahmutesatkolay/

Proje yapım aşamasındadır tam bitmemiştir kodlar arası uyumsuzluk olabilir.
