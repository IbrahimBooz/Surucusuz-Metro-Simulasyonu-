# collections - Veri yapıları için yardımcı kütüphane
# Deque: FIFO (First In First Out) yapısında çalışan ve kuyruğa ekleme/çıkarma işlemlerini hızlı bir şekilde yapmamıza olanak tanır.
from collections import deque, defaultdict

# heapq - Öncelik sıralı kuyruklar için kullanılan kütüphane
# Bu kütüphane, en küçük öğeyi hızlıca almak için kullanılacak. A* algoritmasında toplam süreyi yöneten öncelik sıralı kuyruk için kullanılacaktır.
import heapq

# typing - Tür ipuçları sağlamak için kullanılır. Bu, özellikle fonksiyonların parametre ve dönüş türlerini belirtmek için faydalıdır.
from typing import List, Dict, Tuple

import networkx as nx
import matplotlib.pyplot as plt

# İstasyon sınıfı (Her bir istasyonun bilgilerini tutar)
class Istasyon:
    def __init__(self, kod: str, ad: str, hat: str):
        self.kod = kod  # İstasyon kodu (örneğin: AŞTİ, Kızılay)
        self.ad = ad  # İstasyon adı (örneğin: AŞTİ İstasyonu)
        self.hat = hat  # İstasyonun ait olduğu hat (örneğin: M1, M2)
    
    def __lt__(self, other):
        # A* algoritması için karşılaştırma fonksiyonu
        return self.kod < other.kod  # İstasyon kodu üzerinden sıralama yapıyoruz

    
    def __eq__(self, other):
        # 'Istasyon' nesnelerini eşitlik açısından karşılaştırıyoruz
        return self.kod == other.kod

    def __repr__(self):
        # Görselleştirmede istasyon adı görünsün
        return self.ad  # Adı kullanıyoruz

# Metro Ağı sınıfı (Ağı modellemek için kullanılır)
class MetroAgi:
    def __init__(self):
        # Istasyonları saklamak için bir sözlük oluşturuyoruz
        # defaultdict kullanarak, yeni istasyon eklerken hata almıyoruz
        self.istasyonlar = defaultdict(Istasyon)  # İstasyonları tutar
        # Baglantıları saklamak için bir sözlük kullanıyoruz
        # Her istasyon için komşularını tutar
        self.baglanti = defaultdict(list)  # Bağlantıları tutar
        self.G = nx.Graph()  # NetworkX graph

    # İstasyon ekleme fonksiyonu
    def istasyon_ekle(self, kod: str, ad: str, hat: str):
        # Yeni bir istasyon eklerken, istasyonun adı ve hattı belirlenir.
        self.istasyonlar[kod] = Istasyon(kod, ad, hat)
        self.G.add_node(kod, label=ad)

    # Bağlantı ekleme fonksiyonu
    def baglanti_ekle(self, kod1: str, kod2: str, sure: int):
        # İki istasyon arasındaki bağlantıyı eklerken süreyi de ekliyoruz
        # İstasyonlar arasındaki bağlanma sürelerini burada tutuyoruz
        self.baglanti[kod1].append((self.istasyonlar[kod2], sure)) # Bağlantı: Komşu istasyon ve süre
        self.baglanti[kod2].append((self.istasyonlar[kod1], sure)) # Ters yön için de aynı işlemi yapıyoruz
        self.G.add_edge(kod1, kod2, weight=sure)

    # BFS algoritmasıyla en az aktarmalı rotayı bulma
    def en_az_aktarma_bul(self, baslangic: str, hedef: str) -> List[Istasyon]:
        """
        Bu fonksiyon, başlangıç istasyonundan hedef istasyonuna kadar olan
        en az aktarmalı rotayı BFS algoritması ile bulur.
        """
        kuyruk = deque([(self.istasyonlar[baslangic], [self.istasyonlar[baslangic]])])
        ziyaret_edilen = set()

        while kuyruk:
            mevcut, yol = kuyruk.popleft()
            if mevcut.kod == hedef:
                return yol
            if mevcut.kod not in ziyaret_edilen:
                ziyaret_edilen.add(mevcut.kod)
                for komsu, _ in self.baglanti[mevcut.kod]:
                    if komsu.kod not in ziyaret_edilen:
                        kuyruk.append((komsu, yol + [komsu]))

    # A* algoritmasıyla en hızlı rotayı bulma
    def en_hizli_rota_bul(self, baslangic: str, hedef: str) -> Tuple[List[Istasyon], int]:
        """
        Bu fonksiyon, başlangıç istasyonundan hedef istasyonuna kadar olan
        en hızlı rotayı A* algoritması ile bulur.
        """
        pq = []
        heapq.heappush(pq, (0, self.istasyonlar[baslangic], [self.istasyonlar[baslangic]]))
        ziyaret_edilen = set()

        while pq:
            sure, mevcut, yol = heapq.heappop(pq)
            if mevcut.kod == hedef:
                return yol, sure
            if mevcut.kod not in ziyaret_edilen:
                ziyaret_edilen.add(mevcut.kod)
                for komsu, baglanti_suresi in self.baglanti[mevcut.kod]:
                    if komsu.kod not in ziyaret_edilen:
                        toplam_sure = sure + baglanti_suresi
                        heapq.heappush(pq, (toplam_sure, komsu, yol + [komsu]))

        return None

      # Metro ağını ve rotayı çizme
    def plot_agi(self, rota=None):
        """
        Metro ağını ve verilen rotayı görselleştirmek için plt kullanıyoruz
        """
        pos = nx.spring_layout(self.G)  # Graph layout
        plt.figure(figsize=(12, 8))
        
        # Tüm bağlantıları çizme
        nx.draw(self.G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", edge_color="gray", labels=nx.get_node_attributes(self.G, 'label'), arrows=True)
        
        if rota:
            # Rota üzerindeki istasyonları vurgulama
            rota_kodlari = [i.kod for i in rota]
            edges_in_route = [(rota_kodlari[i], rota_kodlari[i + 1]) for i in range(len(rota_kodlari) - 1)]
            nx.draw_networkx_edges(self.G, pos, edgelist=edges_in_route, edge_color="red", width=3)
        
        plt.title("Metro Ağı Görselleştirmesi")
        plt.show()
# Bağlantı eklerken yön belirleyin
    def baglanti_ekle(self, kod1: str, kod2: str, sure: int):
     self.baglanti[kod1].append((self.istasyonlar[kod2], sure))
     self.baglanti[kod2].append((self.istasyonlar[kod1], sure))
     self.G.add_edge(kod1, kod2, weight=sure)  # Burada yönlü ekliyoruz

# Test Senaryoları
def test_metro_agi():
    """
    Metro ağını test eden ve bağlantıların bulunduğu fonksiyon.
    """
    metro = MetroAgi()

      # İstasyonlar ekleme
    metro.istasyon_ekle("K1", "Kızılay", "Kırmızı Hat")
    metro.istasyon_ekle("K2", "Ulus", "Kırmızı Hat")
    metro.istasyon_ekle("K3", "Demetevler", "Kırmızı Hat")
    metro.istasyon_ekle("K4", "OSB", "Kırmızı Hat")

    metro.istasyon_ekle("M1", "AŞTİ", "Mavi Hat")
    metro.istasyon_ekle("M2", "Anıttepe", "Mavi Hat")
    metro.istasyon_ekle("M3", "Sıhhiye", "Mavi Hat")
    metro.istasyon_ekle("M4", "Gar", "Mavi Hat")

    metro.istasyon_ekle("T1", "Batıkent", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Dikimevi", "Turuncu Hat")
    metro.istasyon_ekle("T3", "Dikmen", "Turuncu Hat")
    metro.istasyon_ekle("T4", "Keçiören", "Turuncu Hat")

    metro.istasyon_ekle("B1", "Başkent", "Beyaz Hat")
    metro.istasyon_ekle("B2", "Kocatepe", "Beyaz Hat")

    # Bağlantılar ekleme
    metro.baglanti_ekle("K1", "K2", 4)
    metro.baglanti_ekle("K2", "K3", 6)
    metro.baglanti_ekle("K3", "K4", 8)

    metro.baglanti_ekle("M1", "M2", 5)
    metro.baglanti_ekle("M2", "M3", 3)
    metro.baglanti_ekle("M3", "M4", 4)

    metro.baglanti_ekle("T1", "T2", 7)
    metro.baglanti_ekle("T2", "T3", 9)
    metro.baglanti_ekle("T3", "T4", 5)

    metro.baglanti_ekle("K1", "M2", 2)
    metro.baglanti_ekle("K3", "T2", 3)
    metro.baglanti_ekle("M4", "T3", 2)
    metro.baglanti_ekle("K1", "M4", 4)

    metro.baglanti_ekle("T1", "B2", 3)
    metro.baglanti_ekle("B1", "M1", 10)
    metro.baglanti_ekle("B2", "T4", 2)

    # Test Senaryoları 
    print("\n=== Test Senaryoları ===")

    print("\n1. AŞTİ'den OSB'ye:")
    rota = metro.en_az_aktarma_bul("M1", "K4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("M1", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n2. Batıkent'ten Keçiören'e:")
    rota = metro.en_az_aktarma_bul("T1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("T1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n3. Keçiören'den AŞTİ'ye:")
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n4. Kocatepe'den Keçiören'e:")
    rota = metro.en_az_aktarma_bul("B2", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("B2", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n5. Başkent'ten Batıkent'e:")
    rota = metro.en_az_aktarma_bul("B1", "T1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))

    sonuc = metro.en_hizli_rota_bul("B1", "T1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n6. Batıkent'ten Kocatepe'ye (Bağlantı Yok):")
    rota = metro.en_az_aktarma_bul("T1", "B2")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    else:
        print("Bağlantı bulunamadı.")

    sonuc = metro.en_hizli_rota_bul("T1", "B2")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

        metro.plot_agi(rota)  # Ağı Görüntülemek için
    else:
        print("Bağlantı bulunamadı.")

    print("\n7. Keçiören'den AŞTİ'ye döngüsel hatla (aynı hat üzerinden giderek):")
    rota = metro.en_az_aktarma_bul("T4", "M1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
        metro.plot_agi(rota)  # Ağı Görüntülemek için

    sonuc = metro.en_hizli_rota_bul("T4", "M1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        metro.plot_agi(rota)  # Ağı Görüntülemek için

    print("\n8. Başkent'ten Gar'a (Çoklu hattı kullanarak):")
    rota = metro.en_az_aktarma_bul("B1", "M4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
        metro.plot_agi(rota)  # Ağı Görüntülemek için

    sonuc = metro.en_hizli_rota_bul("B1", "M4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        metro.plot_agi(rota)  # Ağı Görüntülemek için

# Testi çalıştırma 
test_metro_agi()

