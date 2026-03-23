# 🚀 Ürün Gereksinim Belgesi (PRD): Sektör Rehberim

**Proje Sahibi:** Zeynep Feyza  
**Rol:** Kıdemli Full-Stack Developer Rehberliğinde Mini Web App  
**Sürüm:** 1.0.0  

---

## 1. Ürün Vizyonu (Vision)
İş hayatına yeni adım atan profesyonellerin, şirket kültürleri ve mülakat süreçleri hakkında **anonim, şeffaf ve etik** bilgi alabileceği bir platform oluşturmak. Temel amaç, mülakat öncesi adayları bilinçlendirmek ve bu bilgileri **QR kod** teknolojisi ile hızlıca paylaşılabilir kılmaktır.

---

## 2. Kullanıcı Hikayeleri (User Stories)
| Kim? | Ne Yapmak İstiyor? | Neden? |
| :--- | :--- | :--- |
| **Yeni Mezun** | Şirket mülakat sorularını okumak istiyor. | Hazırlıklı gitmek ve heyecanını yenmek için. |
| **Çalışan** | Anonim olarak deneyim paylaşmak istiyor. | Şirket içi kültürü dışarıya dürüstçe aktarmak için. |
| **Kullanıcı** | Bir şirket profilini QR kod olarak üretmek istiyor. | Arkadaşlarıyla veya topluluklarda hızlıca paylaşmak için. |

---

## 3. Fonksiyonel Gereksinimler

### 3.1. Anonim Paylaşım Modülü
* Kullanıcılar gerçek kimliklerini belirtmeden yorum yapabilmelidir.
* Her yoruma otomatik olarak "Mersinli Mühendis" veya "Junior Dev" gibi rastgele/seçilebilir anonim takma adlar atanmalıdır.
* **Puanlama:** Şirketler; mülakat zorluğu, çalışma dengesi ve ofis imkanları üzerinden 1-5 arası puanlanmalıdır.

### 3.2. Mülakat Deneyim Havuzu
* Kullanıcılar girdikleri mülakatlarda kendilerine sorulan teknik veya IK sorularını listeleyebilmelidir.
* Bu sorular "Teknik", "Davranışsal" ve "Genel" olarak kategorize edilmelidir.

### 3.3. QR Kod Entegrasyonu
* Her şirket sayfası veya spesifik mülakat deneyimi için bir **"QR Oluştur"** butonu bulunmalıdır.
* Üretilen QR kod, mobil cihazlar tarafından okutulduğunda doğrudan ilgili sayfayı açmalıdır.

### 3.4. Etik ve Denetim (Moderasyon)
* **Küfür Filtresi:** Hakaret içeren yorumlar sistem tarafından otomatik reddedilmelidir.
* **Raporlama:** Topluluk kurallarına uymayan içerikler "Şikayet Et" butonu ile işaretlenebilmelidir.

---

## 4. Teknik Teknoloji Yığını (Tech Stack)

* **Frontend:** React.js (Hızlı arayüz ve geniş kütüphane desteği).
* **Backend & Veritabanı:** Firebase Firestore (Gerçek zamanlı veri akışı ve kolay kurulum).
* **QR Kütüphanesi:** `qrcode.react` (JavaScript tarafında anlık QR üretimi için).
* **Barındırma (Hosting):** Vercel veya Netlify (Ücretsiz ve hızlı canlıya alma).

---

## 5. Başarı Kriterleri (MVP)
- [ ] Bir kullanıcı anonim olarak şirket yorumu ekleyebiliyor mu?
- [ ] Şirketlerin ortalama puanı doğru hesaplanıyor mu?
- [ ] Sayfaya özel QR kod hatasız üretiliyor mu?
- [ ] Uygulama mobil tarayıcılarda düzgün görüntüleniyor mu?

---

## 6. Güvenlik Notu
* Kullanıcıların gerçek IP adresleri veya e-posta adresleri hiçbir şekilde yorumlarla ilişkilendirilmemeli ve veritabanında açıkça saklanmamalıdır.